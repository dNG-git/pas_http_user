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

from dNG.pas.data.settings import Settings
from dNG.pas.data.text.email_renderer import EMailRenderer
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.text.link import Link

class RegistrationEMailRenderer(EMailRenderer):
#
	"""
"RegistrationEMailRenderer" creates the registration e-mail.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=arguments-differ

	def __init__(self, l10n = None):
	#
		"""
Constructor __init__(RegistrationEMailRenderer)

:param l10n: L10n instance

:since: v0.1.00
		"""

		EMailRenderer.__init__(self, l10n)

		Settings.read_file("{0}/settings/pas_http_user.json".format(Settings.get("path_data")))

		L10n.init("pas_http_user", self.l10n.get_lang())
	#

	def render(self, user_profile_data, vid, vid_timeout_days):
	#
		"""
Render header, body and footer suitable for e-mail delivery.

:param body: Preformatted e-mail body
:param reason: Reason for automated delivery

:return: (str) Rendered e-mail body
:since:  v0.1.00
		"""

		vid_url = "{0}tasks.d/{1}".format(Link.get_preferred().build_url(Link.TYPE_ABSOLUTE | Link.TYPE_BASE_PATH),
		                                  Link.encode_query_value(vid)
		                                 )

		welcome_text = Settings.get_lang_associated("pas_http_user_registration_welcome_text",
		                                            self.l10n.get_lang(),
		                                            self.l10n.get("pas_http_user_registration_pending_email_message")
		                                           )

		content = """
{0}

{1}: {2}
{3}: {4}

{5}
{6}
{7}
		""".format(welcome_text,
		           self.l10n.get("pas_core_username"),
		           user_profile_data['name'],
		           self.l10n.get("pas_http_user_registration_verification_timeout_days"),
		           vid_timeout_days,
		           self.l10n.get("pas_http_user_registration_verification_link_required"),
		           vid_url,
		           self.l10n.get("pas_email_url_notice")
		          )

		return EMailRenderer.render(self, content, self.REASON_FOR_VALIDATION)
	#
#

##j## EOF