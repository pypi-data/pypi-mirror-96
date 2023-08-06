# This file is part of CAT-SOOP
# Copyright (c) 2011-2021 by The CAT-SOOP Developers <catsoop-dev@mit.edu>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Utility functions related to user management)
"""

import os
import sys
import traceback

from . import loader


def _hide(n):
    return n[0] in ("_", ".") or not n.endswith(".py")


def users_dir(context, course):
    """
    Determine the location of the given course's `__USERS__` directory on disk.

    **Parameters:**

    * `context`: the context associated with this request
    * `course`: the name of the course, as a string

    **Returns:** a string containing the location of the given course's
    `__USERS__` directory.
    """
    root = context["cs_data_root"]
    return os.path.join(root, "courses", course, "__USERS__")


def list_all_users(context, course):
    """
    List all the users in a course

    **Parameters:**

    * `context`: the context associated with this request
    * `course`: the name of the course, as a string

    **Returns:** a list of the usernames of all users in the course
    """
    usrdir = users_dir(context, course)
    return [i.rsplit(".", 1)[0] for i in os.listdir(usrdir) if not _hide(i)]


def read_user_file(context, course, user, default={}):
    """
    Retrieve the contents of a given user's `__USERS__` file within a course.

    **Parameters:**

    * `context`: the context associated with this request
    * `course`: the name of the course, as a string
    * `user: the name of a user, as a string

    **Optional Parameters:**

    * `default` (default `{}`): values to be included in the returned
        dictionary if the given user does not have a
        `__USERS__` file

    **Returns:** a dictionary containing the variables defined in the given
    user's file
    """
    user_file = os.path.join(users_dir(context, course), "%s.py" % user)
    uinfo = dict(default)
    try:
        with open(user_file) as f:
            exec(f.read(), uinfo)
        uinfo["username"] = user
        uinfo["_load_ok"] = True
    except:
        uinfo["_load_ok"] = False
        uinfo["_load_exception"] = traceback.format_exception(*sys.exc_info())
    loader.clean_builtins(uinfo)
    return uinfo


def all_users_info(context, course, filter_func=lambda uinfo: True):
    """
    Return a mapping from usernames to user information

    **Parameters:**

    * `context`: the context associated with this request
    * `course`: the name of the course, as a string

    **Optional Parameters:**

    * `filter_func` (default `lambda uinfo: True`): a function mapping user
        information dictionaries to Booleans; a user is only included in the
        output if the function returns `True` when invoked on their user
        information dictionary

    **Returns:** a dictionary mapping usernames to user information
    dictionaries
    """
    all_users = {
        u: read_user_file(context, course, u, {})
        for u in list_all_users(context, course)
    }
    return {k: v for k, v in all_users.items() if filter_func(v)}
