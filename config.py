# 服务
server_host = '127.0.0.1'
server_port = 3090

# 是否处于debug模式
debug = True

# 数据库连接配置
database_settings = {
    'mysql_host': 'localhost',
    'mysql_port': '3306',
    'mysql_user': 'root',
    'mysql_passwd': '',
    'mysql_db': 'novelai',
    'enable_debug': False,
}

# 数据库连接配置
# database_settings = {
#     'mysql_host': '114.55.172.3',
#     'mysql_port': '3306',
#     'mysql_user': 'novelai',
#     'mysql_passwd': 'pMTdWmjTBzAxDE2H',
#     'mysql_db': 'novelai',
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