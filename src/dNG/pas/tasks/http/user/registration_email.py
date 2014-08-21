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

from .abstract_verification_email import AbstractVerificationEMail

class RegistrationEMail(AbstractVerificationEMail):
#
	"""
The "RegistrationEMail" task will send a registration e-mail to the user
profile's address.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	EMAIL_RENDERER = "dNG.pas.data.text.user.RegistrationEMailRenderer"
	"""
E-mail renderer to be used to send the verification
	"""

	def get_email_subject(self, l10n):
	#
		"""
Returns the verification e-mail subject.

:param l10n: L10n instance

:return: (str) Verification e-mail subject; None for default subject
:since:  v0.1.00
		"""

		return l10n.get("pas_http_user_title_registration")
	#
#

##j## EOF