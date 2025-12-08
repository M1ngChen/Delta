
import mysql.connector
from mysql.connector import Error
from mysql.connector import MySQLConnection
from typing import List,Dict

# Openai.py 开头添加这 2 行
import sys
from pathlib import Path
# 获取 models 目录的父目录（即 log 和 models 所在的根目录）
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.sql import SQL

def update_key_value(update_data:List[tuple]) -> tuple:
    tup = []
    kv = ""
    for data in update_data:
        tmp = data[0] + " = " + "%s " + ","
        kv = kv + tmp
        tup.append(data[1])
    if kv[len(kv) -1 ] == ",":
        kv = kv[0:len(kv) - 1]
    return (kv,tuple(tup))


class MysqlControl(SQL):
    def __init__(self,config):
        super().__init__(config)
        self.connection_instance:MySQLConnection = None
        self.create_instance()
        pass
    
    def __del__(self):
        self.close()

    def create_instance(self):
        """创建数据库连接"""
        conn = None
        try:
            # 建立连接
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                print("数据库连接成功！")
                self.connection_instance = conn
        except Error as e:
            print(f"连接失败：{e}")
    def is_connected(self) -> bool:
        return self.connection_instance.is_connected()
    
    def close(self):
        self.connection_instance.close()

    def query(self,sql:str) -> List[dict]:
        try:
            with self.connection_instance.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"异常情况:{e}")
    def insert(self,table:str,template_key:str,template_value:str,value:tuple):
        try:
            with self.connection_instance.cursor(dictionary=True) as cursor:
                # 1. 单条插入（参数化查询，%s 是占位符，不是字符串格式化）
                sql_single = f"INSERT INTO {table} {template_key} VALUES {template_value}"
                data_single = value
                cursor.execute(sql_single, data_single)
            self.connection_instance.commit()
        except Exception as e:
            print(f"异常:{e}")
    
    
    def insert_batch(self,table:str,template_key:str,template_value:str,value:List[tuple]):
        try:
            with self.connection_instance.cursor(dictionary=True) as cursor:
                # 1. 单条插入（参数化查询，%s 是占位符，不是字符串格式化）
                sql_single = f"INSERT INTO {table} {template_key} VALUES {template_value}"
                data_batch = value
                cursor.executemany(sql_single,data_batch)
            self.connection_instance.commit()
        except Exception as e:
            print(f"异常:{e}")
    
    def update(self,table:str,update_data:List[tuple],condition:str):
        try:
            with self.connection_instance.cursor() as cursor:
                _kv,_param = update_key_value(update_data)
                sql = f"UPDATE {table} SET {_kv} WHERE {condition}"
                params = _param  # (新年龄, 新邮箱, 目标 ID)
                cursor.execute(sql, params)

                if cursor.rowcount > 0:
                    print(f"更新成功，影响 {cursor.rowcount} 条记录")
                    self.connection_instance.commit()  # 提交事务
                else:
                    print("未找到匹配的记录")

        except Error as e:
            self.connection_instance.rollback()
            print(f"更新失败：{e}")

    def delete(self,table:str,condition:str):
        try:
            with self.connection_instance.cursor() as cursor:
                sql =f"DELETE FROM {table} WHERE {condition}"
                cursor.execute(sql)

                if cursor.rowcount > 0:
                    print(f"删除成功，影响 {cursor.rowcount} 条记录")
                    self.connection_instance.commit()
                else:
                    print("未找到匹配的记录")

        except Error as e:
            self.connection_instance.rollback()
            print(f"删除失败：{e}")

# mc = MysqlControl()
# # mc.insert_batch("dataset","(dataset_name,hash_id,meta_data)","(%s,%s,%s)",[("测试","dwahekcmkekjr","数据"),
# #                                                                            ("测试2","dwahekcmkekjr","数据"),
# #                                                                            ("测试3","dwahekcmkekjr","数据")])
# # mc.update("dataset",[("meta_data","输出")],"hash_id = 'dwahekcmkekjr'")
# mc.delete("dataset","hash_id = 'dwahekcmkekjr'")
# # print(mc.query("select * from dataset"))
# mc.close()
    