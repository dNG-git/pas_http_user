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

class ChangesConfirmed(AbstractTask):
#
	"""
The "ChangesConfirmed" task is executed after the user clicked on the
link of the confirmation e-mail.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, username, values_changed, vid):
	#
		"""
Constructor __init__(ChangesConfirmed)

:param username: Username to unlock
:param values_changed: Dict of values changed
:param vid: Verification ID

:since: v0.1.00
		"""

		AbstractTask.__init__(self)

		self.username = username
		"""
Username with confirmed changes
		"""
		self.values_changed = values_changed
		"""
Dict of values changed
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

		original_user_profile_data = user_profile.get_data_attributes(*self.values_changed.keys())

		user_profile.set_data_attributes(**self.values_changed)
		user_profile.save()

		DatabaseTasksProxy.get_instance().add("dNG.pas.user.Profile.onEdited.{0}".format(self.username),
		                                      "dNG.pas.user.Profile.onEdited",
		                                      1,
		                                      user_profile_id = user_profile.get_id(),
		                                      user_profile_data_changed = self.values_changed,
		                                      original_user_profile_data = original_user_profile_data
		                                     )

		task_data = DatabaseTasks.get_instance().get(self.vid)

		if (task_data != None and "_task" in task_data):
		#
			task_data['_task'].set_status_completed()
			task_data['_task'].save()
		#

		user_profile_data = user_profile.get_data_attributes("id", "name", "lang")

		L10n.init("core", user_profile_data['lang'])
		L10n.init("pas_core", user_profile_data['lang'])
		L10n.init("pas_http_user", user_profile_data['lang'])

		l10n = L10n.get_instance(user_profile_data['lang'])

		_return = PredefinedHttpRequest()
		_return.set_module("output")
		_return.set_service("http")
		_return.set_action("done")

		_return.set_parameter_chained("title", l10n.get("pas_http_user_title_change_profile"))
		_return.set_parameter_chained("message", l10n.get("pas_http_user_done_change_profile"))
		_return.set_parameter_chained("lang", l10n.get_lang())
		_return.set_parameter_chained("target_iline", "m=user;s=profile;lang={0};dsd=upid+{1}".format(user_profile_data['lang'], user_profile_data['id']))

		return _return
	#
#

##j## EOF