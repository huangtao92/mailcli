# -*- coding: UTF-8 -*-
# mailcli 处理流的逻辑模块
#
# 抓取邮件
# ||
# 解析邮件附件 ->附件内容合法性检查(每行字符串为json字符串）->不合法发邮件提示寄信人
# ||
# 解析后的json调用 API 上传 ->上传失败通知API维护人和mailcli维护人
# ||
# 查询上传数据的客户名称
# ||
# 邮件提示寄信人和数据运营者


from .apicli import API
from .db import Query, query_custom_sql
from .error import *
from .log import logger
from .parser import RFC822Parser, parse_attachment_bytes
from .pullmail import MailPuller
from .sender import MailSender
from .template import *


class Processer(object):
    def __init__(self, config):
        # config is namedtuple
        try:
            self.puller = MailPuller(config.mailserver.host, config.mailserver.user, config.mailserver.password)
            self.puller.login()
            self.sender = MailSender(config.mailserver.host, config.mailserver.user, config.mailserver.password)
            self.sender.login()
            self.config = config
        except MailLoginError as err:
            logger.error(err)
            raise MailLoginError
        try:
            self.query = Query(self.config.database.host, self.config.database.user,
                               self.config.database.password, self.config.database.dbname)
        except DatabaseError as err:
            self.sendmail(self.config.mailto.mailcli_developer, MAIL_TO_MAILCLI_DEVELOPER['subject'],
                          MAIL_TO_MAILCLI_DEVELOPER['message'].format(err=err))
            self.query = None
            logger.error(err)
        self._success_customs = []

    def sendmail(self, to, subject, contents, attachments=None):
        try:
            self.sender.send(to, subject, contents, attachments)
            logger.info('Send email to {to}, subject: {subject}'.format(to=to, subject=subject))
        except MailSendError as err:
            logger.error(err)

    def process(self):
        try:
            msgids_with_sender = self.puller.pull_msgids(self.config.puller.subject)
        except IMAPOperationError as err:
            logger.error(err)
            # 获取邮件id失败，mailcli运行异常，邮件通知维护者
            self.sendmail(self.config.mailto.mailcli_developer,
                          MAIL_TO_MAILCLI_DEVELOPER['subject'],
                          MAIL_TO_MAILCLI_DEVELOPER['message'].format(err=err))
            return
        self._process_messages(msgids_with_sender)

    def _process_messages(self, msgids_with_sender):
        # imap_err_msg 存储imap处理错误的message
        imap_err_msg = []
        # msg_to_deleted 记录要被标记为 DELETED 的邮件
        msg_to_deleted = []
        for (msgid, emaddr) in msgids_with_sender.items():
            try:
                rfc822_str = self.puller.download(msgid)
            except IMAPOperationError as err:
                imap_err_msg.append(msgid)
                logger.err("Message id: {id}, sender: {emaddr}. {err}".format(id=msgid, emaddr=emaddr, err=err))
                continue
            rfc822 = RFC822Parser(rfc822_str)
            if rfc822.get_attachments():
                ret, err_attachs = self._process_attachments(msgid, emaddr, rfc822.get_attachments())
                # ret 为 True 表示服务端已经正确处理了文件
                if ret:
                    msg_to_deleted.append(msgid)
                    if err_attachs:
                        # 如果有不合法的附件文件，则提示发件人
                        self.sendmail(emaddr, MAIL_TO_SENDER_ERROR['subject'], MAIL_TO_SENDER_ERROR['message'].format(
                            attachments=','.join(err_attachs), emaddr=self.config.mailto.mailcli_developer),
                                      self.config.mailto.mailcli_developer)
                    if self._success_customs:
                        self.sendmail(emaddr, MAIL_TO_SENDER_SUCCESS['subject'], MAIL_TO_SENDER_SUCCESS['message'].
                                      format(customs=','.join(self._success_customs)))
            else:
                # 没有附件，邮件提示寄信人漏寄附件
                self.sendmail(emaddr, MAIL_TO_SENDER_LOSE_ATTACH['subject'], MAIL_TO_SENDER_LOSE_ATTACH['message'])
        if msg_to_deleted:
            self.puller.delete(msg_to_deleted)
        if imap_err_msg:
            self.sendmail(self.config.mailto.mailcli_developer, MAIL_TO_MAILCLI_DEVELOPER['subject'],
                          MAIL_TO_MAILCLI_DEVELOPER['message'].format(err="imap error, message ids: {ids}".format(
                              ids=','.format(imap_err_msg))))

    def _process_attachments(self, msgid, emaddr, atms):
        """返回bool值和列表，布尔值表示该条Message是否需要被标记为DELETED, 列表为内容不合法的文件名"""
        # attch_proc_res 记录处理失败的附件和失败的原因
        # 失败原因:
        #   'file_err': 附件文件不合法
        #   'api_err': 上传API请求出错
        attatch_proc_res = {'file_err': [],
                            'api_err': []}
        # 数据上传成功的客户名称
        self._success_customs = []
        for (f_name, atm_bytes) in atms.items():
            try:
                data_list = parse_attachment_bytes(atm_bytes)
            except ParseError as err:
                attatch_proc_res['file_err'].append(f_name)
                logger.error("Message id: {id}, sender: {emaddr}, attatchment: {atm}. {err}".format(
                    id=msgid, emaddr=emaddr, atm=f_name, err=err))
                continue
            # 记录请求 API 的报错信息
            call_api_err = []
            for data in data_list:
                api = API(data)
                try:
                    api.call()
                except (HTTPResponseJSONError, PostError) as err:
                    call_api_err.append(err)
                    attatch_proc_res['api_err'].append(f_name)
                    logger.error(err)
                    continue
                if 'datas' in data:
                    custom = data['datas']['t100Lic']
                    if self.query:
                        try:
                            custom = self.query.query(query_custom_sql, custom)
                        except DatabaseError as err:
                            self.sendmail(self.config.mailto.mailcli_developer, MAIL_TO_MAILCLI_DEVELOPER['subject'],
                                          MAIL_TO_MAILCLI_DEVELOPER['message'].format(err=err))
                            logger.error(err)
                    self._success_customs.append(custom)
            if call_api_err:
                self.sendmail(self.config.mailto.tclserv_developer, MAIL_TO_SERVER_DEVELOPER['subject'],
                              MAIL_TO_SERVER_DEVELOPER['message'].format(err="<br />".join(call_api_err)))
        if attatch_proc_res['api_err']:
            # 如果有API调用报错，则message不标记为DELETED
            return False, []
        else:
            return True, attatch_proc_res['file_err']
