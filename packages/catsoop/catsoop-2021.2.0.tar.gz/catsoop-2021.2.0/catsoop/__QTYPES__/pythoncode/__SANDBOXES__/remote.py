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

import json
import urllib.request, urllib.parse, urllib.error

SANDBOX_URL = "https://catsoop.mit.edu/python_sandbox_v2019.9/"


def run_code(
    context,
    code,
    options,
    count_opcodes=False,
    opcode_limit=None,
    result_as_string=False,
):
    code = code.replace("\r\n", "\n")
    data = urllib.parse.urlencode(
        {"code": code, "result_as_string": result_as_string}
    ).encode()
    request = urllib.request.Request(context.get("csq_sandbox_url", SANDBOX_URL), data)
    try:
        resp = urllib.request.urlopen(request, data).read()
        return json.loads(resp.decode())
    except:
        err = "CAT-SOOP: Could not connect to %s" % context.get(
            "csq_sandbox_url", SANDBOX_URL
        )
        return {"fname": "", "out": "", "err": err, "info": {}}
