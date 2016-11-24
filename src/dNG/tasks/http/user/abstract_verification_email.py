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

from dNG.data.rfc.email.message import Message
from dNG.data.rfc.email.part import Part
from dNG.data.text.l10n import L10n
from dNG.net.smtp.client import Client as SmtpClient
from dNG.module.named_loader import NamedLoader
from dNG.runtime.value_exception import ValueException
from dNG.tasks.abstract import Abstract as AbstractTask

class AbstractVerificationEMail(AbstractTask):
    """
The "AbstractVerificationEMail" task will send a verification e-mail to the user
profile's address.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: user
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    EMAIL_RENDERER = None
    """
E-mail renderer to be used to send the verification
    """

    def __init__(self, username, vid, vid_timeout_days):
        """
Constructor __init__(AbstractVerificationEMail)

:param username: Username to send the verification e-mail to
:param vid: Verification ID
:param vid_timeout_days: Days until vID will time out

:since: v0.2.00
        """

        AbstractTask.__init__(self)

        self.username = username
        """
Username to send the e-mail to
        """
        self.vid = vid
        """
Verification ID
        """
        self.vid_timeout_days = vid_timeout_days
        """
Verification ID timeout (as days)
        """
    #

    def get_email_recipient(self):
        """
Returns the verification e-mail recipient address.

:return: (str) Verification e-mail recipient; None for default recipient
:since:  v0.2.00
        """

        return None
    #

    def get_email_subject(self, l10n):
        """
Returns the verification e-mail subject.

:param l10n: L10n instance

:return: (str) Verification e-mail subject; None for default subject
:since:  v0.2.00
        """

        return None
    #

    def run(self):
        """
Task execution

:since: v0.2.00
        """

        if (self.__class__.EMAIL_RENDERER is None): raise ValueException("Defined e-mail renderer is invalid")

        user_profile_class = NamedLoader.get_class("dNG.data.user.Profile")
        user_profile = user_profile_class.load_username(self.username)

        user_profile_data = user_profile.get_data_attributes("name", "lang", "email")

        email = self.get_email_recipient()
        if (email is None): email = user_profile_data['email']

        L10n.init("core", user_profile_data['lang'])
        L10n.init("pas_core", user_profile_data['lang'])
        L10n.init("pas_http_user", user_profile_data['lang'])

        l10n = L10n.get_instance(user_profile_data['lang'])

        email_renderer = NamedLoader.get_instance(self.__class__.EMAIL_RENDERER, l10n = l10n)
        content = email_renderer.render(user_profile_data, self.vid, self.vid_timeout_days)

        subject = self.get_email_subject(l10n)
        if (subject is None): subject = l10n.get("pas_http_user_title_verification")

        part = Part(Part.TYPE_MESSAGE_BODY, "text/plain", content)

        message = Message()
        message.add_body(part)
        message.set_subject(subject)
        message.set_to(Message.format_address(user_profile_data['name'], email))

        smtp_client = SmtpClient()
        smtp_client.set_message(message)
        smtp_client.send()
    #
#
