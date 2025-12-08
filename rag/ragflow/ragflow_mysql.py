# Openai.py 开头添加这 2 行
import sys
from pathlib import Path
# 获取 models 目录的父目录（即 log 和 models 所在的根目录）
sys.path.append(str(Path(__file__).parent.parent.parent))



from database.sql import SQL
from typing import List
# 配置信息（实际开发中存放在 config.py 或环境变量）
config = {
    "host": "192.168.5.95",        # 数据库主机（本地为 localhost）
    "port": 3306,               # MySQL 默认端口
    "user": "root",             # 用户名（默认 root）
    "password": "123456",       # 你的 MySQL 密码
    "database": "datasets",     # 目标数据库名
    "charset": "utf8mb4"        # 字符集（支持 emoji）
}
## 主要用来操作知识库，表dataset
class RagflowDatasetsControl:
    def __init__(self,instance:SQL):
        self.instance = instance
        pass
    def query_by_hash_id(self,hash_id) -> List[dict]:
        result = self.instance.query(f"select * from dataset where hash_id = '{hash_id}'")
        return result
    
    def query_by_dataset_name(self,dataset_name) -> List[dict]:
        result = self.instance.query(f"select * from dataset where dataset_name = '{dataset_name}'")
        return result
    
    def query_by_meta_data(self,meta_data) -> List[dict]:
        result = self.instance.query(f"select * from dataset where meta_data = '{meta_data}'")
        return result        

    def insert_new_col(self,value: List[tuple]):
        self.instance.insert_batch("dataset","(dataset_name,hash_id,meta_data)","(%s,%s,%s)",value)

    def update_data(self,value: List[tuple],condition):
        self.instance.update("dataset",value,condition)

    def delete_data(self,condition:str):
        self.instance.delete("dataset",condition)
    
    def query_all(self) -> List[dict]:
        return self.instance.query(f"select * from dataset")


## 主要用来操作知识库，表documents
class RagflowDocumentsControl:
    def __init__(self,instance:SQL):
        self.instance = instance
        pass
    def query_by_document_id(self,document_id) -> List[dict]:
        result = self.instance.query(f"select * from document where document_id = '{document_id}'")
        return result
    
    def query_by_document_name(self,document_name) -> List[dict]:
        result = self.instance.query(f"select * from document where document_name = '{document_name}'")
        return result
    
    def query_by_meta_data(self,meta_data) -> List[dict]:
        result = self.instance.query(f"select * from document where meta_data = '{meta_data}'")
        return result        

    def insert_new_col(self,value: List[tuple]):
        self.instance.insert_batch("document","(document_name,document_id,meta_data,from_dataset,from_dataset_id)","(%s,%s,%s,%s,%s)",value)

    def update_data(self,value: List[tuple],condition):
        self.instance.update("document",value,condition)

    def delete_data(self,condition:str):
        self.instance.delete("document",condition)
    
    def query_all(self) -> List[dict]:
        return self.instance.query(f"select * from document")