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

import re

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.settings import Settings
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.session.implementation import Implementation as Session
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.notification_store import NotificationStore
from dNG.pas.data.xhtml.form.password_field import PasswordField
from dNG.pas.data.xhtml.form.processor import Processor as FormProcessor
from dNG.pas.data.xhtml.form.radio_field import RadioField
from dNG.pas.data.xhtml.form.text_field import TextField
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.module.named_loader import NamedLoader
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
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
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

		source = source_iline
		if (source_iline == ""): source_iline = "m=user;a=services;lang=__lang__;theme=__theme__"

		target = target_iline

		if (target_iline == ""):
		#
			if (Settings.is_defined("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))
			elif (Settings.is_defined("pas_http_user_login_default_target")): target_iline = Settings.get("pas_http_user_login_default_target")
			else: target_iline = source_iline
		#

		L10n.init("pas_http_core_form")
		L10n.init("pas_http_user")

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		is_cookie_supported = Settings.get("pas_http_site_cookies_supported", True)

		if (is_cookie_supported
		    and type(Settings.get("pas_http_user_alternative_login_services_list")) == list
		   ):
		#
			Link.set_store("servicemenu",
			               (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED),
			               L10n.get("pas_http_user_alternative_login_methods_view"),
			               { "__request__": True, "a": "login-alternatives-list", "dsd": { "source": source, "target": target } },
			               icon = "mini-default-option",
			               priority = 3
			              )
		#

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)
		if (is_save_mode): form.set_input_available()

		field = TextField("uusername")
		field.set_title(L10n.get("pas_core_username"))
		field.set_placeholder(L10n.get("pas_http_core_form_case_sensitive_placeholder"))
		field.set_required()
		field.set_limits(int(Settings.get("pas_http_core_username_min", 3)), 100)
		field.set_size(TextField.SIZE_SMALL)
		form.add(field)

		field = PasswordField("upassword")
		field.set_title(L10n.get("pas_http_user_password"))
		field.set_required()
		field.set_limits(int(Settings.get("pas_http_user_password_min", 6)))
		field.set_mode(PasswordField.PASSWORD_CLEARTEXT)
		form.add(field)

		if (is_cookie_supported):
		#
			cookie_choices = [ { "value": "1", "title": L10n.get("core_yes") },
			                   { "value": "0", "title": L10n.get("core_no") }
			                 ]

			field = RadioField("ucookie")
			field.set_title(L10n.get("pas_http_user_login_use_cookie"))
			field.set_value("1")
			field.set_choices(cookie_choices)
			field.set_required()
			form.add(field)
		#

		if (is_save_mode and form.check()):
		#
			username = InputFilter.filter_control_chars(form.get_value("uusername"))
			password = InputFilter.filter_control_chars(form.get_value("upassword"))

			user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
			if (user_profile_class == None): raise TranslatableError("core_unknown_error")

			try: user_profile = user_profile_class.load_username(username)
			except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_user_username_or_password_invalid", 403, _exception = handled_exception)

			user_profile_data = user_profile.get_data_attributes("id", "lang", "theme")

			if (user_profile.is_banned()): raise TranslatableError("pas_http_user_profile_banned", 403)
			if (user_profile.is_locked()): raise TranslatableError("pas_http_user_profile_locked", 403)
			if (user_profile.is_type("ex")): raise TranslatableError("pas_http_user_feature_not_available_for_external_verified_member", 403)

			if ((not user_profile.is_valid())
			    or (not user_profile.is_password_valid(password))
			   ): raise TranslatableError("pas_http_user_username_or_password_invalid", 403)

			session = Session.get_class().load()
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
			content = { "title": L10n.get("pas_http_user_title_login") }

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

		self.execute_login(self.request.get_type() == "POST")
	#

	def execute_login_alternatives_list(self):
	#
		"""
Action for "login-alternatives-list"

:since: v0.1.00
		"""

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = source_iline
		if (source_iline == ""): source_iline = "m=user;s=status;a=login"

		target = target_iline

		if (target_iline == ""):
		#
			if (Settings.is_defined("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))
			elif (Settings.is_defined("pas_http_user_login_default_target")): target_iline = Settings.get("pas_http_user_login_default_target")
			else: target_iline = source_iline
		#

		L10n.init("pas_http_user")

		services_list = Settings.get("pas_http_user_alternative_login_services_list")

		if ((not Settings.get("pas_http_site_cookies_supported", True))
		    or type(services_list) != list
		   ): raise TranslatableError("pas_http_user_alternative_login_methods_disabled", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		extended_services_list = [ ]

		for service in services_list:
		#
			if ("id" in service and "parameters" in service):
			#
				extended_service = service.copy()

				extended_service['type'] = Link.TYPE_RELATIVE
				if ("dsd" not in extended_service['parameters']): extended_service['parameters']['dsd'] = { }
				extended_service['parameters']['dsd']['usid'] = service['id']
				extended_service['parameters']['dsd']['source'] = source
				extended_service['parameters']['dsd']['target'] = target

				extended_services_list.append(extended_service)
			#
		#

		content = { "title": L10n.get("pas_http_user_alternative_login_services"),
		            "service_list": { "entries": extended_services_list }
		          }

		self.response.init()
		self.response.set_title(L10n.get("pas_http_user_alternative_login_services"))
		self.response.add_oset_content("core.service_list", content)
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

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		session = Session.get_class().load(session_create = False)

		if (session != None):
		#
			session.delete()
			self.request.set_session(None)
		#

		Link.clear_store("servicemenu")

		target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

		redirect_request = PredefinedHttpRequest()
		redirect_request.set_module("output")
		redirect_request.set_service("http")
		redirect_request.set_action("done")

		redirect_request.set_parameter_chained("title", L10n.get("pas_http_user_logout"))
		redirect_request.set_parameter_chained("message", L10n.get("pas_http_user_done_logout"))
		redirect_request.set_parameter_chained("target_iline", target_iline)

		self.request.redirect(redirect_request)
	#
#

##j## EOF