# -*- coding: UTF-8 -*-
# SMTP客户端， 发送邮件


import yagmail
from .error import MailLoginError, MailSendError


class MailSender(object):
    def __init__(self, host, user, password):
        self._host = host
        # user 应该是带@domain-name的邮箱帐号全写
        self._user = user
        self._password = password
        try:
            self._sender = yagmail.SMTP(host=host, user=user, password=password)
        except Exception as err:
            raise MailLoginError('yagmail login error. Login info: host:{host}, user:{user}. '
                                 'Message: {err}'.format(host=self._host, user=self._user, err=err))

    def login(self):
        self._sender.login()

    def send(self, to, subject, contents, cc=None, bcc=None, attachments=None):
        # yagmail 0.11.214 版本会在每次调用 send() 方法前无条件调用 login() 方法，导致异常
        if self._sender.is_closed is False:
            self._sender.close()
        try:
            self._sender.send(to=to, subject=subject, contents=contents, cc=cc, bcc=bcc, attachments=attachments)
        except Exception as err:
            raise MailSendError("yagmail send email to '{to}' failed, subject: {subject}. Message: {err}".format(
                to=to, subject=subject, err=err))

    def __del__(self):
        if hasattr(self, '_sender'):
            try:
                self._sender.close()
            except Exception:
                pass
