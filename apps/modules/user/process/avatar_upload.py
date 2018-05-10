# -*-coding:utf-8-*-
import base64
import json

import os
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.configs.sys_config import APPS_PATH
from apps.modules.user.process.user_profile_process import delete_user_info_cache
from apps.utils.image.image import ImageCompression
from apps.utils.upload.file_up import file_up, file_del, fileup_base_64
from apps.app import mdb_user
from apps.core.utils.get_config import get_config
from apps.utils.upload.get_filepath import get_file_url

__author__ = "Allen Woo"

def avatar_upload():
    '''
    头像上传
    :return:
    '''
    result = None
    imgfile_base = request.argget.all("imgfile_base")
    if imgfile_base:
        result = fileup_base_64(uploaded_files = [imgfile_base], prefix="user_avatar/")
    else:
        file = request.files['imgfile']
        if file:
            tailoring = request.argget.all('tailoring')
            if tailoring:
                if not isinstance(tailoring, dict):
                    tailoring = json.loads(tailoring)
                for k in ["width", "height", "x", "y", "rotate"]:
                    tailoring.setdefault(k, 0)
            result = file_up(uploaded_files=[file], prefix="user_avatar/", tailoring=tailoring)

    data = {}
    if result:
        result = result[0]
        user = mdb_user.db.user.find_one({"_id":current_user.id})
        if user:
            if result["key"] != user['avatar_url']["key"]:
                # 当使用了不同的名字删除老的头像
                file_del(user['avatar_url'])

            update_data = {
                "avatar_url" : result
            }
            r = mdb_user.db.user.update_one({"_id":current_user.id}, {"$set":update_data})
            if not r.matched_count:
                data = {'msg':gettext("Save failed"), 'msg_type':"w", "http_status":400}
            else:
                if result["type"] == "local":
                    # 如果保存再本地的话, 保存为一定尺寸大小
                    path = "{}{}".format(APPS_PATH, get_file_url(result))
                    imgcp = ImageCompression(path, path)
                    ava_size = get_config("account", "USER_AVATAR_SIZE")
                    imgcp.custom_pixels(ava_size[0], ava_size[1])
                data = {'msg':gettext("Save successfully"), 'msg_type':"s", "http_status":201}
    if not data:
        data = {'msg':gettext("Upload failed"), 'msg_type':"w", "http_status":400}

    # 清理user信息数据缓存
    delete_user_info_cache(user_id=current_user.str_id)
    return data
