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

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.tasks.database import Database as DatabaseTasks
from dNG.pas.data.tasks.database_proxy import DatabaseProxy as DatabaseTasksProxy
from dNG.pas.data.text.l10n import L10n
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.tasks.abstract import Abstract as AbstractTask

class RegistrationValidated(AbstractTask):
#
	"""
The "RegistrationValidated" task is executed after the user clicked on the
link of the registration e-mail.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, username, vid):
	#
		"""
Constructor __init__(RegistrationValidated)

:param username: Username validated
:param vid: Verification ID

:since: v0.1.00
		"""

		AbstractTask.__init__(self)

		self.username = username
		"""
Username validated
		"""
		self.vid = vid
		"""
Verification ID
		"""
	#

	def run(self):
	#
		"""
Task execution

:since: v0.1.00
		"""

		user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")

		user_profile = user_profile_class.load_username(self.username)
		user_profile.unlock()
		user_profile.save()

		database_tasks_proxy = DatabaseTasksProxy.get_instance()

		database_tasks_proxy.add("dNG.pas.user.Profile.updateSecID.{0}".format(self.username),
		                         "dNG.pas.user.Profile.updateSecID",
		                         1,
		                         username = self.username
		                        )

		database_tasks_proxy.remove("dNG.pas.user.Profile.delete.{0}".format(self.username))

		task_data = DatabaseTasks.get_instance().get(self.vid)

		if (task_data != None and "_task" in task_data):
		#
			task_data['_task'].set_status_completed()
			task_data['_task'].save()
		#

		user_profile_data = user_profile.get_data_attributes("name", "lang")

		L10n.init("core", user_profile_data['lang'])
		L10n.init("pas_core", user_profile_data['lang'])
		L10n.init("pas_http_user", user_profile_data['lang'])

		l10n = L10n.get_instance(user_profile_data['lang'])

		_return = PredefinedHttpRequest()
		_return.set_module("output")
		_return.set_service("http")
		_return.set_action("done")

		_return.set_parameter_chained("title", l10n.get("pas_http_user_title_registration"))
		_return.set_parameter_chained("message", l10n.get("pas_http_user_done_registration"))
		_return.set_parameter_chained("lang", l10n.get_lang())
		_return.set_parameter_chained("target_iline", "m=user;s=status;a=login;lang={0}".format(user_profile_data['lang']))

		return _return
	#
#

##j## EOF