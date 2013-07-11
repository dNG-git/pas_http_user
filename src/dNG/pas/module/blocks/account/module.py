# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.account.Module
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
from dNG.pas.data.translatable_exception import TranslatableException
from dNG.pas.database.connection import Connection
from dNG.pas.module.blocks.abstract_block import AbstractBlock

class Module(AbstractBlock):
#
	"""
Module for "account"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user_profile
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Module)

:since: v0.1.00
		"""

		AbstractBlock.__init__(self)

		self.database = None
		"""
Database instance
		"""
	#

	def execute(self):
	#
		"""
Execute the requested action.

:since: v0.1.00
		"""

		with self.database: return AbstractBlock.execute(self)
	#

	def init(self, request, response):
	#
		"""
Initialize block from the given request and response.

:param request: Request object
:param response: Response object

:since: v0.1.00
		"""

		AbstractBlock.init(self, request, response)

		Settings.read_file("{0}/settings/pas_user_profile.json".format(Settings.get("path_data")))
		self._init_db()
	#

	def _init_db(self):
	#
		"""
Initializes the database.

:since: v0.1.00
		"""

		try: self.database = Connection.get_instance()
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
		#

		if (self.database == None): raise TranslatableException("core_database_error")
	#
#

##j## EOF