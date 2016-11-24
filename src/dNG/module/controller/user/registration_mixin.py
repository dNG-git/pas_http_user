# -*- coding: utf-8 -*-

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

from dNG.controller.predefined_http_request import PredefinedHttpRequest
from dNG.data.settings import Settings
from dNG.data.http.translatable_error import TranslatableError
from dNG.data.http.translatable_exception import TranslatableException
from dNG.data.tasks.database_proxy import DatabaseProxy as DatabaseTasks
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.data.text.md5 import Md5
from dNG.data.xhtml.link import Link
from dNG.data.xhtml.notification_store import NotificationStore
from dNG.data.xhtml.form.email_field import EMailField
from dNG.data.xhtml.form.form_tags_file_field import FormTagsFileField
from dNG.data.xhtml.form.info_field import InfoField
from dNG.data.xhtml.form.password_field import PasswordField
from dNG.data.xhtml.form.processor import Processor as FormProcessor
from dNG.data.xhtml.form.radio_field import RadioField
from dNG.data.xhtml.form.text_field import TextField
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.database.transaction_context import TransactionContext
from dNG.module.named_loader import NamedLoader

class RegistrationMixin(object):
    """
This mixin provides the registration form.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def _check_email_not_registered(self, field, validator_context):
        """
Form validator that checks if the e-mail is not already registered.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.2.00
        """

        _return = None

        user_profile_class = NamedLoader.get_class("dNG.data.user.Profile")

        if (user_profile_class is None): _return = L10n.get("pas_http_core_form_error_internal_error")
        else:
            try:
                user_profile_class.load_email(InputFilter.filter_control_chars(field.get_value()), True)
                _return = L10n.get("pas_http_user_form_error_email_exists")
            except NothingMatchedException: pass
        #

        return _return
    #

    def _check_tos_accepted(self, field, validator_context):
        """
Form validator that checks if the TOS have been accepted.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.2.00
        """

        return (None if (field.get_value() == "accepted") else L10n.get("pas_http_user_form_error_tos_required"))
    #

    def _check_username_not_registered(self, field, validator_context):
        """
Form validator that checks if the user name is not already registered.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.2.00
        """

        _return = None

        user_profile_class = NamedLoader.get_class("dNG.data.user.Profile")

        if (user_profile_class is None): _return = L10n.get("pas_http_core_form_error_internal_error")
        else:
            try:
                user_profile_class.load_username(InputFilter.filter_control_chars(field.get_value()), True)
                _return = L10n.get("pas_http_user_form_error_username_exists")
            except NothingMatchedException: pass
        #

        return _return
    #

    def _execute_register(self, username = None, email = None, ex_type = None, source_iline = "", target_iline = "", is_save_mode = False):
        """
Action for "register"

:param username: User name to be used
:param email: Verified e-mail address to be used
:param ex_type: Externally verified service identifier string
:param source_iline: Source URI query string
:param target_iline: Target URI query string
:param is_save_mode: True if the form is submitted

:since: v0.2.00
        """

        # pylint: disable=star-args

        source = source_iline
        if (source_iline == ""): source_iline = "m=user;a=services"

        target = target_iline

        if (target_iline == ""):
            if (Settings.is_defined("pas_http_user_register_default_target_lang_{0}".format(self.request.get_lang()))): target_iline = Settings.get("pas_http_user_register_default_target_lang_{0}".format(self.request.get_lang()))
            elif (Settings.is_defined("pas_http_user_register_default_target")): target_iline = Settings.get("pas_http_user_register_default_target")
            else: target_iline = source_iline
        #

        L10n.init("pas_http_core_form")
        L10n.init("pas_http_user")

        if (not Settings.get("pas_http_user_registration_allowed", True)): raise TranslatableError("pas_http_user_registration_disabled", 403)

        if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

        Link.set_store("servicemenu",
                       Link.TYPE_RELATIVE_URL,
                       L10n.get("core_back"),
                       { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
                       icon = "mini-default-back",
                       priority = 7
                      )

        if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

        form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

        form = FormProcessor(form_id)
        if (is_save_mode): form.set_input_available()

        is_email_verified = (email is not None)

        if (not is_email_verified):
            field = EMailField("uemail")
            field.set_title(L10n.get("pas_http_user_email"))
            field.set_required()
            field.set_limits(_max = 255)
            field.set_validators([ self._check_email_not_registered ])
            form.add(field)
        #

        if (username is None):
            field = TextField("uusername")
            field.set_required()
            field.set_limits(int(Settings.get("pas_http_core_username_min", 3)), 100)
            field.set_size(TextField.SIZE_SMALL)
        else:
            field = InfoField("uusername")
            field.set_value(username)
        #

        field.set_title(L10n.get("pas_core_username"))
        field.set_validators([ self._check_username_not_registered ])
        form.add(field)

        if (is_email_verified):
            field = InfoField("uemail")
            field.set_title(L10n.get("pas_http_user_email"))
            field.set_value(email)
            field.set_validators([ self._check_email_not_registered ])
            form.add(field)
        #

        if (ex_type is None):
            field = PasswordField("upassword")
            field.set_title(L10n.get("pas_http_user_password"))
            field.set_required()
            field.set_limits(int(Settings.get("pas_http_user_password_min", 6)))
            field.set_mode(PasswordField.PASSWORD_CLEARTEXT | PasswordField.PASSWORD_WITH_REPETITION)
            form.add(field)
        #

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
            if (not is_email_verified): email = InputFilter.filter_email_address(form.get_value("uemail"))
            if (username is None): username = InputFilter.filter_control_chars(form.get_value("uusername"))

            user_profile_class = NamedLoader.get_class("dNG.data.user.Profile")
            if (user_profile_class is None): raise TranslatableException("core_unknown_error")

            user_profile = user_profile_class()

            user_profile_data = { "name": username,
                                  "lang": self.request.get_lang(),
                                  "email": email
                                }

            if (ex_type is None):
                password = InputFilter.filter_control_chars(form.get_value("upassword"))
                user_profile.set_password(password)
            else:
                user_profile_data['type'] = user_profile_class.TYPE_EXTERNAL_VERIFIED_MEMBER
                user_profile_data['type_ex'] = ex_type
            #

            with TransactionContext():
                user_profile.set_data_attributes(**user_profile_data)

                if (not is_email_verified): user_profile.lock()
                else: user_profile.unlock()

                user_profile.save()
            #

            user_id = user_profile.get_id()

            if (not is_email_verified):
                cleanup_timeout_days = int(Settings.get("pas_http_user_registration_days", 28))

                cleanup_timeout = (cleanup_timeout_days * 86400)
                vid = Md5.hash(urandom(32))

                database_tasks = DatabaseTasks.get_instance()

                database_tasks.add("dNG.pas.user.Profile.delete.{0}".format(username),
                                   "dNG.pas.user.Profile.delete",
                                   cleanup_timeout,
                                   username = username
                                  )

                database_tasks.add("dNG.pas.user.Profile.sendRegistrationEMail.{0}".format(username),
                                   "dNG.pas.user.Profile.sendRegistrationEMail",
                                   1,
                                   username = username,
                                   vid = vid,
                                   vid_timeout_days = cleanup_timeout_days
                                  )

                database_tasks.register_timeout(vid,
                                                "dNG.pas.user.Profile.registrationValidated",
                                                cleanup_timeout,
                                                username = username,
                                                vid = vid
                                               )

                self._on_pending_registration(user_id, source_iline, target_iline)
            else: self._on_registration_completed(user_id, source_iline, target_iline)
        else:
            content = { "title": L10n.get("pas_http_user_registration") }

            content['form'] = { "object": form,
                                "url_parameters": { "__request__": True, "a": "register-save", "dsd": { "source": source, "target": target } },
                                "button_title": "core_continue"
                              }

            self.response.init()
            self.response.set_title(content['title'])
            self.response.add_oset_content("core.form", content)
        #
    #

    def _on_pending_registration(self, user_id, source_iline, target_iline):
        """
Called after "register" has added a pending user registration.

:param user_id: User-ID
:param source_iline: Source URI query string
:param target_iline: Target URI query string

:since: v0.2.00
        """

        NotificationStore.get_instance().add_info(L10n.get("pas_http_user_done_registration_pending"))
        target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

        self._on_registration_redirect(target_iline)
    #

    def _on_registration_completed(self, user_id, source_iline, target_iline):
        """
Called after "register" has completed a user registration.

:param user_id: User-ID
:param source_iline: Source URI query string
:param target_iline: Target URI query string

:since: v0.2.00
        """

        NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_user_done_registration"))
        target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

        self._on_registration_redirect(target_iline)
    #

    def _on_registration_redirect(self, iline):
        """
Called after "register" to redirect to the given URI request string.

:param iline: URI request string

:since: v0.2.00
        """

        Link.clear_store("servicemenu")

        redirect_request = PredefinedHttpRequest()
        redirect_request.set_iline(iline)
        self.request.redirect(redirect_request)
    #
#
