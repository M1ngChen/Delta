from ragflow_sdk import *
from ragflow_sdk.modules.dataset import DataSet
from ragflow_sdk.modules.document import Document
# Openai.py 开头添加这 2 行
import sys
from pathlib import Path
# 获取 models 目录的父目录（即 log 和 models 所在的根目录）
sys.path.append(str(Path(__file__).parent.parent.parent))

from rag.rag_base import RAG
from typing import List,Tuple
from database.mysql.mysql_control import MysqlControl
from rag.ragflow.ragflow_mysql import RagflowDatasetsControl,RagflowDocumentsControl
from rag.ragflow.ragflow_pandas import PandasMapping
from models.http.openAI.Openai import EmbeddingInstanceByOpenai
QUERY_ALL = "所有"
QUERY_CRAFT = "工艺"
QUERY_DEVICE = "设备"

import time


class RagflowEmbeddingRetrieval(RAG):
    def __init__(self,url_http,api_key,embedding_instance:EmbeddingInstanceByOpenai):
        super().__init__(url_http,api_key)
        self.rag:RAGFlow = None
        self.rag = self.create_instance()
        self.meta_data_list = None
        self.ragflow_control = RagflowControl(self.rag)
        self.embedding_instance:EmbeddingInstanceByOpenai = embedding_instance
        self.meta_data_list = self._standard_meta_data(self.ragflow_control.pandas.query_key("meta_data"))
        pass

    def _standard_meta_data(self,meta_data:list):
        new_meta_data = []
        for meta in meta_data:
            if meta not in new_meta_data:
                new_meta_data.append(meta)
        return new_meta_data
    
    def update_metadata_list(self,meta:str):
        self.meta_data_list.append(meta)

    def create_instance(self):
        if self.rag is not None:
            return self.rag
        return RAGFlow(api_key=self.api_key,base_url=self.url_http)

    def retrieval(self,question:str,keyword:bool) -> List[Chunk]:
        start = time.time()
        meta_data = []
        if len(self.meta_data_list) == 1 and "all" in self.meta_data_list:
            meta_data = []
        else:
            for meta in self.meta_data_list:
                if meta == "all":
                    continue
                meta_data.append(meta)
        if self.embedding_instance is None:
            raise f"cannot retrieval question:{question},embedding instance is none"
            return []
        if len(meta_data) != 0:
            meta_data = self.retrieval_the_content(meta_data,question)
        else:
            meta_data.append("all")

        datasets,documents = self.get_relevant_documents(meta_data)
        embedding_time = time.time()
        chunk:List[Chunk] = self.rag.retrieve(dataset_ids=datasets,document_ids=documents,question=question,keyword=keyword)
        # for ck in chunk:
        #     print(f"chunk id:{ck.id}=======chunk similarity:{ck.similarity},chunk term_similarity:{ck.term_similarity},chunk vector_similarity:{ck.vector_similarity}")
        end = time.time()
        print(f"开销:{end - start}s,embedding time :{end - embedding_time}")
        return chunk


            
    def get_relevant_documents(self,meta_data:list) -> Tuple[list,list]:
        ret_datasets = []
        ret_documents = []
        data = self.ragflow_control.query_by_metadata(meta_data)
        for documents in data:
            for document in documents:
                if document["from_dataset_id"] not in ret_datasets:
                    ret_datasets.append(document["from_dataset_id"])
                if document["document_id"] not in ret_documents:
                    ret_documents.append(document["document_id"])
        return ret_datasets,ret_documents


    def retrieval_the_content(self,key_words:list,question:str) -> list:
        if not key_words:
            return []
        return self.embedding_instance.calculate_relevance(question,key_words)
    
dataset_frame = {
    "id": [],
    "name": [],
    "metadata":[]
}

# 配置信息（实际开发中存放在 config.py 或环境变量）
config = {
    "host": "192.168.5.95",        # 数据库主机（本地为 localhost）
    "port": 3306,               # MySQL 默认端口
    "user": "root",             # 用户名（默认 root）
    "password": "123456",       # 你的 MySQL 密码
    "database": "datasets",     # 目标数据库名
    "charset": "utf8mb4"        # 字符集（支持 emoji）
}

class RagflowControl:
    def __init__(self,rag_instance:RAGFlow):
        self.rag_instance:RAGFlow = rag_instance
        self.mysql_control =  MysqlControl(config)
        self.ragflow_datasets_control = RagflowDatasetsControl(self.mysql_control)
        self.ragflow_document_control = RagflowDocumentsControl(self.mysql_control)
        self.update_database()
        self.pandas:PandasMapping = self.mapping_to_pandas()
        pass

    def _checkout_key_value(self,dataset: DataSet,data:List[dict]):
        pass

    def update_database(self):
        datasets = self.rag_instance.list_datasets(page=1,page_size=4096)
        for dataset in datasets:
            result =  self.ragflow_datasets_control.query_by_hash_id(dataset.id)
            if not result:
                self.ragflow_datasets_control.insert_new_col([(dataset.name,dataset.id,"all")])
                continue
        self.update_documents(datasets)

    def update_documents(self,datasets:List[DataSet]):
        for dataset in datasets:
            for document in dataset.list_documents():
                # print(f"找到文档:{document.name},状态:{document.run}")
                if document.run != "DONE":
                    # print(f"跳过文档:{document.name},当前状态:{document.run}")
                    continue
                result = self.ragflow_document_control.query_by_document_id(document.id)
                if not result:
                    ret = self.ragflow_datasets_control.query_by_hash_id(dataset.id)
                    self.ragflow_document_control.insert_new_col([(document.name,document.id,ret[0]["meta_data"],dataset.name,dataset.id)])
        pass

    ## 加速查询
    def mapping_to_pandas(self) -> PandasMapping:
        mapping = {
                'document_name': [], 
                'document_id': [], 
                'meta_data': [],
                'from_dataset': [], 
                'from_dataset_id': []
                }
        results= self.ragflow_document_control.query_all()
        for ret in results:
            mapping["document_name"].append(ret["document_name"])
            mapping["document_id"].append(ret["document_id"])
            mapping["meta_data"].append(ret["meta_data"])
            mapping["from_dataset"].append(ret["from_dataset"])
            mapping["from_dataset_id"].append(ret["from_dataset_id"])
        return PandasMapping(mapping)
        
        
    def insert_new_raw_to_pandas(self,data:list):
        self.pandas.insert(data)

    ### 返回所有的docments对象
    def query_by_metadata(self,meta_data:list):
        datas_set = []
        for meta in meta_data:
            ret = self.pandas.query("meta_data",meta)
            datas_set.append(ret)
        return datas_set
