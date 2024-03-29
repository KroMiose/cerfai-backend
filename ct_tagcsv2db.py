from utils.dbManager import DatabaseManager
import pandas
import config
import math
import time
import re


db = DatabaseManager(config=config.database_settings)
file_timestr = time.strftime('%Y-%m-%d %H:%M:%S').replace(':', '_')


csvlist = [ # 待导入的csv文件 按顺序覆盖
    # 'A汉化词条31141.csv',
    # 'B未完成汉化11.5.csv',
    'C已完成汉化11.5.csv',
    '新增汉化D .csv',
]
overwriteTname = True   # 是否强制覆盖译名

'''
词条导入更新策略：
1. 如果该词条不存在贡献者，或已存在的贡献者即为待导入文件中该词条的词条贡献者，则执行词条信息各字段覆盖操作；更新贡献者
2. 如果该词条不存在数据库中则添加入库；更新贡献者
'''


# 写日志
def write_log(text, sqldata=None):
    with open(f"./outputs/入库日志_{file_timestr}_data.txt", "a", encoding="utf-8") as f: # 保存请求结果
        if config.debug:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n=> sql: {sqldata or 'None'}\n")
        else:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
        f.close()
    print(text)

# 获取danbooru检索链接
def get_search_url(tag):
    tag = tag.replace(' ', '_')
    return f"https://danbooru.donmai.us/posts?tags={tag}"

# 从 CSV 导入分类到数据库
def importTegCsv(csvfile, encode):
    sta = time.time()
    update_cnt = 0
    total_cnt = 0
    insert_cnt = 0

    df = pandas.read_csv('./data/' + csvfile, encoding=encode)

    # id;  name;  t_name;  is_nsfw;  desc;  remarks;  contributor;  c_id;  update_times;
    for i, row in df.iterrows():    # 遍历数据行
        total_cnt += 1

        if str(row['name']) != 'nan':
            if re.search(r'[a-zA-Z]{2}_[a-zA-Z(][a-zA-Z]', row['name']):   # 如果词条名符合 aa_aa
                name = row['name'].replace('\'', '\\\'').replace('_', ' ')  if row['name']        and (str(row['name'])        != 'nan') and (str(row['name'])        != 'None') else ''   # 词条名
            else:
                name = row['name'].replace('\'', '\\\'')                    if row['name']        and (str(row['name'])        != 'nan') and (str(row['name'])        != 'None') else ''   # 词条名

            t_name = row['t_name'].replace('\'', '\\\'')                    if row['t_name']      and (str(row['t_name'])      != 'nan') and (str(row['t_name'])      != 'None') else ''   # 词条译名
            c_id = row['c_id']                                              if row['c_id']        and (str(row['c_id'])        != 'nan') and (str(row['c_id'])        != 'None') else 3101 # 分类id
            desc = row['desc'].replace('\'', '\\\'')                        if row['desc']        and (str(row['desc'])        != 'nan') and (str(row['desc'])        != 'None') else ''   # 词条描述
            remarks = row['remarks'].replace('\'', '\\\'')                  if row['remarks']     and (str(row['remarks'])     != 'nan') and (str(row['remarks'])     != 'None') else ''   # 词条备注
            contributor  = row['contributor'].replace('\'', '\\\'')         if row['contributor'] and (str(row['contributor']) != 'nan') and (str(row['contributor']) != 'None') else ''   # 词条贡献者

            odata = db.select(f'''SELECT * FROM ct_tags WHERE name = '{name}';''')    # 检索词条名相同的原数据
            if len(odata) > 0:
                odata = odata[0]

                if (not odata['contributor']) or (odata['contributor'] == contributor+','):
                    sql = f'''UPDATE `ct_tags` SET `t_name` = '{t_name}', `desc` = '{desc}', `contributor` = '{contributor},', `c_id` = {c_id}, `remarks` = '{remarks}', `update_time` = NOW(), `update_times` = 1 WHERE `id` = {odata['id']};'''
                    write_log(f"正在更新词条 {odata['name']} 译名为 {row['t_name']}\n", sql)
                    db.execute(sql)
                    update_cnt += 1
                elif overwriteTname:
                    desc = desc or odata['desc']
                    remarks = remarks or odata['remarks']
                    sql = f'''UPDATE `ct_tags` SET `t_name` = '{t_name}', `desc` = '{desc or odata['desc']}', `remarks` = '{remarks or odata['remarks']}', `update_time` = NOW() WHERE `id` = {odata['id']};'''
                    write_log(f"正在更新词条 {odata['name']} 译名为 {row['t_name']}\n", sql)
                    db.execute(sql)
                    update_cnt += 1
            else: # todo 未匹配的词条作插入处理
                sql = f'''
                INSERT INTO `novelai`.`ct_tags` (`name`, `t_name`, `is_nsfw`, `desc`, `remarks`, `contributor`, `c_id`, `update_times`, `update_time`, `is_locked`, `effect_level`, `source`)\
                VALUES ('{name}', '{t_name}', 0, '{desc}', '{remarks}', '{contributor},', {c_id}, 1, NOW(), NULL, NULL, '');
                '''
                write_log(f"数据库中未匹配到词条: {row['name']} 执行插入\n", sql)
                db.execute(sql)
                insert_cnt += 1
    write_log(f"词条入库完成，共检索到词条数量: {total_cnt}，更新词条数: {update_cnt}，耗时: {time.time() - sta}\n\n")


if __name__ == "__main__":
    encodelist = ['gb2312', 'utf-8', 'utf_8_sig']
    for csv in csvlist:
        for encode in encodelist:
            try:
                write_log(f"正在处理文件: {csv}，编码: {encode}")
                importTegCsv(csv, encode)
                break
            except UnicodeDecodeError:
                write_log(f"处理文件: {csv}，编码: {encode} 无效，尝试下一种编码")
                continue

