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

import os
import ast
import sys
import time
import uuid
import fcntl
import shutil
import hashlib
import logging
import tempfile
import resource
import subprocess

LOGGER = logging.getLogger("cs")

_resource_mapper = {
    "CPUTIME": (resource.RLIMIT_CPU, lambda x: (x, x + 1)),
    "MEMORY": (resource.RLIMIT_AS, lambda x: (x, x)),
    "FILESIZE": (resource.RLIMIT_FSIZE, lambda x: (x, x)),
}


def run_code(
    context,
    code,
    options,
    count_opcodes=False,
    opcode_limit=None,
    result_as_string=False,
):
    if options.get("do_rlimits", True):
        rlimits = [(resource.RLIMIT_NPROC, (0, 0))]
        for key, val in _resource_mapper.items():
            if key == "MEMORY" and options[key] <= 0:
                continue
            rlimits.append((val[0], val[1](options[key])))
    else:
        rlimits = []

    def limiter():
        os.setsid()
        for i in rlimits:
            resource.setrlimit(*i)
        context["csm_process"].set_pdeathsig()()

    tmpdir = context.get("csq_sandbox_dir", "/tmp/sandbox")
    this_one = "_%s" % uuid.uuid4().hex
    tmpdir = os.path.join(tmpdir, this_one)
    with open(
        os.path.join(
            context["cs_fs_root"],
            "__QTYPES__",
            "pythoncode",
            "__SANDBOXES__",
            "_template",
        )
    ) as f:
        template = f.read()
    template %= {
        "enable_opcode_count": count_opcodes,
        "result_as_string": result_as_string,
        "test_module": this_one,
        "opcode_limit": opcode_limit or float("inf"),
    }
    os.makedirs(tmpdir, 0o777)
    with open(os.path.join(tmpdir, "run_catsoop_test.py"), "w") as f:
        f.write(template)
    for f in options["FILES"]:
        typ = f[0].strip().lower()
        if typ == "copy":
            shutil.copyfile(f[1], os.path.join(tmpdir, f[2]))
        elif typ == "string":
            with open(os.path.join(tmpdir, f[1]), "w") as fileobj:
                fileobj.write(f[2])
    fname = "%s.py" % this_one
    with open(os.path.join(tmpdir, fname), "w") as fileobj:
        fileobj.write(code.replace("\r\n", "\n"))

    LOGGER.debug(
        "[pythoncode.sandbox.python] context cs_version=%s, cs_python_interpreter=%s"
        % (context.get("cs_version"), context.get("cs_python_interpreter"))
    )

    interp = context.get(
        "csq_python_interpreter", context.get("cs_python_interpreter", "python3")
    )

    try:
        p = subprocess.Popen(
            [interp, "-E", "-B", "run_catsoop_test.py"],
            cwd=tmpdir,
            preexec_fn=limiter,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as err:
        LOGGER.error(
            "[pythoncode.sandbox.python] error executing subprocess, interp=%s, fname=%s, tmpdir=%s, preexec_fn=%s"
            % (interp, fname, tmpdir, limiter)
        )
        raise Exception(
            "[cs.qtypes.pythoncode.python] Failed to execute subprocess interp=%s (need to set csq_python_interpreter?), err=%s"
            % (interp, err)
        )

    out = ""
    err = ""
    try:
        out, err = p.communicate(options["STDIN"] or "", timeout=options["CLOCKTIME"])
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
        out, err = p.communicate()
    out = out.decode()
    err = err.decode()

    shutil.rmtree(tmpdir, True)

    n = out.rsplit("---", 1)
    log = {}
    if len(n) == 2:  # should be this
        out, log = n
        try:
            log = context["csm_util"].literal_eval(log)
        except:
            log = {}

    if log == {} or log.get("opcode_limit_reached", False):
        if err.strip() == "":
            err = (
                "Your code did not run to completion, "
                "but no error message was returned."
                "\nThis normally means that your code contains an "
                "infinite loop or otherwise took too long to run."
            )

    if len(n) > 2:  # ???
        out = ""
        log = {}
        err = "BAD CODE - this will be logged"

    return {"fname": fname, "out": out, "err": err, "info": log}
