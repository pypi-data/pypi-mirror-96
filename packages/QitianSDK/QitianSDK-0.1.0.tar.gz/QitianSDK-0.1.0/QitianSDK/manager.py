import requests
from SmartDjango import E, Analyse, P, PDict, Hc, BaseError


@E.register(id_processor=E.idp_cls_prefix())
class QitianError:
    QITIAN_GET_USER_INFO_FAIL = E("齐天簿获取用户信息失败", hc=Hc.InternalServerError)
    QITIAN_GET_USER_PHONE_FAIL = E("齐天簿获取用户手机号失败", hc=Hc.InternalServerError)
    QITIAN_AUTH_FAIL = E("齐天簿身份认证失败", hc=Hc.InternalServerError)
    QITIAN_REQ_FAIL = E("齐天簿请求{0}失败", hc=Hc.InternalServerError)


class QitianManager:
    QITIAN_HOST = 'https://ssoapi.6-79.cn'
    GET_TOKEN_URL = '%s/api/oauth/token' % QITIAN_HOST
    GET_USER_INFO_URL = '%s/api/user/' % QITIAN_HOST
    GET_USER_PHONE_URL = '%s/api/user/phone' % QITIAN_HOST

    def __init__(self, app_id, app_secret, timeout = 3):
        self.app_id = app_id
        self.app_secret = app_secret
        self.timeout = timeout

    def set_timeout(self, timeout):
        self.timeout = timeout

    @Analyse.p(PDict(name='res').set_fields('code', 'msg', P('body').null()))
    def _res_checker(self, res, error: E):
        if res['code'] != BaseError.OK.eid:
            error.append_message = res['msg']
            raise error
        return res['body']

    def _req_extractor(self, req: requests.Response, error: E):
        if req.status_code != requests.codes.ok:
            raise error
        try:
            res = req.json()
        except Exception as err:
            raise error(debug_message=err)

        return self._res_checker(res, error)

    def get_token(self, code):
        req = requests.post(self.GET_TOKEN_URL, json=dict(
            code=code,
            app_secret=self.app_secret,
        ), timeout=self.timeout)

        return self._req_extractor(req, QitianError.QITIAN_REQ_FAIL('身份认证'))

    def get_user_info(self, token):
        req = requests.get(self.GET_USER_INFO_URL, headers=dict(
            token=token,
        ), timeout=self.timeout)

        return self._req_extractor(req, QitianError.QITIAN_REQ_FAIL('用户信息'))

    def get_user_phone(self, token):
        req = requests.get(self.GET_USER_PHONE_URL, headers=dict(
            token=token,
        ), timeout=self.timeout)

        return self._req_extractor(req, QitianError.QITIAN_REQ_FAIL('用户手机号'))
