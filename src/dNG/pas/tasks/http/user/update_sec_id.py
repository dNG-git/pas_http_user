# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;http;user

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasHttpUserVersion)#
#echo(__FILEPATH__)#
"""

import re

from dNG.data.rfc.email.message import Message
from dNG.data.rfc.email.part import Part
from dNG.pas.data.settings import Settings
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.text.tmd5 import Tmd5
from dNG.pas.net.smtp.client import Client as SmtpClient
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.tasks.abstract import Abstract as AbstractTask

class UpdateSecID(AbstractTask):
#
	"""
The "UpdateSecID" task generates a new "Security ID string" for a given user
and notifies him via e-mail.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, username):
	#
		"""
Constructor __init__(UpdateSecID)

:param username: Username to unlock

:since: v0.1.00
		"""

		AbstractTask.__init__(self)

		self.username = username
		"""
Username to send the e-mail to
		"""

		Settings.read_file("{0}/settings/pas_http.json".format(Settings.get("path_data")))
		Settings.read_file("{0}/settings/pas_user_profile.json".format(Settings.get("path_data")))
	#

	def run(self):
	#
		"""
Task execution

:since: v0.1.00
		"""

		user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
		user_profile = user_profile_class.load_username(self.username)

		secid = user_profile_class.generate_secid()
		secid_hashed = Tmd5.password_hash(re.sub("\\W+", "", secid), Settings.get("pas_user_profile_password_salt"), self.username)

		user_profile.set_data_attributes(secid = secid_hashed)
		user_profile.save()

		user_profile_data = user_profile.get_data_attributes("name", "lang", "email")

		L10n.init("core", user_profile_data['lang'])
		L10n.init("pas_core", user_profile_data['lang'])
		L10n.init("pas_http_user", user_profile_data['lang'])

		l10n = L10n.get_instance(user_profile_data['lang'])

		email_renderer = NamedLoader.get_instance("dNG.pas.data.text.user.SecIDUpdatedEMailRenderer", l10n = l10n)
		content = email_renderer.render(user_profile_data, secid)
		subject = l10n.get("pas_http_user_title_sec_id_updated")

		part = Part(Part.TYPE_MESSAGE_BODY, "text/plain", content)

		message = Message()
		message.add_body(part)
		message.set_subject(subject)
		message.set_to(Message.format_address(user_profile_data['name'], user_profile_data['email']))

		smtp_client = SmtpClient()
		smtp_client.set_message(message)
		smtp_client.send()
	#
#

##j## EOF