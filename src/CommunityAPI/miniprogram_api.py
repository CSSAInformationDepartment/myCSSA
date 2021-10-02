"""
这个文件包含了小程序相关的API
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from time import time
import requests
from django.conf import settings
import logging
import textwrap

from .models import WxMiniProgramData

logger = logging.getLogger(__name__)

# 获取 access token 的过程每天只能调用2000次。所以必须把它缓存起来。

def get_access_token() -> Optional[str]:
    """
    Return access token of mini program.

    It cached the token to be used later.

    If acquiring failed, return None.
    """

    try:
        data: WxMiniProgramData = WxMiniProgramData.objects \
            .get(type=WxMiniProgramData.Type.ACCESS_TOKEN)
        if data.access_token['exp'] >= time():
            # expired
            raise WxMiniProgramData.DoesNotExist()
        return data.access_token['token']

    except WxMiniProgramData.DoesNotExist:
        id = settings.MINIPROGRAM_APPID
        secret = settings.MINIPROGRAM_SECRET

        if not id or not secret:
            logger.warning('小程序 APPID 或 SECRET 不存在，无法获取 access_token')
            return None

        ret: Dict[str, Any] = requests.get('https://api.weixin.qq.com/cgi-bin/token', params={
            'grant_type': 'client_credential',
            'appid': id,
            'secret': secret,
        }).json()

        if 'errcode' in ret:
            logger.warning('获取 access token 出错，code: %s, msg: %s', ret['errcode'], ret['errmsg'])
            return None

        token = ret['access_token']
        exp = int(ret['expires_in']) + int(time())
        WxMiniProgramData.objects.update_or_create(
            type=WxMiniProgramData.Type.ACCESS_TOKEN,
            data={'token': token, 'exp': exp})

        return token

def is_text_invalid(openid: str, text: str, title: Optional[str]=None):
    """
    使用微信API检测文本是否合法。

    如果不合法，返回True；如果合法，返回False；如果API调用出错，返回 None。

    可以用如下方式调用本函数：
    ```
    if is_text_invalid(openid, text, title=title):
        # 处理不合法的情况
        return

    # 正常业务逻辑
    ```
    """

    # 小程序检测的字数上限
    MAX_CONTENT_LEN = 2500

    token = get_access_token()
    if not token:
        logger.warning('无法获取token，文本检测中断')
        return

    text_list = textwrap.wrap(text, MAX_CONTENT_LEN)

    for x in text_list:
        # api doc: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/sec-check/security.msgSecCheck.html
        res = requests.post('https://api.weixin.qq.com/wxa/msg_sec_check', params={'access_token': token},
            data={
                'version': 2,
                'openid': openid,
                'scene': 3, # 场景固定为论坛
                'content': x,
                'title': title,
            }).json()
        title = None # after first iteration, do not send title anymore

        if 'errcode' in res:
            logger.warning('获取检测结果出错，code: %s, msg: %s', res['errcode'], res['errmsg'])
            return None

        if res['result']['suggest'] == 'risky':
            logger.debug('审查命中，详细信息： %s', res)
            return True

    return False