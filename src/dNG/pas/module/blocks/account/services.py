# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.account.Index
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;http;user_profile

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasHttpUserProfileVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from dNG.pas.data.settings import Settings
from dNG.pas.data.text.l10n import L10n
from .module import Module

class Index(Module):
#
	"""
Service for "m=account"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user_profile
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def execute_index(self, is_safe_mode = False):
	#
		"""
Action for "index"

:since: v0.1.00
		"""

		L10n.init("pas_http_user_profile")

		content = {
			"title": L10n.get("pas_http_user_profile_title_services"),
			"service_list": { "file": "{0}/settings/lists/pas_user_profile.service.json".format(Settings.get("path_data")) }
		}

		self.response.init()
		self.response.set_title(L10n.get("pas_http_user_profile_title_services"))
		self.response.add_oset_content("core.service_list", content)
	#
#

##j## EOF