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
#echo(pasHttpUserVersion)#
#echo(__FILEPATH__)#
"""

from os import urandom
import re

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.settings import Settings
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.tasks.database_proxy import DatabaseProxy as DatabaseTasks
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.text.md5 import Md5
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.notification_store import NotificationStore
from dNG.pas.data.xhtml.form.email_field import EMailField
from dNG.pas.data.xhtml.form.form_tags_file_field import FormTagsFileField
from dNG.pas.data.xhtml.form.password_field import PasswordField
from dNG.pas.data.xhtml.form.processor import Processor as FormProcessor
from dNG.pas.data.xhtml.form.radio_field import RadioField
from dNG.pas.data.xhtml.form.text_field import TextField
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.database.transaction_context import TransactionContext
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hook import Hook
from .module import Module

class Index(Module):
#
	"""
Service for "m=user"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def _check_tos_accepted(self, field, validator_context):
	#
		"""
Form validator that checks if the TOS have been accepted.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.1.00
		"""

		return (None if (field.get_value() == "accepted") else L10n.get("pas_http_user_form_error_tos_required"))
	#

	def execute_index(self):
	#
		"""
Action for "index"

:since: v0.1.00
		"""

		self.execute_services()
	#

	def execute_register(self, is_save_mode = False):
	#
		"""
Action for "register"

:since: v0.1.00
		"""

		# pylint: disable=star-args

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = source_iline
		if (source_iline == ""): source_iline = "m=user;a=services"

		target = target_iline

		if (target_iline == ""):
		#
			if (Settings.is_defined("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_login_default_target_lang_{0}".format(self.request.get_lang()))
			elif (Settings.is_defined("pas_http_user_login_default_target")): target_iline = Settings.get("pas_http_user_login_default_target")
			else: target_iline = source_iline
		#

		Settings.read_file("{0}/settings/pas_user_profile.json".format(Settings.get("path_data")))
		L10n.init("pas_http_user")

		if (not Settings.get("pas_http_user_registration_allowed", True)): raise TranslatableError("pas_http_user_registration_disabled", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)
		if (is_save_mode): form.set_input_available()

		field = EMailField("uemail")
		field.set_title(L10n.get("pas_http_user_email"))
		field.set_required()
		field.set_limits(_max = 255)
		form.add(field)

		field = TextField("uusername")
		field.set_title(L10n.get("pas_core_username"))
		field.set_required()
		field.set_limits(int(Settings.get("pas_http_core_username_min", 3)), 100)
		field.set_size(TextField.SIZE_SMALL)
		form.add(field)

		field = PasswordField("upassword")
		field.set_title(L10n.get("pas_http_user_password"))
		field.set_required()
		field.set_limits(int(Settings.get("pas_http_user_password_min", 6)))
		field.set_mode(PasswordField.PASSWORD_CLEARTEXT | PasswordField.PASSWORD_WITH_REPETITION)
		form.add(field)

		tos_filepath = Settings.get_lang_associated("pas_http_user_tos_filepath",
		                                            self.request.get_lang(),
		                                            "{0}/settings/pas_user_tos.ftg".format(Settings.get("path_data"))
		                                           )

		field = FormTagsFileField("utos")
		field.set_title(L10n.get("pas_http_user_tos"))
		field.set_required()
		field.set_formtags_filepath(tos_filepath)
		form.add(field)

		tos_choices = [ { "title": L10n.get("core_yes"), "value": "accepted" },
		                { "title": L10n.get("core_no"), "value": "denied" }
		              ]

		field = RadioField("utos_accepted")
		field.set_title(L10n.get("pas_http_user_tos_accepted"))
		field.set_choices(tos_choices)
		field.set_required()
		field.set_validators([ self._check_tos_accepted ])
		form.add(field)

		if (is_save_mode and form.check()):
		#
			email = InputFilter.filter_email_address(form.get_value("uemail"))
			username = InputFilter.filter_control_chars(form.get_value("uusername"))
			password = InputFilter.filter_control_chars(form.get_value("upassword"))

			user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
			if (user_profile_class == None): raise TranslatableError("core_unknown_error")
			user_profile = user_profile_class()

			try:
			#
				user_profile_class.load_email(email, True)
				raise TranslatableError("pas_http_user_email_exists", 403)
			#
			except NothingMatchedException: pass

			try:
			#
				user_profile_class.load_username(username, True)
				raise TranslatableError("pas_http_user_username_exists", 403)
			#
			except NothingMatchedException: pass

			with TransactionContext():
			#
				user_profile_data = { "name": username,
				                      "lang": self.request.get_lang(),
				                      "email": email
				                    }

				user_profile.set_data_attributes(**user_profile_data)
				user_profile.set_password(password)
				user_profile.lock()

				user_profile.save()
			#

			cleanup_timeout_days = int(Settings.get("pas_http_user_registration_days", 28))

			cleanup_timeout = (cleanup_timeout_days * 86400)
			vid = Md5.hash(urandom(32))

			database_tasks = DatabaseTasks.get_instance()
			database_tasks.add("dNG.pas.user.Profile.delete.{0}".format(username), "dNG.pas.user.Profile.delete", cleanup_timeout, username = username)

			database_tasks.add("dNG.pas.user.Profile.sendRegistrationEMail.{0}".format(username),
			                   "dNG.pas.user.Profile.sendRegistrationEMail",
			                   1,
			                   username = username,
			                   vid = vid,
			                   vid_timeout_days = cleanup_timeout_days
			                  )

			database_tasks.register_timeout(vid, "dNG.pas.user.Profile.registrationValidated", cleanup_timeout, username = username, vid = vid)

			target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

			NotificationStore.get_instance().add_info(L10n.get("pas_http_user_done_registration_pending"))

			Link.clear_store("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			alternative_login_links = Hook.call("dNG.pas.http.UserProfile.getAlternativeRegistrationLinks")

			content = { "title": L10n.get("pas_http_user_registration"),
			            "alternative_login_links": (alternative_login_links if (type(alternative_login_links) == list) else [ ])
			          }

			content['form'] = { "object": form,
			                    "url_parameters": { "__request__": True, "a": "register-save", "dsd": { "source": source, "target": target } },
			                    "button_title": "core_continue"
			                  }

			self.response.init()
			self.response.set_title(L10n.get("pas_http_user_registration"))
			self.response.add_oset_content("core.form", content)
		#
	#

	def execute_register_save(self):
	#
		"""
Action for "register-save"

:since: v0.1.00
		"""

		self.execute_register(self.request.get_type() == "POST")
	#

	def execute_services(self):
	#
		"""
Action for "services"

:since: v0.1.00
		"""

		L10n.init("pas_http_user")

		content = { "title": L10n.get("pas_http_user_title_services"),
		            "service_list": { "file": "{0}/settings/lists/pas_user.service.json".format(Settings.get("path_data")) }
		          }

		self.response.init()
		self.response.set_title(L10n.get("pas_http_user_title_services"))
		self.response.add_oset_content("core.service_list", content)
	#
#

##j## EOF