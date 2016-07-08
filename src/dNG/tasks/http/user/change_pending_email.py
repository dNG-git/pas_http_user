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

from dNG.data.tasks.database import Database as DatabaseTasks

from .abstract_verification_email import AbstractVerificationEMail

class ChangePendingEMail(AbstractVerificationEMail):
#
	"""
The "ChangePendingEMail" task will send an e-mail to confirm changes.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	EMAIL_RENDERER = "dNG.data.text.user.ChangePendingEMailRenderer"
	"""
E-mail renderer to be used to send the verification
	"""

	def __init__(self, username, recipient, vid, vid_timeout_days):
	#
		"""
Constructor __init__(ChangePendingEMail)

:param username: Username to send the verification e-mail to
:param recipient: Verification e-mail recipient address; None for default
:param vid: Verification ID
:param vid_timeout_days: Days until vID will time out

:since: v0.2.00
		"""

		AbstractVerificationEMail.__init__(self, username, vid, vid_timeout_days)

		self.recipient = recipient
		"""
Verification e-mail recipient
		"""
	#

	def get_email_recipient(self):
	#
		"""
Returns the verification e-mail recipient address.

:return: (str) Verification e-mail recipient; None for default recipient
:since:  v0.2.00
		"""

		return self.recipient
	#

	def get_email_subject(self, l10n):
	#
		"""
Returns the verification e-mail subject.

:param l10n: L10n instance

:return: (str) Verification e-mail subject; None for default subject
:since:  v0.2.00
		"""

		return l10n.get("pas_http_user_title_change_profile")
	#
#

##j## EOF