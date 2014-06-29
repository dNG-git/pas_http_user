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

import re

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.settings import Settings
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.session.implementation import Implementation as SessionImplementation
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.tmd5 import Tmd5
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.notification_store import NotificationStore
from dNG.pas.data.xhtml.form.processor import Processor as FormProcessor
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hook import Hook
from .module import Module

class Status(Module):
#
	"""
Service for "m=user;s=status"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def execute_login(self, is_save_mode = False):
	#
		"""
Action for "login"

:since: v0.1.00
		"""

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = ""

		if (source_iline == ""): source_iline = "m=user;a=services;lang=__lang__;theme=__theme__"
		else: source = Link.encode_query_value(source_iline)

		target = ""

		if (target_iline == ""):
		#
			if (Settings.is_defined("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))
			elif (Settings.is_defined("pas_http_user_login_default_target")): target_iline = Settings.get("pas_http_user_login_default_target")
			else: target_iline = source_iline
		#
		else: target = Link.encode_query_value(target_iline)

		Settings.read_file("{0}/settings/pas_user_profile.json".format(Settings.get("path_data")))
		L10n.init("pas_http_user")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               image = "mini_default_back",
		               priority = 2
		              )

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)
		if (is_save_mode): form.set_input_available()

		is_cookie_supported = Settings.get("pas_http_site_cookies_supported", True)

		form.add_text({ "name": "uusername",
		                "title": L10n.get("pas_core_username"),
		                "required": True,
		                "size": "s",
		                "min": int(Settings.get("pas_http_core_username_min", 3)),
		                "max": 100,
		                "helper_text": L10n.get("pas_http_user_helper_username")
		              })

		form.add_password({ "name": "upassword",
		                    "title": L10n.get("pas_http_user_password"),
		                    "required": True,
		                    "min": int(Settings.get("pas_http_user_password_min", 6))
		                  },
		                  FormProcessor.PASSWORD_CLEARTEXT
		                 )

		if (is_cookie_supported):
		#
			form_field = { "name": "ucookie",
			               "title": L10n.get("pas_http_user_login_use_cookie"),
			               "required": True,
			               "choices": [ { "value": "1", "title": L10n.get("core_yes") },
			                            { "value": "0", "title": L10n.get("core_no") }
			                          ]
			             }

			if (not is_save_mode): form_field['content'] = "1"
			form.add_radio(form_field)
		#

		if (is_save_mode and form.check()):
		#
			username = InputFilter.filter_control_chars(form.get_value("uusername"))
			password = Tmd5.password_hash(form.get_value("upassword"), Settings.get("pas_user_profile_password_salt"), username)

			user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
			if (user_profile_class == None): raise TranslatableError("core_unknown_error")

			try: user_profile = user_profile_class.load_username(username)
			except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_user_username_or_password_invalid", 403, _exception = handled_exception)

			user_profile_data = user_profile.get_data_attributes("id", "type_ex", "password", "banned", "deleted", "locked", "lang", "theme")

			if (user_profile_data['banned'] != 0): raise TranslatableError("pas_http_user_profile_banned", 403)
			if (user_profile_data['locked'] != 0): raise TranslatableError("pas_http_user_profile_locked", 403)
			if (user_profile_data['type_ex'] != "" or password != user_profile_data['password'] or user_profile_data['deleted'] != 0): raise TranslatableError("pas_http_user_username_or_password_invalid", 403)

			session = SessionImplementation.get_class().load()
			session.set("session.user_id", user_profile_data['id'])
			session.set_cookie(is_cookie_supported and form.get_value("ucookie") == "1")
			session.save()

			self.request.set_session(session)

			target_iline = target_iline.replace("__lang__", user_profile_data['lang'])
			target_iline = target_iline.replace("__theme__", user_profile_data['theme'])
			target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

			NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_user_done_login"))

			Link.clear_store("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			alternative_login_links = Hook.call("dNG.pas.http.UserProfile.getAlternativeLoginLinks")

			content = { "title": L10n.get("pas_http_user_title_login"),
			            "alternative_login_links": (alternative_login_links if (type(alternative_login_links) == list) else [ ])
			          }

			content['form'] = { "object": form,
			                    "url_parameters": { "__request__": True, "a": "login-save", "dsd": { "source": source, "target": target } },
			                    "button_title": "pas_core_login"
			                  }

			self.response.init()
			self.response.set_title(L10n.get("pas_http_user_title_login"))
			self.response.add_oset_content("user.status.login", content)
		#
	#

	def execute_login_save(self):
	#
		"""
Action for "login-safe"

:since: v0.1.00
		"""

		self.execute_login(True)
	#

	def execute_logout(self):
	#
		"""
Action for "logout"

:since: v0.1.00
		"""

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		if (target_iline == ""):
		#
			if (Settings.is_defined("pas_http_user_logout_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_logout_default_target_lang_{0}".format(self.request.get_lang()))
			elif (Settings.is_defined("pas_http_user_logout_default_target")): target_iline = Settings.get("pas_http_user_logout_default_target")
			else: target_iline = source_iline
		#

		L10n.init("pas_http_user")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               image = "mini_default_back",
		               priority = 2
		              )

		session = SessionImplementation.get_class().load(session_create = False)

		if (session != None):
		#
			session.delete()
			self.request.set_session(None)
		#

		target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

		content = { "task": L10n.get("pas_core_logout"),
		            "message": L10n.get("pas_http_user_done_logout"),
		            "continue_url": Link().build_url(Link.TYPE_RELATIVE, { "__query__": target_iline })
		          }

		self.response.init()
		self.response.set_title(L10n.get("pas_http_user_title_logout"))
		self.response.add_oset_content("core.done", content)
	#
#

##j## EOF