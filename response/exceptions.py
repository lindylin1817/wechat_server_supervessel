
# -*- coding: utf-8 -*-
class NeedParamError(Exception):
    pass

class ParseError(Exception):
    pass

class NeedParseError(Exception):
    pass

class OfficialAPIError(Exception):
    pass

class UnOfficialAPIError(Exception):
    pass

class NeedLoginError(UnOfficialAPIError):
    pass

class LoginError(UnOfficialAPIError):
    pass

class LoginVerifyCodeError(LoginError):
    pass
