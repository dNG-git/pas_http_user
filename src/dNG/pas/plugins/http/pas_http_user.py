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

from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.value_exception import ValueException
from dNG.pas.tasks.http.user.changes_confirmed import ChangesConfirmed
from dNG.pas.tasks.http.user.registration_validated import RegistrationValidated

def changes_confirmed(params, last_return = None):
#
	"""
Called for "dNG.pas.user.Profile.changesConfirmed"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
	"""

	if (last_return != None): _return = last_return
	elif ("username" not in params
	      or "values_changed" not in params
	      or "vid" not in params
	     ): raise ValueException("Missing required arguments")
	else: _return = ChangesConfirmed(params['username'], params['values_changed'], params['vid']).run()

	return _return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.user.Profile.changesConfirmed", changes_confirmed)
	Hook.register("dNG.pas.user.Profile.registrationValidated", registration_validated)
#

def registration_validated(params, last_return = None):
#
	"""
Called for "dNG.pas.user.Profile.registrationValidated"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
	"""

	if (last_return != None): _return = last_return
	elif ("username" not in params or "vid" not in params): raise ValueException("Missing required arguments")
	else: _return = RegistrationValidated(params['username'], params['vid']).run()

	return _return
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.user.Profile.changesConfirmed", changes_confirmed)
	Hook.unregister("dNG.pas.user.Profile.registrationValidated", registration_validated)
#

##j## EOF