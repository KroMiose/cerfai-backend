# 服务
server_host = '127.0.0.1'
server_port = 9091

# 是否处于debug模式
debug = True

# 数据库连接配置（本地）
database_settings = {
    'mysql_host': 'localhost',
    'mysql_port': '3306',
    'mysql_user': 'root',
    'mysql_passwd': '',
    'mysql_db': 'novelai',
    'enable_debug': False,
}

# 数据库连接配置（生产）
# database_settings = {
#     'mysql_host': '127.0.0.1',
#     'mysql_port': '3306',
#     'mysql_user': 'novelai',
#     'mysql_passwd': 'y8ryKCZynxM5GfY7',
#     'mysql_db': 'novelai',
#     'enable_debug': False,
# }

# 数据库连接配置（测试）
# database_settings = {
#     'mysql_host': '127.0.0.1',
#     'mysql_port': '3306',
#     'mysql_user': 'novelai-dev',
#     'mysql_passwd': 'fGbnjDGtZ7HMKywf',
#     'mysql_db': 'novelai-dev',
#     'enable_debug': False,
# }

# 贡献榜更新间隔时间：单位：秒
contributor_update_delay = 60 * 60

# 词条更新提交间隔时间，单位：秒
ct_submit_delay = 10

# 管理访问密钥
access_key = '9a58459a6ec807b112933c8c676e295e'

# 每次返回的数据条数最大限制
max_ret_data_limit = 100

# SSL证书配置(弃用)
enable_ssl = False
ssl_pem_path = './ssl/api.kromiose.top.pem'
ssl_key_path = './ssl/api.kromiose.top.key'