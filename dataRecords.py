# 数据日志功能模块，用于每次修改后记录日志



from utils.dbManager import DatabaseManager


class dataRecorder:
    def __init__(self,db:DatabaseManager):
        self.db = db
        self.keyList={
        "ct_id":"id",
        "name":"name",
        "t_name":"t_name",
        "is_nsfw":"is_nsfw",
        "desc":"desc",
        "remarks":"remarks",
        "contributor":"contributor",
        "c_id":"c_id",
        "update_times":"update_times",
        "update_time":"update_time",
        "is_locked":"is_locked",
        "effect_level":"effect_level",
        "source":"source"
        }
        self.keyStr = ",".join(["`"+x+"`" for x in self.keyList.keys()])
        self.paramStr = ",".join(["%s"]*len(self.keyList.keys()))
    # 函数：修改记录。用于修改一次记录值
    def editRecord(self,originObj:object,ip:str="")->None:
        paramList=[]
        for (key,value) in self.keyList.items():
            paramList.append(originObj[value])
        paramList.append(ip)
        sql = "INSERT INTO ct_edit_record (%s,`record_time`,`ip`)VALUES(%s,NOW(),%%s);"%(self.keyStr,self.paramStr)
        if not self.db.execute_bind(sql, paramList):
            raise BaseException("Failed in creating record")
    
    # 函数：查询记录。用于查询一个词条的最近更新记录
    def getRecord(self,ct_id:int,page:int=1,pageSize:int=50) -> tuple:
        sql = "SELECT * from `ct_edit_record` where `ct_id`=%s ORDER BY `record_time` DESC LIMIT %s OFFSET %s;"
        return self.db.select_bind(sql, [ct_id,pageSize,(page-1)*pageSize])
    # 函数：查询记录。用于查询对于任意词条最近更新记录
    def filterRecord(self,ip:str="",time1:int=0,time2:int=0,page:int=1,pageSize:int=50) -> tuple:
        additionFilter = ""
        additionParam = []
        if time1 != 0:
            additionFilter = additionFilter + "`record_time` >= %%s"
            additionParam.append(time1)
        if time2 != 0:
            additionFilter = additionFilter + "`record_time` <= %%s"
            additionParam.append(time2)
        if ip != "":
            additionFilter = additionFilter + "`ip` = %%s"
            additionParam.append(ip)
        sql = "SELECT * from `ct_edit_record` %s ORDER BY `record_time` DESC LIMIT %%s OFFSET %%s;"%(additionFilter)
        return self.db.select_bind(sql, [*additionParam,pageSize,(page-1)*pageSize])
    def backToRecord(self,recId:int):
        recData = self.db.select_bind("SELECT * FROM `ct_edit_record` where `id`=%s",[recId])[0]
        ct_id=recData['ct_id']
        record_time=recData['record_time']
        paramList = []
        keyList = []
        for (key,value) in self.keyList.items():
            paramList.append(recData[key])
            keyList.append(value)

        keyStr = ",".join(["`"+x+"`=%s" for x in keyList])

        #TODO:此处由于库限制暂未实现原子化，日后需要修改
        if self.db.execute_bind(
            "UPDATE `ct_tags` SET %s where `id`=%%s;"
            %
            (keyStr),[*paramList,ct_id]
        ) and self.db.execute_bind("DELETE FROM `ct_edit_record` where `ct_id`=%s AND `record_time`>%s OR `id`=%s",
        [ct_id,record_time,recId]):
            return True
        raise BaseException("无法回滚数据")

    
