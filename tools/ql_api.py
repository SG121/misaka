import json, os
import time
from sys import stdout
from datetime import datetime

import requests,re

ql_auth_path = '/ql/data/config/auth.json'
ql_config_path = '/ql/data/config/config.sh'
#判断环境变量
flag = 'new'
if not os.path.exists(ql_auth_path):
    ql_auth_path = '/ql/config/auth.json'
    ql_config_path = '/ql/config/config.sh'
    if not os.path.exists(ql_config_path):
        ql_config_path = '/ql/config/config.js'
    flag = 'old'
# ql_auth_path = r'D:\Docker\ql\config\auth.json'
ql_url = 'http://localhost:5600'


def __get_token() -> str or None:
    with open(ql_auth_path, 'r', encoding='utf-8') as f:
        j_data = json.load(f)
    return j_data.get('token')


def __get__headers() -> dict:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8',
        'Authorization': 'Bearer ' + __get_token()
    }
    return headers




# 封装读取环境变量的方法(读取环境变量的整个CK)
def get_cookie_all(key, default="", output=True):
    def no_read():
        if output:
            print_now(f"未填写环境变量 {key} 请添加")
        return default
    return get_cookie_all_data(key) if get_cookie_all_data(key) else no_read()


#获取整个ck，包括备注
def get_cookie_all_data(name):
    ck_list = []
    remarks_list = []
    cookie = None
    cookies = get_config_and_envs(name)
    for ck in cookies:
        data_temp = {}
        if ck["name"] != name:
            continue
        if ck.get('status') == 0:
            # ck_list.append(ck.get('value'))
            # 直接添加CK
            ck_list.append(ck)
    return ck_list



# 封装读取环境变量的方法(只读取环境变量的value)
def get_cookie(key, default="", output=True):
    def no_read():
        if output:
            print_now(f"未填写环境变量 {key} 请添加")
        return default
    return get_cookie_data(key) if get_cookie_data(key) else no_read()

#获取ck的value
def get_cookie_data(name):
    ck_list = []
    cookie = None
    cookies = get_config_and_envs(name)
    for ck in cookies:
        if ck["name"] != name:
            continue
        if ck.get('status') == 0:
            ck_list.append(ck.get('value'))
    return ck_list 

# 修改print方法 避免某些环境下python执行print 不会去刷新缓存区导致信息第一时间不及时输出
def print_now(content):
    print(content)
    stdout.flush()


# 查询环境变量
def get_envs(name: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    if name is not None:
        params['searchValue'] = name
    res = requests.get(ql_url + '/api/envs', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        return j_data['data']
    return []


# 查询环境变量+config.sh变量
def get_config_and_envs(name: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    #返回的数据data
    data = []
    if name is not None:
        params['searchValue'] = name
    res = requests.get(ql_url + '/api/envs', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        data = j_data['data']
    with open(ql_config_path, 'r', encoding='utf-8') as f:
        while  True:
            # Get next line from file
            line  =  f.readline()
            # If line is empty then end of file reached
            if  not  line  :
                break;
            #print(line.strip())
            exportinfo = line.strip().replace("\"","").replace("\'","")
            #去除注释#行
            rm_str_list = re.findall(r'^#(.+?)', exportinfo,re.DOTALL)
            #print('rm_str_list数据：{}'.format(rm_str_list))
            exportinfolist = []
            if len(rm_str_list) == 1:
                exportinfo = ""
            #list_all = re.findall(r'export[ ](.+?)', exportinfo,re.DOTALL)
            #print('exportinfo数据：{}'.format(exportinfo))
            #以export分隔，字符前面新增标记作为数组0，数组1为后面需要的数据
            list_all = ("标记"+exportinfo.replace(" ","").replace(" ","")).split("export")
            #print('list_all数据：{}'.format(list_all))
            if len(list_all) > 1:
                #以=分割，查找需要的环境名字
                tmp = list_all[1].split("=")
                if len(tmp) > 1:
                    
                    info = tmp[0]
                    if name in info:
                        #print('需要查询的环境数据：{}'.format(tmp))
                        data_tmp = []
                        data_json = {
                            'id': None,
                            'value': tmp[1],
                            'status': 0,
                            'name': name,
                            'remarks': "",
                            'position': None,
                            'timestamp': int(time.time()*1000),
                            'created': int(time.time()*1000)
                        }
                        if flag == 'old':
                            data_json = {
                            '_id': None,
                            'value': tmp[1],
                            'status': 0,
                            'name': name,
                            'remarks': "",
                            'position': None,
                            'timestamp': int(time.time()*1000),
                            'created': int(time.time()*1000)
                            }
                        #print('需要的数据：{}'.format(data_json))
                        data.append(data_json)
        #print('第二次配置数据：{}'.format(data))
    return data


# 新增环境变量
def post_envs(name: str, value: str, remarks: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    data = [{
        'name': name,
        'value': value
    }]
    if remarks is not None:
        data[0]['remarks'] = remarks
    res = requests.post(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return j_data['data']
    return []


# 修改环境变量(2.11.x版本有问题，属于旧版青龙，但是id属于新版本)
def put_envs(_id: str, name: str, value: str, remarks: str = None) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    
    data = {
        'name': name,
        'value': value,
        'id': _id
    }
    if flag == 'old':
       data = {
        'name': name,
        'value': value,
        '_id': _id
        } 
    
    if remarks is not None:
        data['remarks'] = remarks
    res = requests.put(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 修改环境变量1，青龙2.11.0以下版本（不含2.11.0）
def put_envs_old(_id: str, name: str, value: str, remarks: str = None) -> bool:
    params = {
        't': int(time.time() * 1000)
    }

    data = {
        'name': name,
        'value': value,
        '_id': _id
    }

    if remarks is not None:
        data['remarks'] = remarks
    res = requests.put(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False


# 修改环境变量2，青龙2.11.0以上版本（含2.11.0）
def put_envs_new(_id: int, name: str, value: str, remarks: str = None) -> bool:
    params = {
        't': int(time.time() * 1000)
    }

    data = {
        'name': name,
        'value': value,
        'id': _id
    }

    if remarks is not None:
        data['remarks'] = remarks
    res = requests.put(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False


# 禁用环境变量
def disable_env(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/envs/disable', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False


# 启用环境变量
def enable_env(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/envs/enable', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False



# 获取所有的定时任务详情
def get_crons(name: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    if name is not None:
        params['searchValue'] = name
    res = requests.get(ql_url + '/api/crons', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        if flag == 'old':
            return j_data['data']
        else:
            return j_data['data']['data']
    return []

# 获取指定定时任务详情
def get_crons_by_id(_id: str) -> list:
    # 统一返回队列类型
    result = []
    params = {
        't': int(time.time() * 1000)
    }
    res = requests.get(ql_url + f'/api/crons/{_id}', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        return result.append(j_data['data'])
    return []


# 新增任务
def post_crons( name: str, labels: str, command: str, schedule: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = {
        'labels': labels,
        'command': command,
        'schedule': schedule,
        'name': name
    }
    if flag == 'old':
       data = {
        'labels': labels,
        'command': command,
        'schedule': schedule,
        'name': name
        } 
    res = requests.post(ql_url + '/api/crons', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 更新任务
def put_crons(_id: str, name: str, labels: str, command: str, schedule: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = {
        'labels': labels,
        'command': command,
        'schedule': schedule,
        'name': name,
        'id': _id
    }
    if flag == 'old':
       data = {
        'labels': labels,
        'command': command,
        'schedule': schedule,
        'name': name,
        '_id': _id
        } 
    res = requests.put(ql_url + '/api/crons', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 禁用任务
def disable_crons(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/crons/disable', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False


# 启用任务
def enable_crons(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/crons/enable', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 删除任务
def delete_crons(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.delete(ql_url + '/api/crons', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 运行任务
def run_crons(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/crons/run', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 停止任务
def stop_crons(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/crons/stop', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 获取指定任务的日志详情
def get_crons_log(_id: str) -> str:
    params = {
        't': int(time.time() * 1000)
    }
    res = requests.get(ql_url + f'/api/crons/{_id}/log', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        return j_data['data']
    return ""

# 随机生成比当前时间小的定时任务规则
def generate_past_cron():
    现在 = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    # 处理无法生成的情况（当前时间为00:00）
    if current_hour == 0 and current_minute == 0:
        return "16 23 * * *"  # 默认返回前一天23:16
    
    # 计算当前时间的总分钟数
    total_minutes = current_hour * 60 + current_minute
    
    # 随机生成过去的时间点（0到总分钟数-1之间）
    random_minutes = random.randint(0, total_minutes - 1)
    random_hour = random_minutes // 60
    random_minute = random_minutes % 60

    current_time = datetime.now().strftime("%H:%M")
    print(f"当前时间: {current_time}")
    print(f"生成新的Cron表达式: {random_minute} {random_hour} * * *")
    print(f"含义: 每天 {random_hour}:{random_minute:02d} 执行")

    # 格式化为cron表达式
    return f"{random_minute} {random_hour} * * *"


# 根据当前文件随机改变定时任务时间
def random_time():
    print_now("执行更改定时任务表达式")
    cron_details = None
    script_path = os.path.abspath(__file__)  # 转为绝对路径
    # print_now(f"脚本绝对路径: {script_path}")    # 示例脚本绝对路径: /ql/data/scripts/yuanter_hw/akilecloud_checkin.py
    # script_name = os.path.basename(script_path)     # 文件名: main.py
    # 获取所有任务的脚本路径
    crons_data = get_crons()
    
    for i in range(len(crons_data)): 
        
        script_path_temp = crons_data[i].get("command").split(" ")[1]
        if script_path_temp in script_path:
            # 获取当前的任务详情
            cron_details = crons_data[i]
            if cron_details is not None:
                _id = None
                if flag == 'new':
                    _id = cron_details["id"]
                else:
                    _id = cron_details["_id"]
                schedule = generate_past_cron()
                # 修改任务
                if put_crons(_id, cron_details["name"], cron_details["labels"], cron_details["command"], schedule):
                    print_now(f"生成新的定时任务成功。旧表达式：{cron_details['schedule']} ，新的表达式：{schedule}")
            # 结束
            break
    
