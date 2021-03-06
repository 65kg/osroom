# -*-coding:utf-8-*-
from gettext import gettext

import time

from apps.app import mdb_sys
from apps.core.plug_in.manager import plugin_manager

__author__ = "Allen Woo"

def send_mobile_msg(numbers, content):
    '''
    短信发送
    :param numbers:数组
    :param content:
    :return:
    '''

    # 检测插件
    data = plugin_manager.call_plug(hook_name="send_msg",
                                    to_numbers=numbers,
                                    content=content)
    if data == "__no_plugin__":
        msg = gettext("There is no plug-in for sending SMS messages to mobile phones,"
                      " please install the relevant plug-in")
        status = "abnormal"
        result = (False, msg)

    elif not data:
        status = "abnormal"
        result = (False, gettext("Failed to send"))

    else:
        status = "normal"
        result = (True, gettext("SMS sent successfully"))

    log = {
        "type": "sms",
        "error_info": msg,
        'status': status,
        'subject': "",
        'from': "",
        'to': numbers,
        'date': time.time(),
        'body': content,
        'html': "",
        'msgid': None,
        'time': time.time()
    }
    mdb_sys.db.sys_message.insert_one(log)

    return result




