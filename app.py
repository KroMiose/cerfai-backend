from flask import Flask, redirect, request, session
from flask_cors import CORS
import os
import json
import time
import config
from dataOpts import dataOpt

app = Flask(__name__)
CORS(app, supports_credentials=True)

do = dataOpt()
ip_dict = {}

# 测试服务器连通性接口
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    user_ip = request.remote_addr if request.remote_addr != '127.0.0.1' else request.headers.get('X-Real-IP')
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ping from {user_ip} with data: {reqData}")
    return {'code': 200, 'msg': 'CERF-AI贡献站点运行正常', 'data': reqData, 'from_ip': user_ip}

# 获取类别列表
@app.route('/get_categories', methods=['GET', 'POST'])
def get_categories():
    up_cnt = do.get_run_data()['upload_cnt']
    ct_total = do.get_run_data()['tag_cnt']
    return {'code': 200, 'msg': '获取分类成功', 'data': do.get_categories(), 'up_cnt': up_cnt, 'ct_total': ct_total, 'contributor': do.get_contributor()}

# 获取随机词条
@app.route('/get_random_tag', methods=['GET', 'POST'])
def get_random_tag():
    return {'code': 200, 'msg': '获取随机词条信息成功', 'data': do.get_random_tag()}

# 更新词条内容
@app.route('/update_taginfo', methods=['POST'])
def update_taginfo():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    user_ip = request.remote_addr if request.remote_addr != '127.0.0.1' else request.headers.get('X-Real-IP')
    if user_ip in ip_dict:
        ctime = time.time()
        if ctime - ip_dict[user_ip] < config.ct_submit_delay:
            return {'code': 401, 'msg': f"提交过于频繁，请等待 {int(config.ct_submit_delay - (ctime - ip_dict[user_ip]))} 秒后重试"}

    if do.update_taginfo(reqData,user_ip):
        ip_dict[user_ip] = time.time()
        return {'code': 200, 'msg': '更新成功，感谢您的贡献！'}
    return {'code': 401, 'msg': '上传失败，请检查输入内容是否合法'}

# 搜索词条
@app.route('/search_tags', methods=['GET', 'POST'])
def search_tags():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data = do.search_tags(reqData)
    if data != False:
        return {'code': 200, 'data': data}
    return {'code': 401, 'msg': '参数错误'}

# 获取贡献榜
@app.route('/get_contributor', methods=['GET', 'POST'])
def get_contributor():
    return {'code': 200, 'data': do.get_contributor()}


""" ================================ 管理接口 ================================ """
# 验证授权码
@app.route('/admin/check_access', methods=['POST'])
def check_access():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    try:
        if reqData['token'] == config.access_key:
            return {'code': 200, 'msg': '授权校验成功'}
        return {'code': 401, 'msg': '授权校验失败'}
    except Exception as e:
        return {'code': 401, 'msg': '授权校验失败'}

# 请求重载运行数据接口
@app.route('/admin/reload_rundata', methods=['POST'])
def reload_rundata():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    if do.reload_rundata(reqData):
        return {'code': 200, 'msg': '数据重载成功'}
    else:
        return {'code': 401, 'msg': '重载失败'}

# 获取筛选词条内容
@app.route('/admin/filter_tags', methods=['POST'])
def filter_tags():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data, cnt = do.filter_tags(reqData)
    if data != False:
        return {'code': 200, 'data': data, 'total': cnt}
    return {'code': 500, 'msg': '参数错误'}

# 编辑词条信息
@app.route('/admin/edit_tag', methods=['POST'])
def edit_tag():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data = do.edit_tag(reqData)
    if data != False:
        return {'code': 200, 'data': data, 'msg': '更新成功'}
    return {'code': 500, 'msg': '参数错误'}
# 获取词条历史记录
@app.route('/admin/get_record', methods=['GET','POST'])
def get_record():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data = do.get_record(reqData)
    if data != False:
        return {'code': 200, 'data': data, 'msg': '查询成功'}
    return {'code': 500, 'msg': '未获取到数据'}
# 回溯词条
@app.route('/admin/back_to_record', methods=['GET','POST'])
def back_to_record():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data = do.back_to_record(reqData)
    if data != False:
        return {'code': 200, 'data': data, 'msg': '处理成功'}
    return {'code': 500, 'msg': '处理失败'}
# 回溯词条
@app.route('/admin/back_record_for', methods=['GET','POST'])
def back_record_for():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data = do.back_for_all(reqData)
    if data != False:
        return {'code': 200, 'data': data, 'msg': '处理成功'}
    return {'code': 500, 'msg': '处理失败'}




""" ================================ 开放平台接口 ================================ """
# 获取完整分类表
@app.route('/open/get_full_categories', methods=['GET', 'POST'])
def open_get_full_categories():
    return {'code': 200, 'msg': '获取完整分类成功', 'data': do.get_full_categories()}

# 获取分类词条内容
@app.route('/open/get_tags_by_category', methods=['POST'])
def open_get_tags_by_category():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    data, cnt = do.get_tags_by_category(reqData)
    if data != False:
        return {'code': 200, 'data': data, 'total': cnt}
    return {'code': 401, 'msg': '参数错误或请求未被授权'}


if __name__ == '__main__':
    os.system('cls')
    app.config['SECRET_KEY'] = os.urandom(32)
    ssl_context = (config.ssl_pem_path, config.ssl_key_path) if config.enable_ssl else None
    app.run(debug=config.debug, threaded=True, host='0.0.0.0', port=config.server_port, ssl_context=ssl_context)