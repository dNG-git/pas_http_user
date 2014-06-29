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

from dNG.pas.data.text.email_renderer import EMailRenderer
from dNG.pas.data.text.l10n import L10n

class SecIDUpdatedEMailRenderer(EMailRenderer):
#
	"""
"SecIDUpdatedEMailRenderer" generates an e-mail to send the "Security ID
string".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=signature-differs

	def __init__(self, l10n = None):
	#
		"""
Constructor __init__(SecIDUpdatedEMailRenderer)

:param l10n: L10n instance

:since: v0.1.00
		"""

		EMailRenderer.__init__(self, l10n)

		L10n.init("pas_http_user", self.l10n.get_lang())
	#

	def render(self, user_profile_data, secid):
	#
		"""
Render header, body and footer suitable for e-mail delivery.

:param body: Preformatted e-mail body
:param reason: Reason for automated delivery

:return: (str) Rendered e-mail body
:since:  v0.1.00
		"""

		content = """
{0}
{1}

{2}: {3}

{4}
		""".format(self.l10n.get("pas_http_user_sec_id_updated_email_message"),
		           secid,
		           self.l10n.get("pas_core_username"),
		           user_profile_data['name'],
		           self.l10n.get("pas_http_user_sec_id_updated_email_burn_after_notice")
		          )

		return EMailRenderer.render(self, content, self.REASON_ON_DEMAND)
	#
#

##j## EOF