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

from dNG.data.settings import Settings
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n

from .module import Module
from .registration_mixin import RegistrationMixin

class Index(Module, RegistrationMixin):
    """
Service for "m=user"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(Index)

:since: v0.2.00
        """

        Module.__init__(self)
        RegistrationMixin.__init__(self)
    #

    def execute_index(self):
        """
Action for "index"

:since: v0.2.00
        """

        self.execute_services()
    #

    def execute_register(self, is_save_mode = False):
        """
Action for "register"

:since: v0.2.00
        """

        source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
        target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

        self._execute_register(source_iline = source_iline,
                               target_iline = target_iline,
                               is_save_mode = is_save_mode
                              )
    #

    def execute_register_save(self):
        """
Action for "register-save"

:since: v0.2.00
        """

        self.execute_register(self.request.get_type() == "POST")
    #

    def execute_services(self):
        """
Action for "services"

:since: v0.2.00
        """

        L10n.init("pas_http_user")

        content = { "title": L10n.get("pas_http_user_services"),
                    "service_list": { "file": "{0}/settings/lists/pas_user.service.json".format(Settings.get("path_data")) }
                  }

        self.response.init()
        self.response.set_title(content['title'])
        self.response.add_oset_content("core.service_list", content)
    #
#
