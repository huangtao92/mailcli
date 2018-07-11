# -*- coding: UTF-8 -*-
# 检索并下载关于tclient的邮件


from imapclient import IMAPClient
from .error import MailLoginError, IMAPOperationError


class MailPuller(object):
    def __init__(self, host, user, password):
        self._host = host
        self._user = user
        self._password = password
        self._server = IMAPClient(host, ssl=False)

    def login(self):
        try:
            self._server.login(self._user, self._password)
        except MailLoginError as err:
            raise MailLoginError('imapclient login error.Login info: host:{host}, user=:{user}.'
                                 ' Message: {err}'.format(host=self._host, user=self._user, err=err))

    def pull_msgids(self, subject):
        """返回一个字典，字典key为messageid, value为发件人.若没有获取到则为空字典{}"""
        try:
            self._server.select_folder('INBOX')
            msgids = self._server.search(['UNDELETED', 'SUBJECT', subject])
            envelopes = self._server.fetch(msgids, ['ENVELOPE'])
        except Exception as err:
            raise IMAPOperationError("MailPuller.pull_msgids() run error. Message: {err}".format(err=err))
        msgids_with_sender = {}
        for i in msgids:
            msgids_with_sender.update({i: (envelopes[i][b'ENVELOPE'].sender[0].mailbox.decode('utf-8') + '@' +
                                           envelopes[i][b'ENVELOPE'].sender[0].host.decode('utf-8'))})
        return msgids_with_sender

    def download(self, msgid):
        """返回 RFC822 格式的 str

        :param msgid: int
        :return: str
        下载(fetch)后，邮件被标记为 SEEN"""
        try:
            return self._server.fetch(msgid, ['RFC822'])[msgid][b'RFC822'].decode('utf-8')
        except Exception as err:
            raise IMAPOperationError("MailPuller.download() run error. Message: {err}".format(err=err))

    def delete(self, msgids):
        """将邮件标记为 DELETED, 并未真正删除

        :param msgids: int or list that item is int"""
        self._server.delete_messages(msgids)

    def logout(self):
        try:
            self._server.logout()
        except Exception:
            pass

    def __del__(self):
        # 对象被回收时，自动关闭邮箱服务器的链接
        try:
            self._server.logout()
        except Exception:
            pass
