# -*- coding: UTF-8 -*-
# 邮件内容模板

__all__ = ['MAIL_TO_MAILCLI_DEVELOPER',
           'MAIL_TO_SENDER_ERROR',
           'MAIL_TO_SENDER_SUCCESS',
           'MAIL_TO_SENDER_LOSE_ATTACH',
           'MAIL_TO_SERVER_DEVELOPER']


MAIL_TO_SENDER_ERROR = {'subject': 'tlcient:文件不合法',
                        'message': ('<html><body aria-readonly="false">'
                                    '<span style="font-size:16px">'
                                    '您好：'
                                    '<br />'
                                    '<br />'
                                    '<p>您邮件中上传的附件 {attachments} 不合法，请确认是否被人为修改或上传了错误的文件,再重新发送。</p>'
                                    '<p>若有疑问请联系: <em>{emaddr}</em> 处理。</p>'
                                    '</span>'
                                    '<br />'
                                    '<br />'
                                    '<br />'
                                    '<em>此消息系统自动发送，请勿回复</em>'
                                    '</body></html>')}

MAIL_TO_SENDER_LOSE_ATTACH = {'subject': 'tclient: 邮件没有附件',
                              'message': '<html>'
                                         '<body aria-readonly="false">'
                                         '<span style="font-size:16px">'
                                         '您好：'
                                         '<p>您发送的邮件没有附件</p>'
                                         '</span>'
                                         '<br />'
                                         '<br />'
                                         '<br />'
                                         '<em>此消息系统自动发送，请勿回复</em>'
                                         '</body>'
                                         '</html>'}

MAIL_TO_SENDER_SUCCESS = {'subject': 'tclient:文件上传成功',
                          'message': ('<html><body aria-readonly="false">'
                                      '<span style="font-size:16px">'
                                      '您好：'
                                      '<br />'
                                      '<br />'
                                      '<p>客户 {customs} 数据上传成功。</p>'
                                      '<p>感谢您的支持。</p>'
                                      '</span>'
                                      '<br />'
                                      '<br />'
                                      '<br />'
                                      '<em>此消息系统自动发送，请勿回复</em>'
                                      '</html>')}

MAIL_TO_MAILCLI_DEVELOPER = {'subject': 'mailcli:运行出错,请及时处理',
                             'message': 'Error: {err}'}

MAIL_TO_SERVER_DEVELOPER = {'subject': 'tclient:上传数据返回错误,请及时处理',
                            'message': '<html><body>{err}</body></html>'}
