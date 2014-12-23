# -*- coding: utf-8 -*-

import hashlib
import requests
import time
import json

from xml.dom import minidom

from .messages import MESSAGE_TYPES, UnknownMessage
from .exceptions import ParseError, NeedParseError, NeedParamError, OfficialAPIError
from .reply import TextReply

class WechatBasic(object):
    """
    The basic service for Wechat
    """
    def __init__(self, token=None, appid=None, appsecret=None, partnerid=None,
            partnerkey=None, paysignkey=None, access_token=None, 
            access_token_expires_at=None):
        self.__token = token
        self.__appid = appid
        self.__appsecret = appsecret
        self.__partnerid = partnerid
        self.__partnerkey = partnerkey
        self.__paysignkey = paysignkey
        self.__access_token = access_token
        self.__access_token_expires_at = access_token_expires_at
        self.__is_parse = False
        self.__message = None

    def check_signature(self, signature, timestamp, nonce):
        self._check_token()
        if not signature or not timestamp or not nonce:
            return False
        tmp_list = [self.__token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        if signature == hashlib.sha1(tmp_str).hexdigest():
            return True
        else:
            return False

    def parse_data(self, data):
        result = {}
        if type(data) == unicode:
            data = data.encode('utf-8')
        elif type(data) == str:
            pass
        else:
            raise ParseError()

        try:
            doc = minidom. parseString(data)
        except Exception:
            raise ParseError()

        params = [ele for ele in doc.childNodes[0].childNodes
                    if isinstance(ele, minidom.Element)]

        for param in params:
            if param.childNodes:
                text = param.childNodes[0]
                result[param.tagName] = text.data
        result['raw'] = data
        result['type'] = result.pop('MsgType').lower()
        message_type = MESSAGE_TYPES.get(result['type'], UnknownMessage)
        self.__message = message_type(result)
        self.__is_parse = True

    def get_message(self):
        self._check_parse()
        return self.__message

 
    def get_access_token(self):
        self._check_appid_appsecret()
        return {
            'access_token': self.access_token,
            'access_token_expires_at': self.__access_token_expires_at,
        }

    def response_text(self, content):
        self._check_parse()
        content = self._transcoding(content)
        return TextReply(message=self.__message, content=content).render()

    def grant_token(self):
        self._check_appid_appsecret()
        return self._get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.__appid,
                "secret": self.__appsecret,
            }
        )

    def send_text_message(self, user_id, content):
        self._check_appid_appsecret()
        return self._post(
            url='https://api.weixin.qq.com/cgi-bin/message/custom/send',
            data={
                'touser': user_id,
                'msgtype': 'text',
                'text': {
                    'content': content,
                },
            }
        )
 
    @property
    def access_token(self):
        self._check_appid_appsecret()
        if self.__access_token:
            now = time.time()
            if self.__access_token_expires_at - now > 60:
                return self.__access_token
        response_json = self.grant_token()
        self.__access_token = response_json['access_token']
#        self.__access_token_expires_at = int(time.time()) 
#                + response_json['expires_in']
        return self.__access_token

    def _check_token(self):
        if not self.__token:
            raise NeedParamError('Please provide Token parameter in the construction of class.')

    def _check_appid_appsecret(self):
        if not self.__appid or not self.__appsecret:
            raise NeedParamError('Please provide app_id and app_secret parameters in the construction of class.')

    def _check_parse(self):
        if not self.__is_parse:
            raise NeedParseError()

    def _check_official_error(self, json_data):
        if "errcode" in json_data and json_data["errcode"] != 0:
            raise OfficialAPIError("{}: {}".format(json_data["errcode"], json_data["errmsg"]))

    def _request(self, method, url, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = {
                "access_token": self.access_token,
            }
        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body
        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        response_json = r.json()
        self._check_official_error(response_json)
        return response_json

    def _get(self, url, **kwargs):
        return self._request(
            method="get",
            url=url,
            **kwargs
        )

    def _post(self, url, **kwargs):
        return self._request(
            method="post",
            url=url,
            **kwargs
        )

    def _transcoding(self, data):
        if not data:
            return data
    	result = None
        if type(data) == unicode:
            result = data
        elif type(data) == str:
            result = data.decode('utf-8')
        else:
            raise ParseError()
        return result

