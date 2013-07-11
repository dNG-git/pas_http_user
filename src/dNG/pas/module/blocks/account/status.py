# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.account.Status
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

import re

from dNG.pas.data.session import Session
from dNG.pas.data.settings import Settings
from dNG.pas.data.traced_exception import TracedException
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.http.url import Url
from dNG.pas.data.user.profile import Profile
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.input_form import InputForm
from dNG.pas.data.text.l10n import L10n
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks
from .module import Module

class Status(Module):
#
	"""
Service for "m=account;s=status"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user_profile
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def execute_login(self, is_safe_mode = False):
	#
		"""
Action for "login"

:since: v0.1.00
		"""

		source = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source_iline = (Url.query_param_decode(source) if (source != "") else "m=account;a=services[lang][theme]")

		if (target != ""): target_iline = Url.query_param_decode(target)
		elif (Settings.is_defined("pas_http_user_profile_login_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_profile_login_default_target_lang_{0}".format(self.request.get_lang()))
		elif (Settings.is_defined("pas_http_user_profile_login_default_target")): target_iline = Settings.get("pas_http_user_profile_login_default_target")
		else:
		#
			target = source
			target_iline = source_iline
		#

		L10n.init("pas_http_user_profile")

		Url.store_set("servicemenu", Url.TYPE_RELATIVE, L10n.get("core_back"), { "__query__": re.sub("\\[\\w+\\]", "", source_iline) }, image = "mini_default_back", priority = 2)

		form = NamedLoader.get_instance("dNG.pas.data.xhtml.form.Input", True)
		if (is_safe_mode): form.set_input_available()
		is_cookie_supported = Settings.get("pas_core_cookies_supported", True)

		form.entry_add_text({
			"name": "ausername",
			"title": L10n.get("pas_core_username"),
			"required": True,
			"size": "s",
			"min": int(Settings.get("pas_core_username_min", 3)),
			"max": 100,
			"helper_text": L10n.get("pas_http_user_profile_helper_username")
		})

		form.entry_add_password({
			"name": "apassword",
			"title": L10n.get("pas_http_user_profile_password"),
			"required": True,
			"min": int(Settings.get("pas_http_user_profile_password_min", 6))
		}, InputForm.PASSWORD_TMD5)

		if (is_cookie_supported):
		#
			form_field = {
				"name": "acookie",
				"title": L10n.get("pas_http_user_profile_login_use_cookie"),
				"required": True,
				"choices": [
					{ "value": "1", "title": L10n.get("core_yes") },
					{ "value": "0", "title": L10n.get("core_no") }
				]
			}

			if (not is_safe_mode): form_field['content'] = "1"
			form.entry_add_radio(form_field)
		#

		if (is_safe_mode and form.check()):
		#
			username = InputFilter.filter_control_chars(form.get_value("ausername"))
			password = form.get_value("apassword")
			# TODO: Remove me
			print(password)

			try: user_profile = Profile.load_username(username)
			except TracedException as handled_exception: raise TranslatableException("pas_http_user_profile_username_or_password_invalid", 403, _exception = handled_exception)

			is_validated = (Hooks.call("dNG.pas.http.UserProfile.validateLogin", username = username, password = form.get_value("apassword", _raw_input = True)) if (Settings.get("pas_user_profile_status_mods_supported", False)) else None)
			user_profile_data = user_profile.data_get("id", "password", "banned", "deleted", "locked", "lang", "theme")
			if (is_validated == None): is_validated = (password == user_profile_data['password'])

			if (not is_validated or user_profile_data['deleted'] != 0): raise TranslatableException("pas_http_user_profile_username_or_password_invalid", 403)
			if (user_profile_data['banned'] != 0): raise TranslatableException("pas_http_user_profile_banned", 403)
			if (user_profile_data['locked'] != 0): raise TranslatableException("pas_http_user_profile_locked", 403)

			session = Session.load()
			session.set("session.user_id", user_profile_data['id'])
			session.set_cookie(is_cookie_supported and form.get_value("acookie") == "1")
			session.save()

			self.request.set_session(session)

			target_iline = target_iline.replace("[lang]", ";lang={0}".format(user_profile_data['lang']))
			target_iline = target_iline.replace("[theme]", ";theme={0}".format(user_profile_data['theme']))
			target_iline = re.sub("\\[\\w+\\]", "", target_iline)

			content = {
				"task": L10n.get("pas_core_login"),
				"message": L10n.get("pas_http_user_profile_done_login"),
				"continue_url": Url().build_url(Url.TYPE_RELATIVE, { "__query__": target_iline })
			}

			self.response.init()
			self.response.set_title(L10n.get("pas_http_user_profile_title_login"))
			self.response.add_oset_content("core.done", content)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_user_profile_title_login") }

			content['form'] = {
				"object": form,
				"url_parameters": { "__request__": True, "a": "login-safe", "dsd": { "source": source, "target": target } },
				"button_title": "pas_core_login"
			}

			self.response.init()
			self.response.set_title(L10n.get("pas_http_user_profile_title_login"))
			self.response.add_oset_content("account.status.login", content)
		#
	#

	def execute_login_safe(self):
	#
		"""
Action for "login"

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

		source = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source_iline = (Url.query_param_decode(source) if (source != "") else "")

		if (target != ""): target_iline = Url.query_param_decode(target)
		elif (Settings.is_defined("pas_http_user_profile_logput_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_profile_logput_default_target_lang_{0}".format(self.request.get_lang()))
		elif (Settings.is_defined("pas_http_user_profile_logput_default_target")): target_iline = Settings.get("pas_http_user_profile_logput_default_target")
		else:
		#
			target = source
			target_iline = source_iline
		#

		L10n.init("pas_http_user_profile")

		Url.store_set("servicemenu", Url.TYPE_RELATIVE, L10n.get("core_back"), { "__query__": re.sub("\\[\\w+\\]", "", source_iline) }, image = "mini_default_back", priority = 2)

		session = Session.load(session_create = False)

		if (session != None):
		#
			session.delete()
			self.request.set_session(None)
		#

		target_iline = re.sub("\\[\\w+\\]", "", target_iline)

		content = {
			"task": L10n.get("pas_core_logout"),
			"message": L10n.get("pas_http_user_profile_done_logout"),
			"continue_url": Url().build_url(Url.TYPE_RELATIVE, { "__query__": target_iline })
		}

		self.response.init()
		self.response.set_title(L10n.get("pas_http_user_profile_title_logout"))
		self.response.add_oset_content("core.done", content)
	#
#

##j## EOF