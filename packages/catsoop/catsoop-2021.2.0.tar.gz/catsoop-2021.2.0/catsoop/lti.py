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
LTI Tool Provider interface
"""

import re
import uuid
import urllib
import traceback
import pylti.common

from lxml import etree
from lxml.builder import ElementMaker

from datetime import datetime

from oauthlib.oauth1 import Client

from . import auth
from . import session
from . import debug_log

LOGGER = debug_log.LOGGER

DEBUG = True


def log(msg):
    if not DEBUG:
        return
    dt = datetime.now()
    omsg = "[checker:%s]: %s" % (dt, msg)
    LOGGER.info(omsg)


_nodoc = {"Client", "ElementMaker", "etree", "LOGGER", "DEBUG", "datetime", "log"}


class lti4cs(pylti.common.LTIBase):
    """
    LTI object representation for CAT-SOOP: validation and data receipt
    """

    def __init__(self, context, session, lti_args, lti_kwargs):
        self.session = session
        self.lti_data = {}
        self.config = context.get("cs_lti_config", {})
        pylti.common.LTIBase.__init__(self, lti_args, lti_kwargs)

        self.consumers = self.config["consumers"]
        self.lti_session_key = self.config["session_key"]
        self.base_url = self.config.get("base_url")

    def verify_request(self, params, environment):
        try:
            base_url_default = "%s://%s" % (
                environment["wsgi.url_scheme"],
                environment["HTTP_HOST"],
            )
            url = "%s/%s" % (
                self.base_url or base_url_default,
                environment["REQUEST_URI"][1:],
            )
            method = environment["REQUEST_METHOD"]
            LOGGER.info("[lti.lti4cs.verify_request] method=%s, url=%s" % (method, url))
            pylti.common.verify_request_common(
                self.consumers, url, method, environment, params
            )
            LOGGER.info("[lti.lti4cs.verify_request] verify_request success")
            extra_fields = [self.config.get("lti_user_id_field")] + [
                "tool_consumer_info_product_family_code",
                "tool_consumer_.*",
                "custom_canvas_.*",
            ]
            for prop in pylti.common.LTI_PROPERTY_LIST + extra_fields:
                if prop is None:
                    continue
                if params.get(prop, None):
                    LOGGER.info(
                        "[lti.lti4cs.verify_request] params %s=%s",
                        prop,
                        params.get(prop, None),
                    )
                    self.lti_data[prop] = params[prop]
                    continue
                for key in params:
                    m = re.match(prop, key)
                    if m:
                        LOGGER.info(
                            "[lti.lti4cs.verify_request] params %s=%s",
                            key,
                            params.get(key, None),
                        )
                        self.lti_data[key] = params[key]

            self.session["lti_data"] = self.lti_data
            return True

        except Exception as err:
            LOGGER.error(
                "[lti.lti4cs.verify_request] verify_request failed, err=%s" % str(err)
            )
            self.session["lti_data"] = {}
            self.session["is_lti_user"] = False

        return False

    def save_lti_data(self, context):
        """
        Save LTI data locally (e.g. so that the checker can send grades back to the LTI tool consumer)
        """
        logging = context["csm_cslog"]
        uname = context["cs_user_info"]["username"]
        db_name = "_lti_data"
        logging.overwrite_log(
            db_name, [], uname, self.lti_data, **context["cs_logging_kwargs"]
        )


class lti4cs_response(object):
    """
    LTI handler for responses from CAT-SOOP to tool consumer
    """

    def __init__(self, context, lti_data=None):
        """
        Load LTI data from logs (cs database) if available
        """
        if lti_data:
            self.lti_data = lti_data  # use provided LTI data (e.g. for asynchronous grading response)
        else:
            logging = context["csm_cslog"]
            uname = context["cs_user_info"]["username"]
            db_name = "_lti_data"
            self.lti_data = logging.most_recent(
                db_name, [], uname, **context["cs_logging_kwargs"]
            )  # retrieve LTI data
        self.consumers = context.get("cs_lti_config")["consumers"]
        self.pylti_url_fix = context.get("cs_lti_config").get("pylti_url_fix", {})

    def to_dict(self):
        """
        Return dict representation of this LTI response handler
        """
        return self.lti_data

    @property
    def have_data(self):
        return bool(self.lti_data)

    def send_outcome(self, data):
        """
        Send outcome (ie grade) to LTI tool consumer (XML as defined in LTI v1.1)
        """
        url = self.response_url
        result_sourcedid = self.lti_data.get("lis_result_sourcedid", None)
        consumer_key = self.lti_data.get("oauth_consumer_key")
        xml_body = self.generate_result_xml(result_sourcedid, data)
        LOGGER.info(
            "[lti.lti4cs_response.send_outcome] sending grade=%s to %s" % (data, url)
        )
        success = pylti.common.post_message(self.consumers, consumer_key, url, xml_body)
        if success:
            LOGGER.info("[lti.lti4cs_response.send_outcome] outcome sent successfully")
        else:
            LOGGER.error("[lti.lti4cs_response.send_outcome] outcome sending FAILED")

    def generate_result_xml(self, result_sourcedid, score):
        """
        Create the XML document that contains the new score to be sent to the LTI
        consumer. The format of this message is defined in the LTI 1.1 spec.
        """
        elem = ElementMaker(
            nsmap={None: "http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0"}
        )
        xml = elem.imsx_POXEnvelopeRequest(
            elem.imsx_POXHeader(
                elem.imsx_POXRequestHeaderInfo(
                    elem.imsx_version("V1.0"),
                    elem.imsx_messageIdentifier(str(uuid.uuid4())),
                )
            ),
            elem.imsx_POXBody(
                elem.replaceResultRequest(
                    elem.resultRecord(
                        elem.sourcedGUID(elem.sourcedId(result_sourcedid)),
                        elem.result(
                            elem.resultScore(
                                elem.language("en"), elem.textString(str(score))
                            )
                        ),
                    )
                )
            ),
        )
        xml = etree.tostring(xml, xml_declaration=True, encoding="UTF-8")  # bytes
        xml = xml.decode("utf-8")
        return xml

    @property
    def response_url(self):
        """
        Returns remapped lis_outcome_service_url
        uses pylti_url_fix map to support edX dev-stack

        :return: remapped lis_outcome_service_url
        """
        url = ""
        url = self.lti_data["lis_outcome_service_url"]
        urls = self.pylti_url_fix
        # url remapping is useful for using edX devstack
        # edX devstack reports httpS://localhost:8000/ and listens on HTTP
        for prefix, mapping in urls.items():
            if url.startswith(prefix):
                for _from, _to in mapping.items():
                    url = url.replace(_from, _to)
        return url


# -----------------------------------------------------------------------------


class LTI_Consumer(object):
    """
    Simple LTI tool consumer (useful for unit-tests of CAT-SOOP acting as an LTI tool provider)
    """

    def __init__(
        self,
        lti_url="",
        username="lti_user",
        service_url="http://localhost",
        consumer_key="consumer_key",
        secret="secret_key",
    ):
        self.lti_url = lti_url
        self.username = username
        self.service_url = service_url
        self.consumer_key = consumer_key
        self.lti_context = self._get_lti_context(self.lti_url, secret=secret)

    def _get_lti_context(self, lti_url, secret=None):
        """
        Generate the LTI context for a specific LTI url request

        lti_url: (str) URL to the LTI tool provider
        secret: (str) shared secret with the LTI tool provder
        """
        body = {
            "tool_consumer_instance_guid": u"lti_test_%s" % self.lti_url,
            "user_id": self.username + "__LTI__1234",
            "roles": u"[student]",
            "context_id": u"catsoop_test",
            "lti_url": self.lti_url,
            "lti_version": u"LTI-1p0",
            "lis_result_sourcedid": self.username,
            "lis_person_sourcedid": self.username,
            "lis_outcome_service_url": self.service_url,
            "lti_message_type": "basic-lti-launch-request",  # required, see https://www.imsglobal.org/specs/ltiv2p0/implementation-guide#toc-21
            "resource_link_id": "123",
        }
        retdat = body.copy()
        key = self.consumer_key
        self._sign_lti_message(body, key, secret, lti_url)
        LOGGER.info(
            "[unit_tests] signing OAUTH with key=%s, secret=%s, url=%s"
            % (key, secret, lti_url)
        )
        retdat.update(
            dict(
                lti_url=lti_url,
                oauth_consumer_key=key,
                oauth_timestamp=body["oauth_timestamp"],
                oauth_nonce=body["oauth_nonce"],
                # oauth_signature=urllib.parse.unquote(body['oauth_signature']).encode('utf8'),
                oauth_signature=urllib.parse.unquote(body["oauth_signature"]),
                oauth_signature_method=body["oauth_signature_method"],
                oauth_version=body["oauth_version"],
            )
        )
        return retdat

    def _sign_lti_message(self, body, key, secret, url):
        client = Client(client_key=key, client_secret=secret)

        __, headers, __ = client.sign(
            url,
            http_method=u"POST",
            body=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        auth_header = headers["Authorization"][len("OAuth ") :]
        auth = dict(
            [
                param.strip().replace('"', "").split("=")
                for param in auth_header.split(",")
            ]
        )

        body["oauth_nonce"] = auth["oauth_nonce"]
        body["oauth_signature"] = auth["oauth_signature"]
        body["oauth_timestamp"] = auth["oauth_timestamp"]
        body["oauth_signature_method"] = auth["oauth_signature_method"]
        body["oauth_version"] = auth["oauth_version"]


# -----------------------------------------------------------------------------


def serve_lti(context, path_info, environment, params, dispatch_main, return_context):
    """
    **Parameters**:

    * `context`: dictionary, the context associated with this request
    * `path_info`: list of URL path components
    * `environment`: dictionary containing web server data, such as form input
    * `dispatch_main`: function of the same form as `catsoop.dispatch.main`
    """
    if not "cs_lti_config" in context:
        msg = "[lti] LTI not configured - missing cs_lti_config in config.py"
        LOGGER.error(msg)
        raise Exception(msg)

    LOGGER.info("[lti] parameters=%s" % params)
    lti_action = path_info[0]
    LOGGER.info("[lti] lti_action=%s, path_info=%s" % (lti_action, path_info))

    session_data = context["cs_session_data"]
    if "is_lti_user" in session_data:  # needed to handle form POSTS to _lti/course/...
        lti_ok = True  # already authenticated
        l4c = None
    else:
        l4c = lti4cs(context, session_data, {}, {})  # not yet authenticated; check now
        lti_ok = l4c.verify_request(params, environment)
    if not lti_ok:
        msg = "LTI verification failed"
    elif l4c is not None:
        lti_data = session_data["lti_data"]
        lup = context["cs_lti_config"].get("lti_username_prefix", "lti_")
        if "lti_username_function" in context["cs_lti_config"]:
            lti_uname = context["cs_lti_config"]["lti_username_function"](lti_data)
        else:
            default_user_id_field = "user_id"  # used by OpenEdX

            if "canvas" in lti_data.get("tool_consumer_info_product_family_code", ""):
                default_user_id_field = (
                    "custom_canvas_user_login_id"  # used by Canvas LMS
                )

            lti_user_id_field = context["cs_lti_config"].get(
                "lti_user_id_field", default_user_id_field
            )  # allow config to override LTI field to use for uname

            lti_uname = lti_data[lti_user_id_field]

            if context["cs_lti_config"].get("prefer_username_to_userid", True):
                lti_uname = lti_data.get(
                    "lis_person_sourcedid", lti_uname
                )  # prefer username to user_id

        uname = "%s%s" % (lup, lti_uname)

        email = lti_data.get("lis_person_contact_email_primary", "%s@unknown" % uname)
        name = lti_data.get("lis_person_name_full", uname)
        lti_data["cs_user_info"] = {
            "username": uname,
            "name": name,
            "email": email,
            "lti_role": lti_data.get("roles"),
            "is_lti_user": True,
        }  # save LTI user data in session for auth.py
        session_data.update(lti_data["cs_user_info"])
        session.set_session_data(
            context, context["cs_sid"], session_data
        )  # save session data
        user_info = auth.get_logged_in_user(
            context
        )  # saves user_info in context["cs_user_info"]
        LOGGER.info("[lti] auth user_info=%s" % user_info)
        l4c.save_lti_data(context)  # save lti data, e.g. for later use by the checker

    if lti_ok:

        uname = session_data["username"]
        if lti_action == "course":

            LOGGER.info("[lti] rendering course page for %s" % uname)

            sub_path_info = path_info[1:]  # path without _lti/course prefix
            sub_path = "/".join(sub_path_info)
            LOGGER.info("[lti] sub_path=%s" % sub_path)
            environment["PATH_INFO"] = sub_path
            environment["session_id"] = context[
                "cs_sid"
            ]  # so that a new session ID isn't generated
            return dispatch_main(
                environment, return_context=return_context, form_data=params
            )

        msg = "Hello LTI"

    if return_context:
        LOGGER.info("[lti] Returning context instead of HTML response")
        return context

    return (
        ("200", "Ok"),
        {"Content-type": "text/plain", "Content-length": str(len(msg))},
        msg,
    )


def update_lti_score(lti_handler, problemstate, name_map):
    """
    Send a score to an LTI endpoint.

    **Parameters:**

    * `lti_handler`: an instance of `lti4cs` containing the relevant data for
        this request
    * `problemstate`: the _contents_ of the current `problemstate` log (a
        dictionary)
    * `name_map`: a dictionary (or `OrderedDict`) mapping question names to
        those questions' respective contexts (this is of the form generated by
        the default handler by looping over `cs_problem_spec`)
    """
    total_possible_npoints = 0.0
    aggregate_score = 0.0
    cnt = 0
    try:
        for qname, (qtype, info) in name_map.items():
            score = problemstate["scores"].get(qname, 0.0)
            npoints = qtype["total_points"](**info)
            total_possible_npoints += npoints
            aggregate_score += score * npoints
        if total_possible_npoints == 0:
            total_possible_npoints = 1.0
            LOGGER.error("[checker] total_possible_npoints=0 ????")
        aggregate_score_fract = (
            aggregate_score * 1.0 / total_possible_npoints
        )  # LTI wants score in [0, 1.0]
        log(
            "Computed aggregate score from %d questions, aggregate_score=%s (fraction=%s)"
            % (cnt, aggregate_score, aggregate_score_fract)
        )
        score_ok = True
    except Exception as err:
        LOGGER.error(
            "[checker] failed to compute score for problem %s, err=%s"
            % (problemstate, err)
        )
        score_ok = False

    if score_ok:
        try:
            lti_handler.send_outcome(max(0.0, min(1.0, aggregate_score_fract)))
        except Exception as err:
            LOGGER.error(
                "[checker] failed to send outcome to LTI consumer, err=%s" % str(err)
            )
            LOGGER.error("[checker] traceback=%s" % traceback.format_exc())
    return problemstate
