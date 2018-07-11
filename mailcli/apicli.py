# -*- coding: UTF-8 -*-
# 将数据上传到tclient的服务端


import requests
from .error import PostError, HTTPResponseJSONError


class API(object):
    BASE_URL = 'http://10.40.40.153/DWGateway/restful/TCPortal/ITclientService'
    DATA_URL = BASE_URL + '/uploaddata'
    LOG_URL = BASE_URL + '/uploadlog'

    def __init__(self, json_dict):
        self.json = json_dict
        if 'logs' in self.json:
            self.url = self.LOG_URL
        elif 'datas' in self.json:
            self.url = self.DATA_URL
        else:
            self.url = ''

    @staticmethod
    def post(url, json_dict):
        try:
            response = requests.post(url, json=json_dict)
        except Exception as err:
            raise PostError('Failed to send a POST HTTP request, url: {url}, json: {json}. Message: {err}'.format(
                url=url, json=json_dict, err=err))
        return response

    def call(self):
        resp = self.post(self.url, self.json)
        if not (resp.ok and resp.json()['response']):
            raise HTTPResponseJSONError('HTTPResponseJSONError: url: {url},json: {json}'.format(
                url=resp.url, json=resp.text))
