# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;http;user

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasHttpUserProfileVersion)#
#echo(__FILEPATH__)#
"""

from dNG.data.rfc.email.message import Message
from dNG.data.rfc.email.part import Part
from dNG.pas.data.settings import Settings
from dNG.pas.data.text.l10n import L10n
from dNG.pas.net.smtp.client import Client as SmtpClient
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.tasks.abstract import Abstract as AbstractTask

class RegistrationEMail(AbstractTask):
#
	"""
The "RegistrationEMail" task will send a registration e-mail to the user
profile's address.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, username, vid, vid_timeout_days):
	#
		"""
Constructor __init__(RegistrationEMail)

:param username: Username to send the registration e-mail to
:param vid: Verification ID
:param vid_timeout_days: Days until vID will time out

:since: v0.1.00
		"""

		AbstractTask.__init__(self)

		self.username = username
		"""
Username to send the e-mail to
		"""
		self.vid = vid
		"""
Verification ID
		"""
		self.vid_timeout_days = vid_timeout_days
		"""
Verification ID timeout (as days)
		"""

		Settings.read_file("{0}/settings/pas_http.json".format(Settings.get("path_data")))
	#

	def run(self):
	#
		"""
Hook execution

:since: v0.1.00
		"""

		user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
		user_profile = user_profile_class.load_username(self.username)

		user_profile_data = user_profile.get_data_attributes("name", "lang", "email")

		L10n.init("core", user_profile_data['lang'])
		L10n.init("pas_core", user_profile_data['lang'])
		L10n.init("pas_http_user", user_profile_data['lang'])

		l10n = L10n.get_instance(user_profile_data['lang'])

		email_renderer = NamedLoader.get_instance("dNG.pas.data.text.user.RegistrationEMailRenderer", l10n = l10n)
		content = email_renderer.render(user_profile_data, self.vid, self.vid_timeout_days)
		subject = l10n.get("pas_http_user_title_registration")

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