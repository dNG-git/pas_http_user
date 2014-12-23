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

from dNG.pas.data.settings import Settings
from dNG.pas.data.text.email_renderer import EMailRenderer
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.text.link import Link

class VerificationEMailRenderer(EMailRenderer):
#
	"""
"VerificationEMailRenderer" creates the verification e-mail.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=arguments-differ

	def __init__(self, l10n = None):
	#
		"""
Constructor __init__(VerificationEMailRenderer)

:param l10n: L10n instance

:since: v0.1.00
		"""

		EMailRenderer.__init__(self, l10n)

		self.verification_details = None
		"""
Details text about what will be verified with the task link
		"""

		Settings.read_file("{0}/settings/pas_http.json".format(Settings.get("path_data")))
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

		vid_url = "{0}tasks.d/{1}".format(Link.get_preferred().build_url(Link.TYPE_ABSOLUTE_URL | Link.TYPE_BASE_PATH),
		                                  Link.encode_query_value(vid)
		                                 )

		content = ("" if (self.verification_details is None) else self.verification_details)

		content += """

{0}: {1}
{2}: {3}

{4}
{5}
{6}
		""".format(self.l10n.get("pas_core_username"),
		           user_profile_data['name'],
		           self.l10n.get("pas_http_user_verification_timeout_days"),
		           vid_timeout_days,
		           self.l10n.get("pas_http_user_verification_link_required"),
		           vid_url,
		           self.l10n.get("pas_email_url_notice")
		          )

		return EMailRenderer.render(self, content, self.REASON_FOR_VALIDATION)
	#
#

##j## EOF