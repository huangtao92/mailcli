# -*- coding: UTF-8 -*-
# 执行SQL查询语句，查询客户的名称


import pymysql
from .error import DatabaseError


query_custom_sql = "SELECT cust_name FROM tcloud.customers_info WHERE t100reg_id=%s"


class Query(object):
    def __init__(self, host, user, password, dbname='tcloud'):
        try:
            self._conn = pymysql.connect(host=host,
                                         user=user,
                                         password=password,
                                         db=dbname,
                                         charset='utf8',
                                         cursorclass=pymysql.cursors.DictCursor)
        except Exception as err:
            raise DatabaseError('Failed to login dbserver. Message: {}'.format(err))

    def query(self, sql, sql_args=None):
        """查询结果是一个列表，列表中的元素为字典，key为列名，value为查询结果

        :param sql: SQL语句字符串
        :param sql_args: SQL语句的条件，为tuple，list or dict"""
        result = []
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(sql, sql_args)
                result.extend(cursor.fetchall())
        except Exception as err:
            raise DatabaseError('Execute SQL error.SQL: {sql}, sql_args:{sql_args}. Message: {err}'.format(
                sql=sql, sql_args=sql_args, err=err))
        # 查询结果是[{**: **}]格式
        return result[0]['cust_name']

    def __del__(self):
        # 对象在使用完毕后被自动回收内存或者程序正常关闭时，主动关闭数据库连接
        if hasattr(self, '_conn'):
            try:
                self._conn.close()
            except Exception:
                pass
            del self._conn
