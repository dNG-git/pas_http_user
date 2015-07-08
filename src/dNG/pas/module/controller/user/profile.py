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

from os import urandom
import re

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.settings import Settings
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.tasks.database_proxy import DatabaseProxy as DatabaseTasks
from dNG.pas.data.text.date_time import DateTime
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.text.md5 import Md5
from dNG.pas.data.xhtml.form_tags import FormTags
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.notification_store import NotificationStore
from dNG.pas.data.xhtml.form.email_field import EMailField
from dNG.pas.data.xhtml.form.form_tags_text_field import FormTagsTextField
from dNG.pas.data.xhtml.form.form_tags_textarea_field import FormTagsTextareaField
from dNG.pas.data.xhtml.form.info_field import InfoField
from dNG.pas.data.xhtml.form.password_field import PasswordField
from dNG.pas.data.xhtml.form.text_field import TextField
from dNG.pas.data.xhtml.form.processor import Processor as FormProcessor
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.module.named_loader import NamedLoader
from .module import Module

class Profile(Module):
#
	"""
Service for "m=user;s=profile"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	CHANGE_TYPE_EMAIL = 1
	"""
Change the e-mail address
	"""
	CHANGE_TYPE_PASSWORD = 2
	"""
Change the password
	"""
	CHANGE_TYPE_USERNAME = 4
	"""
Change the username
	"""

	def execute_change_email(self):
	#
		"""
Action for "change-email"

:since: v0.1.00
		"""

		self._execute_validated_profile_change(Profile.CHANGE_TYPE_EMAIL, "change-email")
	#

	def execute_change_email_save(self):
	#
		"""
Action for "change-email-save"

:since: v0.1.00
		"""

		self._execute_validated_profile_change(Profile.CHANGE_TYPE_EMAIL,
		                                       "change-email",
		                                       (self.request.get_type() == "POST")
		                                      )
	#

	def execute_change_username(self):
	#
		"""
Action for "change-username"

:since: v0.1.01
		"""

		self._execute_validated_profile_change(Profile.CHANGE_TYPE_USERNAME,
		                                       "change-username"
		                                      )
	#

	def execute_change_username_save(self):
	#
		"""
Action for "change-username"

:since: v0.1.01
		"""

		self._execute_validated_profile_change(Profile.CHANGE_TYPE_USERNAME,
		                                       "change-username",
		                                       (self.request.get_type() == "POST")
		                                      )
	#

	def execute_change_username_password(self):
	#
		"""
Action for "change-username-password"

:since: v0.1.00
		"""

		self._execute_validated_profile_change(Profile.CHANGE_TYPE_USERNAME | Profile.CHANGE_TYPE_PASSWORD,
		                                       "change-username-password"
		                                      )
	#

	def execute_change_username_password_save(self):
	#
		"""
Action for "change-username-password"

:since: v0.1.00
		"""

		self._execute_validated_profile_change(Profile.CHANGE_TYPE_USERNAME | Profile.CHANGE_TYPE_PASSWORD,
		                                       "change-username-password",
		                                       (self.request.get_type() == "POST")
		                                      )
	#

	def execute_index(self):
	#
		"""
Action for "index"

:since: v0.1.00
		"""

		self.execute_view()
	#

	def execute_edit(self, is_save_mode = False):
	#
		"""
Action for "edit"

:since: v0.1.00
		"""

		pid = InputFilter.filter_file_path(self.request.get_dsd("upid", ""))

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = source_iline
		if (source_iline == ""): source_iline = "m=user;s=profile;dsd=upid+{0}".format(Link.encode_query_value(pid))

		target = target_iline
		if (target_iline == ""): target_iline = source_iline

		L10n.init("pas_http_user")

		session = self.request.get_session()

		session_user_is_administrator = False
		session_user_pid = None
		session_user_profile = None

		if (session is not None):
		#
			session_user_pid = session.get_user_id()
			session_user_profile = session.get_user_profile()

			if (session_user_profile is not None):
			#
				if (session_user_profile.is_valid()): session_user_is_administrator = session_user_profile.is_type("ad")
				if (pid == ""): pid = session_user_pid
			#
		#

		if (pid == ""): raise TranslatableError("pas_http_user_pid_invalid", 404)

		user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
		if (user_profile_class is None): raise TranslatableException("core_unknown_error")

		try: user_profile = user_profile_class.load_id(pid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_user_pid_invalid", 404, _exception = handled_exception)

		if ((not session_user_is_administrator)
		    and (pid != session_user_pid or (not user_profile.is_valid()))
		   ): raise TranslatableError("core_access_denied", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE_URL,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		edit_source = ("m=user;s=profile;a=edit;dsd=upid+{0}".format(Link.encode_query_value(pid)) if (source == "") else source)

		if (not user_profile.is_type("ex")):
		#
			Link.set_store("servicemenu",
			               Link.TYPE_RELATIVE_URL,
			               (L10n.get("pas_http_user_change_username_or_password")
			                if (Settings.get("pas_http_user_change_username_allowed", True)) else
			                L10n.get("pas_http_user_change_password")
			               ),
			               { "m": "user", "s": "profile", "a": "change-username-password", "dsd": { "source": edit_source, "target": target } },
			               icon = "mini-default-option",
			               priority = 3
			              )

			if (not session_user_is_administrator):
			#
				Link.set_store("servicemenu",
				               Link.TYPE_RELATIVE_URL,
				               L10n.get("pas_http_user_change_email"),
				               { "m": "user", "s": "profile", "a": "change-email", "dsd": { "source": edit_source, "target": target } },
				               icon = "mini-default-option",
				               priority = 3
				              )
			#
		#
		elif (Settings.get("pas_http_user_change_username_allowed", True)):
		#
			Link.set_store("servicemenu",
			               Link.TYPE_RELATIVE_URL,
			               L10n.get("pas_http_user_change_username"),
			               { "m": "user", "s": "profile", "a": "change-username", "dsd": { "source": edit_source, "target": target } },
			               icon = "mini-default-option",
			               priority = 3
			              )
		#

		if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)

		user_profile_data = user_profile.get_data_attributes("name", "email", "signature", "title")

		email = user_profile_data['email']
		title = user_profile_data['title']

		if (is_save_mode): form.set_input_available()

		if (session_user_is_administrator):
		#
			field = EMailField("uemail")
			field.set_title(L10n.get("pas_http_user_email"))
			field.set_value(email)
			field.set_required()
			field.set_limits(_max = 255)
			form.add(field)
		#
		else:
		#
			field = InfoField("uemail")
			field.set_title(L10n.get("pas_http_user_email"))
			field.set_value(email)
			form.add(field)
		#

		field = FormTagsTextareaField("usignature")
		field.set_title(L10n.get("pas_http_user_signature"))
		field.set_value(user_profile_data['signature'])
		field.set_size(FormTagsTextareaField.SIZE_SMALL)
		field.set_limits(_max = 255)
		form.add(field)

		if (session_user_is_administrator):
		#
			field = FormTagsTextField("utitle")
			field.set_title(L10n.get("pas_http_user_title"))
			field.set_value(title)
			field.set_limits(_max = 255)
			form.add(field)
		#

		if (is_save_mode and form.check()):
		#
			if (session_user_is_administrator): email = InputFilter.filter_control_chars(form.get_value("uemail"))
			signature = InputFilter.filter_control_chars(form.get_value("usignature"))
			if (session_user_is_administrator): title = InputFilter.filter_control_chars(form.get_value("utitle"))

			original_user_profile_data = user_profile_data.copy()
			user_profile_data_changed = { "signature": FormTags.encode(signature) }

			if (session_user_is_administrator):
			#
				user_profile_data_changed['email'] = email
				user_profile_data_changed['title'] = FormTags.encode(title)
			#

			user_profile.set_data_attributes(**user_profile_data_changed)
			user_profile.save()

			DatabaseTasks.get_instance().add("dNG.pas.user.Profile.onEdited.{0}".format(user_profile_data['name']),
			                                 "dNG.pas.user.Profile.onEdited",
			                                 1,
			                                 user_profile_id = pid,
			                                 user_profile_data_changed = user_profile_data_changed,
			                                 original_user_profile_data = original_user_profile_data
			                                )

			target_iline = target_iline.replace("__id_d__", pid)
			target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

			NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_user_done_change_profile"))

			Link.clear_store("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_user_title_change_profile") }

			content['form'] = { "object": form,
			                    "url_parameters": { "__request__": True,
			                                        "a": "edit-save",
			                                        "dsd": { "source": source, "target": target }
			                                      },
			                    "button_title": "pas_http_core_edit"
			                  }

			self.response.init()
			self.response.set_title(L10n.get("pas_http_user_title_change_profile"))
			self.response.add_oset_content("core.form", content)
		#
	#

	def execute_edit_save(self):
	#
		"""
Action for "edit-save"

:since: v0.1.00
		"""

		self.execute_edit(self.request.get_type() == "POST")
	#

	def _execute_validated_profile_change(self, _type, base_action, is_save_mode = False):
	#
		"""
Action for public "change-*" requests

:since: v0.1.00
		"""

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = source_iline
		if (source_iline == ""): source_iline = "m=user"

		target = target_iline
		if (target_iline == ""): target_iline = source_iline

		L10n.init("pas_http_user")

		session = self.request.get_session()

		pid = None
		if (session is not None): pid = session.get_user_id()
		if (pid is None): raise TranslatableError("pas_http_user_pid_invalid", 404)

		user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
		if (user_profile_class is None): raise TranslatableException("core_unknown_error")

		try: user_profile = user_profile_class.load_id(pid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_user_pid_invalid", 404, _exception = handled_exception)

		if (not user_profile.is_valid()): raise TranslatableError("core_access_denied", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		if (source_iline == ""): source_iline = "m=user;s=profile;a=edit;dsd=upid+{0}".format(Link.encode_query_value(pid))

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE_URL,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

		change_email = (_type & Profile.CHANGE_TYPE_EMAIL == Profile.CHANGE_TYPE_EMAIL)

		change_password = ((not user_profile.is_type("ex"))
		                   and _type & Profile.CHANGE_TYPE_PASSWORD == Profile.CHANGE_TYPE_PASSWORD
		                  )

		change_username = (Settings.get("pas_http_user_change_username_allowed", True)
		                   and _type & Profile.CHANGE_TYPE_USERNAME == Profile.CHANGE_TYPE_USERNAME
		                   )

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)

		user_profile_data = user_profile.get_data_attributes("name", "email")

		current_email = user_profile_data['email']
		current_username = user_profile_data['name']

		if (is_save_mode): form.set_input_available()

		if (not user_profile.is_type("ex")):
		#
			field = PasswordField("upassword")
			field.set_title(L10n.get("pas_http_user_password_current"))
			field.set_required()
			field.set_limits(int(Settings.get("pas_http_user_password_min", 6)))
			field.set_mode(PasswordField.PASSWORD_CLEARTEXT)
			form.add(field)
		#

		if (change_username):
		#
			field = TextField("uusername")
			field.set_title(L10n.get("pas_core_username"))
			field.set_value(current_username)
			field.set_required()
			field.set_limits(int(Settings.get("pas_http_core_username_min", 3)), 100)
			field.set_size(TextField.SIZE_SMALL)
			form.add(field)
		#

		if (change_email):
		#
			field = EMailField("uemail")
			field.set_title(L10n.get("pas_http_user_email"))
			field.set_value(current_email)
			field.set_required()
			field.set_limits(_max = 255)
			form.add(field)
		#

		if (change_password):
		#
			field = PasswordField("upassword_new")
			field.set_title(L10n.get("pas_http_user_password_new"))
			field.set_limits(int(Settings.get("pas_http_user_password_min", 6)))
			field.set_mode(PasswordField.PASSWORD_CLEARTEXT | PasswordField.PASSWORD_WITH_REPETITION)
			form.add(field)
		#

		if (is_save_mode and form.check()):
		#
			if (not user_profile.is_type("ex")):
			#
				current_password = InputFilter.filter_control_chars(form.get_value("upassword"))
				if (not user_profile.is_password_valid(current_password)): raise TranslatableError("pas_http_user_password_invalid", 403)
			#

			new_email = (InputFilter.filter_control_chars(form.get_value("uemail"))
			             if (change_email) else
			             None
			            )

			new_password = (InputFilter.filter_control_chars(form.get_value("upassword_new"))
			                if (change_password) else
			                None
			               )

			new_username = (InputFilter.filter_control_chars(form.get_value("uusername"))
			                if (change_username) else
			                None
			               )

			user_profile_data_changed = { }

			if (change_email and current_email != new_email):
			#
				try:
				#
					user_profile_class.load_email(new_email, True)
					raise TranslatableError("pas_http_user_email_exists", 403)
				#
				except NothingMatchedException: pass
			#

			if (change_username and current_username != new_username):
			#
				try:
				#
					user_profile_class.load_username(new_username, True)
					raise TranslatableError("pas_http_user_username_exists", 403)
				#
				except NothingMatchedException: pass

				user_profile_data_changed['name'] = new_username
				user_profile.set_data_attributes(**user_profile_data_changed)
			#

			if (not user_profile.is_type("ex")):
			#
				if (change_password
				    and new_password != ""
				    and current_password != new_password
				   ): user_profile.set_password(new_password)
				elif (change_username
				      and current_username != new_username
				     ): user_profile.set_password(current_password)
			#

			user_profile.save()

			database_tasks = DatabaseTasks.get_instance()
			username = (new_username if (new_username is not None) else current_username)

			if (len(user_profile_data_changed) > 0):
			#
				original_user_profile_data = user_profile.get_data_attributes(*user_profile_data_changed.keys())

				database_tasks.add("dNG.pas.user.Profile.onEdited.{0}".format(username),
				                                 "dNG.pas.user.Profile.onEdited",
				                                 1,
				                                 user_profile_id = pid,
				                                 user_profile_data_changed = user_profile_data_changed,
				                                 original_user_profile_data = original_user_profile_data
				                                )
			#

			if (change_email and current_email != new_email):
			#
				cleanup_timeout_days = int(Settings.get("pas_http_user_change_profile_days", 7))

				cleanup_timeout = (cleanup_timeout_days * 86400)
				vid = Md5.hash(urandom(32))

				database_tasks.add("dNG.pas.user.Profile.sendChangePendingEMail.{0}".format(username),
				                   "dNG.pas.user.Profile.sendChangePendingEMail",
				                   1,
				                   username = username,
				                   recipient = new_email,
				                   vid = vid,
				                   vid_timeout_days = cleanup_timeout_days
				                  )

				database_tasks.register_timeout(vid,
				                                "dNG.pas.user.Profile.changesConfirmed",
				                                cleanup_timeout,
				                                username = username,
				                                values_changed = { "email": new_email },
				                                vid = vid
				                               )
			#

			target_iline = target_iline.replace("__id_d__", pid)
			target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

			if (change_email
			    and current_email != new_email
			   ): NotificationStore.get_instance().add_info(L10n.get("pas_http_user_done_change_profile_pending"))
			else: NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_user_done_change_profile"))

			Link.clear_store("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_user_title_change_profile") }

			content['form'] = { "object": form,
			                    "url_parameters": { "__request__": True,
			                                        "a": "{0}-save".format(base_action),
			                                        "dsd": { "source": source, "target": target }
			                                      },
			                    "button_title": "pas_http_core_edit"
			                  }

			self.response.init()
			self.response.set_title(L10n.get("pas_http_user_title_change_profile"))
			self.response.add_oset_content("core.form", content)
		#
	#

	def execute_view(self):
	#
		"""
Action for "view"

:since: v0.1.00
		"""

		pid = InputFilter.filter_file_path(self.request.get_dsd("upid", ""))

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()

		source = source_iline
		if (source_iline == ""): source_iline = "m=user;a=services"

		L10n.init("pas_http_user")

		session = self.request.get_session()

		session_user_is_administrator = False
		session_user_pid = None
		session_user_profile = None

		if (session is not None):
		#
			session_user_pid = session.get_user_id()
			session_user_profile = session.get_user_profile()

			if (session_user_profile is not None and session_user_profile.is_valid()):
			#
				session_user_is_administrator = session_user_profile.is_type("ad")
				if (pid == ""): pid = session_user_pid
			#
			else: session_user_pid = None
		#

		if (pid == ""): raise TranslatableError("pas_http_user_pid_invalid", 404)

		user_profile_class = NamedLoader.get_class("dNG.pas.data.user.Profile")
		if (user_profile_class is None): raise TranslatableException("core_unknown_error")

		try: user_profile = user_profile_class.load_id(pid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_user_pid_invalid", 404, _exception = handled_exception)

		if (user_profile.is_deleted()): raise TranslatableError("pas_http_user_pid_invalid", 404)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE_URL,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		if (session_user_pid is not None):
		#
			Link.set_store("servicemenu",
			               Link.TYPE_RELATIVE_URL,
			               L10n.get("pas_http_user_profile_edit"),
			               { "m": "user", "s": "profile", "a": "edit", "dsd": { "source": source } },
			               icon = "mini-default-option",
			               priority = 3
			              )
		#

		user_profile_data = user_profile.get_data_attributes("type",
		                                                     "name",
		                                                     "email",
		                                                     "email_public",
		                                                     "title",
		                                                     "signature",
		                                                     "registration_ip",
		                                                     "registration_time",
		                                                     "lastvisit_ip",
		                                                     "lastvisit_time"
		                                                    )

		form = FormProcessor(False)

		if (user_profile_data['email'] != ""
		    and session_user_profile is not None
		    and session_user_profile.is_valid()
		   ):
		#
			field = InfoField("uemail")
			field.set_title(L10n.get("pas_http_user_email"))

			if (session_user_is_administrator or user_profile_data['email_public']): field.set_value(user_profile_data['email'])
			else: field.set_value(L10n.get("pas_http_user_send_email"))

			field.set_link(Link().build_url(Link.TYPE_RELATIVE_URL,
			                                { "m": "user", "s": "email", "dsd": { "upid": pid } }
			                               )
			              )

			form.add(field)
		#

		if (user_profile_data['registration_time'] > 0):
		#
			field = InfoField("uregistration_time")
			field.set_title(L10n.get("pas_http_user_registration_time"))
			field.set_value(DateTime.format_l10n(DateTime.TYPE_DATE_TIME_SHORT, user_profile_data['registration_time']))
			form.add(field)

			if (session_user_is_administrator and user_profile_data['registration_ip'] != ""):
			#
				field = InfoField("uregistration_ip")
				field.set_title(L10n.get("pas_http_user_registration_ip"))
				field.set_value(user_profile_data['registration_ip'])
				form.add(field)
			#
		#

		if (user_profile_data['lastvisit_time'] > 0):
		#
			field = InfoField("ulastvisit_time")
			field.set_title(L10n.get("pas_http_user_lastvisit_time"))
			field.set_value(DateTime.format_l10n(DateTime.TYPE_DATE_TIME_SHORT, user_profile_data['lastvisit_time']))
			form.add(field)

			if (session_user_is_administrator and user_profile_data['lastvisit_ip'] != ""):
			#
				field = InfoField("ulastvisit_ip")
				field.set_title(L10n.get("pas_http_user_lastvisit_ip"))
				field.set_value(user_profile_data['lastvisit_ip'])
				form.add(field)
			#
		#

		content = { "title": user_profile_data['name'],
		            "username": user_profile_data['name'],
		            "usertitle": user_profile_data['title'],
		            "signature": user_profile_data['signature'],
		            "form": { "object": form }
		          }

		self.response.init()
		self.response.set_title(user_profile_data['name'])
		self.response.add_oset_content("user.profile", content)
	#
#

##j## EOF