# -*- coding: UTF-8 -*-
# 解析RFC822格式的邮件内容


import json
import base64
from email import message_from_string
from .error import ParseError


class RFC822Parser(object):
    def __init__(self, string):
        self._message = message_from_string(string)

    def get_attachments(self):
        """返回附件的附件名和附件内容，每个附件以字典存储 {附件名： 附件内容二进制bytes}
        :return:  dict
        """
        attachments = {}
        for i in self._message.walk():
            if i.get_content_disposition() == 'attachment':
                attachments.update({i.get_filename(): base64.b64decode(i.get_payload())})
        return attachments


def parse_attachment_bytes(attach_bytes):
    """解析邮件附件的bytes，返回list， list里的元素为dict
    :param attach_bytes: 邮件附件的bytes
    :return : list , and its item is dict"""
    try:
        attach_str = attach_bytes.decode('utf-8')
    except UnicodeDecodeError as err:
        raise ParseError(err)
    data_list = []
    for i in attach_str.split('\n'):
        i = i.strip()
        if not i:
            # 略过空行
            continue
        try:
            json_dict = json.loads(i)
        except Exception as err:
            # 一个附件文件中有一行解析错误，则整个附件视为处理失败
            raise ParseError("Parse bytes to JSON error: {err}".format(err=err))
        if isinstance(json_dict, dict) and (len(json_dict) == 1):
            data_list.append(json_dict)
        else:
            raise ParseError("Object from parsing string is not a dict or length not equal with one.")
    return data_list
