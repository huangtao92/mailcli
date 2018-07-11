# -*- coding: UTF-8 -*-
# mailcli 的异常


__all__ = ['MailLoginError', 'PostError', 'HTTPResponseJSONError', 'DatabaseError',
           'ConfigError', 'MailSendError', 'IMAPOperationError', 'ParseError']


from imapclient.exceptions import LoginError


MailLoginError = LoginError


class MailSendError(Exception):
    pass


class IMAPOperationError(Exception):
    pass


class PostError(Exception):
    pass


class HTTPResponseJSONError(Exception):
    pass


class DatabaseError(Exception):
    pass


class ConfigError(Exception):
    pass


class ParseError(Exception):
    pass
