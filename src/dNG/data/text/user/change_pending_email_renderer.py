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

from .verification_email_renderer import VerificationEMailRenderer

class ChangePendingEMailRenderer(VerificationEMailRenderer):
#
	"""
"ChangePendingEMailRenderer" creates the changes confirmation e-mail.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=arguments-differ

	def __init__(self, l10n = None):
	#
		"""
Constructor __init__(ChangePendingEMailRenderer)

:param l10n: L10n instance

:since: v0.2.00
		"""

		VerificationEMailRenderer.__init__(self, l10n)

		self.verification_details = self.l10n.get("pas_http_user_change_profile_pending_email_message")
	#
#

##j## EOF