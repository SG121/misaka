# -*- coding: utf-8 -*-

"""
定时登录青龙
解决脚本因内部青龙token失效而运行失败问题。有些脚本使用了内部的token，而token有时效性，长时间不登录账号以致token失效，导致脚本运行失败。

变量名：QLDLCK
格式：账号&密码 使用&拼接



cron: 0 15 */2 * *
new Env('定时登录青龙');
"""
import requests
import json, os
import time
from sys import stdout

# 修改print方法 避免某些环境下python执行print 不会去刷新缓存区导致信息第一时间不及时输出
def print_now(content):
    print(content)
    stdout.flush()

# 从环境变量获取青龙账号密码
ck = os.getenv("QLDLCK", "")
if ck is None:
    ck = ""
if ck == "":
    print_now("未设置CK，退出")
    os.sys.exit(1)

username = ck.split("&")[0]
password = ck.split("&")[1]
ql_url = 'http://localhost:5600'
params = {
    't': int(time.time() * 1000)
}
data = {
    'username': username,
    'password': password
}
res = requests.post(ql_url + '/api/user/login', params=params, json=data)
j_data = res.json()
if j_data['code'] == 200:
    print_now(j_data['data'])
