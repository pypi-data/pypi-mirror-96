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
import html
import json
import base64
import mimetypes
from urllib.parse import urlencode

tutor.qtype_inherit("smallbox")
base, _ = tutor.question("smallbox")

always_rerender = True

defaults.update(
    {
        "csq_soln_filename": "solution.txt",
        "csq_allow_save": False,
        "csq_soln_type": "string",
        "csq_extract_data": True,
    }
)


def handle_submission(submissions, **info):
    o = {"score": None, "msg": "", "rerender": True}
    name = info["csq_name"]
    ll = submissions.get(name, None)
    if ll is not None:
        if info["csq_extract_data"]:
            submissions[name] = info["csm_cslog"].retrieve_upload(
                ll[1], **info["cs_logging_kwargs"]
            )[1]
        o.update(base["handle_submission"](submissions, **info))
    return o


def render_html(last_log, **info):
    name = info["csq_name"]
    out = """<input type="file" style="display: none" id=%s name="%s" />""" % (
        name,
        name,
    )
    out += (
        """<button class="btn btn-catsoop" id="%s_select_button">Select File</button>&nbsp;"""
        """<tt><span id="%s_selected_file">No file selected</span></tt>"""
    ) % (name, name)
    out += (
        """<script type="text/javascript">"""
        "\n// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-v3"
        """\ndocument.getElementById('%s_select_button').addEventListener('click', function (){"""
        """\n    document.getElementById("%s").click();"""
        """\n});"""
        """\ndocument.getElementById('%s').addEventListener('change', function (){"""
        """\n    document.getElementById('%s_selected_file').innerText = document.getElementById('%s').value;"""
        """\n});"""
        "\n// @license-end"
        """</script>"""
    ) % (name, name, name, name, name)
    ll = last_log.get(name, None)
    if ll is not None:
        try:
            fname, loc = ll
            qstring = urlencode({"id": loc})
            out += "<br/>"
            out += (
                '<a href="%s/_util/get_upload?%s" '
                'download="%s">Download Most '
                "Recent Submission</a>"
            ) % (info["cs_url_root"], qstring, html.escape(fname))
        except:
            pass
    return out


def answer_display(**info):
    name = info["csq_soln_filename"]
    if info["csq_soln_type"] == "string":
        data = csm_thirdparty.data_uri.DataURI.make(
            "text/plain", None, True, info["csq_soln"]
        )
    else:
        data = csm_thirdparty.data_uri.DataURI.from_file(info["csq_soln"])
        ext = mimetypes.guess_extension(data.mimetype) or ".txt"
        name = name.rsplit(".", 1) + ext
    return ('<a href="%s" ' 'download="%s">Download Solution</a>') % (data, name)
