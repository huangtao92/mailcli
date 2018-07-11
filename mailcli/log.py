# -*- coding: UTF-8 -*-
# mailcli日志


__all__ = ['logger']


import logging


_LOG_FORMAT = '[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s'
_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
_LOG_FILE = 'mailcli.log'


def _get_logger():
    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)
    filehandler = logging.FileHandler(filename=_LOG_FILE, mode='a', encoding='utf-8')
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(formatter)
    log = logging.getLogger('mailcli')
    log.addHandler(filehandler)
    log.setLevel(logging.DEBUG)
    return log


logger = _get_logger()
