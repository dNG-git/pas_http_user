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

from dNG.data.settings import Settings
from dNG.data.translatable_exception import TranslatableException
from dNG.database.connection import Connection
from dNG.module.controller.abstract_http import AbstractHttp as AbstractHttpController

class Module(AbstractHttpController):
#
	"""
Module for "user"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Module)

:since: v0.2.00
		"""

		AbstractHttpController.__init__(self)

		Settings.read_file("{0}/settings/pas_http_user.json".format(Settings.get("path_data")))
	#

	def execute(self):
	#
		"""
Execute the requested action.

:since: v0.2.00
		"""

		# pylint: disable=broad-except

		try: database = Connection.get_instance()
		except Exception as handled_exception:
		#
			if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_http_site")
			raise TranslatableException("core_database_error", _exception = handled_exception)
		#

		with database: return AbstractHttpController.execute(self)
	#
#

##j## EOF