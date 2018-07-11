# -*- coding: UTF-8 -*-
# 配置文件相关的操作，包括创建配置文件、配置文件读取、配置文件内容检验


import re
from collections import namedtuple
from configparser import ConfigParser
from .db import Query
from .error import MailLoginError, DatabaseError
from .sender import MailSender


CONFIG_FILE = 'mailcli.conf'


def create_configfile():
    config = ConfigParser(allow_no_value=True)
    config.add_section('puller')
    # config.set 添加配置注释
    config.set('puller', '# 抓取邮件的间隔时间，单位分钟')
    config['puller']['interval'] = '15'
    config.set('puller', '# 根据邮件主题(Subject) 抓取邮件')
    config['puller']['subject'] = 'tcl'

    config.add_section('mailserver')
    config.set('mailserver', '# mailcli 抓取邮件、发送邮件使用的邮箱服务器配置信息')
    config.set('mailserver', '# 邮箱服务器的 IP 地址或域名')
    config['mailserver']['host'] = ''
    config.set('mailserver', '# 邮箱账户，要包含@domain_name的全称')
    config['mailserver']['user'] = ''
    config.set('mailserver', '# 邮箱密码')
    config['mailserver']['password'] = ''

    config.add_section('mailto')
    config.set('mailto', '# mailcli 发送邮件的接收者')
    config.set('mailto', '# tclient 服务端维护人的邮箱地址')
    config['mailto']['tclserv_developer'] = ''
    config.set('mailto', '# mailcli 维护人的邮箱地址')
    config['mailto']['mailcli_developer'] = ''

    config.add_section('database')
    config.set('database', '# 服务云的数据库连线信息')
    config['database']['host'] = ''
    config['database']['dbname'] = ''
    config['database']['user'] = ''
    config['database']['password'] = ''

    try:
        with open(CONFIG_FILE, 'wt') as f:
            config.write(f)
    except (OSError, IOError) as err:
        raise SystemExit("Can't create a config file '{}'. Error: {}".format(CONFIG_FILE, err))


class _ExistChecker(object):
    def __init__(self, config_obj, section, params):
        """检查配置内容
        :param config_obj: instance of the class configparser.ConfigParser
        :param section: configuration section
        :param params: configuration parameters, is a list"""
        self._config = config_obj
        self.section = section
        self.params = tuple(params)

    def check(self):
        """检查参数是否存在，是否为空。若参数存在也不为空，则返回 True 和 [], 否则返回 False 和 错误信息组成的 list"""
        message = []
        m_h = "Section '{section}': ".format(section=self.section)
        if self.section in self._config:
            for p in self.params:
                if p in self._config[self.section]:
                    if self._config[self.section][p].strip():
                        # 参数值不为空则不作处理
                        pass
                    else:
                        message.append((m_h+"'{param}' is empty").format(param=p))
                else:
                    message.append((m_h+"'{param}' not found.").format(param=p))
        else:
            message.append((m_h+"not found in {configfile}.").format(configfile=CONFIG_FILE))
        if message:
            return False, message
        else:
            return True, []


class Configuration(object):
    def __init__(self, config_file=CONFIG_FILE):
        self._config = ConfigParser()
        try:
            self._config.read(config_file)
        except (OSError, IOError) as err:
            raise SystemExit('Failed to read configuration file {}. Error: {}'.format(config_file, err))
        self.struct = {'puller': ['interval', 'subject'],
                       'mailserver': ['host', 'user', 'password'],
                       'mailto': ['tclserv_developer', 'mailcli_developer'],
                       'database': ['host', 'dbname', 'user', 'password']}
        # 以下四个属性，会在配置参数都检查通过时赋值，值类型为 namedtuple
        self.puller = None
        self.mailserver = None
        self.mailto = None
        self.database = None

    @staticmethod
    def is_mailaddress(mailadress):
        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mailadress):
            return True
        else:
            return False

    @staticmethod
    def is_ipdomain(ipdomain):
        if (re.match(r"^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$", ipdomain) or
            re.match(("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
                      "{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"), ipdomain)):
            return True
        else:
            return False

    def get_puller(self):
        message = []
        section = 'puller'
        params = self.struct[section]
        puller = namedtuple('Puller', params)
        try:
            self.puller = puller(self._config.getint(section, params[0]), self._config[section][params[1]])
        except ValueError:
            message.append("Section '{section}': '{param} = {v}', '{v}' is not int.".format(
                section=section, param=params[0], v=self._config.get(section, params[0])))
        return message

    def get_mailserver(self):
        message = []
        section = 'mailserver'
        # 检查host是否为合法IP或域名，user是否为合法邮箱
        m_h = "Section '{section}': ".format(section=section)
        m = m_h + "'{param} = {v}', '{v}' {msg}."
        params = self.struct[section]
        mail_tuple = namedtuple('MailServer', params)
        mailserver = mail_tuple(**dict(self._config[section]))
        if not self.is_ipdomain(mailserver.host):
            message.append(m.format(param='host', v=mailserver.host, msg="is a illegal IP or Domain"))
        if not self.is_mailaddress(mailserver.user):
            message.append(m.format(param='user', v=mailserver.user, msg="is a illegal email address"))
        if message:
            return message

        # 检查根据配置的邮箱地址、用户、密码是否可以成功登录
        try:
            MailSender(mailserver.host, mailserver.user, mailserver.password)
        except MailLoginError as err:
            message.append((m_h+"Can't login to mailserver. ErrorMessage: {err}").format(err=err))

        if not message:
            self.mailserver = mailserver
        return message

    def get_database(self):
        message = []
        section = 'database'
        # 检查host是否是合法的IP或域名
        m_h = "Section '{section}': ".format(section=section)
        m = m_h + "'{param} = {v}', '{v}' {msg}."
        params = self.struct[section]
        db_tuple = namedtuple('Database', params)
        database = db_tuple(**dict(self._config[section]))
        if not self.is_ipdomain(database.host):
            message.append(m.format(param='host', v=database.host, msg="is a illegal Ip or Domain"))
        if message:
            return message

        try:
            Query(database.host, database.user, database.password, database.dbname)
        except DatabaseError as err:
            message.append((m_h+"Can't login to DB Server. ErrorMessage: {err}").format(err=err))

        if not message:
            self.database = database
        return message

    def get_mailto(self):
        message = []
        section = 'mailto'
        m_h = "Section '{section}': ".format(section=section)
        m = m_h + "'{param} = {v}', '{v}' {msg}."
        mailto = dict(self._config[section])
        for k in mailto.keys():
            v = mailto[k]
            if self.is_mailaddress(v):
                continue
            else:
                message.append(m.format(param=k, v=v, msg="is a illegal email address"))

        if not message:
            params = self.struct[section]
            email = namedtuple('Email', params)
            self.mailto = email(**dict(self._config[section]))
        return message

    def _precheck(self):
        # 检查通过返回 True， 失败返回 False
        message = []
        for section in self.struct.keys():
            params = self.struct[section]
            checker = _ExistChecker(self._config, section, params)
            ret, errmsg = checker.check()
            if not ret:
                message.extend(errmsg)

        if not message:
            return True, message
        else:
            return False, message

    def check_all(self):
        print("Starting check configuration...")
        # 预先检查是否有遗漏的配置
        ret, pre_check_message = self._precheck()
        if not ret:
            print("Checking don't passed:")
            for i in pre_check_message:
                print(i)
            raise SystemExit("\nPlease check the configuration in '{configfile}'".format(configfile=CONFIG_FILE))

        # 检查配置是否可用
        after_check_message = (self.get_database() +
                               self.get_mailserver() +
                               self.get_mailto() +
                               self.get_puller())
        if after_check_message:
            print("Checking don't passed:")
            for i in after_check_message:
                print(i)
            raise SystemExit("\nPlease check the configuration in '{configfile}'".format(configfile=CONFIG_FILE))
        else:
            print("Checking passed")
