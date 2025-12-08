# Openai.py 开头添加这 2 行
import sys
from pathlib import Path
# 获取 models 目录的父目录（即 log 和 models 所在的根目录）
sys.path.append(str(Path(__file__).parent.parent.parent))

from rag.ragflow.ragflow_embedding import RagflowEmbeddingRetrieval
from models.http.openAI.Openai import ChatInstanceByOpenai,EmbeddingInstanceByOpenai
from component.base_component import BaseComponent
from typing import List,Tuple
from ragflow_sdk.modules.chunk import Chunk
import time



class ChatInstance(BaseComponent):
    def __init__(self,embedding_model:RagflowEmbeddingRetrieval,chat_model:ChatInstanceByOpenai):
        super().__init__()
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.create_instance()

    def _check_embedding_model_and_chat_model(self,embedding,chat):
        if embedding is None:
            raise f"cannot create chat instance,RagflowEmbeddingRetrieval is None"
        if chat is None:
            raise f"cannot create chat instance,ChatInstanceByOpenai is None"

    def create_instance(self):
        self._check_embedding_model_and_chat_model(self.embedding_model,self.chat_model)

    #过滤部分chunk
    def filter_chunk(self,chunks:List[dict],filter:float,keyword:bool) -> List[str]:
        contents = []
        chunks = sorted(chunks, key=lambda x: x["weight"], reverse=True)
        chunks = chunks[0:int(len(chunks) * filter)]
        for chunk in chunks:
            contents.append({"content":chunk["content"],"name":chunk["name"]})
        return contents
    
    def _recalculate_the_weights(self,chunks:List[Chunk]) -> List[dict]:

        new_weight_chunk = []
        for chunk in chunks:
            #print(f"当前chunk id:{chunk.id},vector_similarity:{chunk.vector_similarity},term_similarity:{chunk.term_similarity}")
            temp = {}
            weight = chunk.similarity
            temp["content"] = chunk.content
            temp["name"] = chunk.document_name
            temp["weight"] = weight
            new_weight_chunk.append(temp)

        return new_weight_chunk
    
    def question(self,question:str,history_conversation:list,stream:bool):
        chunks = self.embedding_model.retrieval(question,False)
        contents = self._recalculate_the_weights(chunks)
        contents = self.filter_chunk(contents,0.2,False)
        self.chat_model.push_content_segments(contents)
        self.chat_model.question(question,history_conversation,stream)
        return self.chat_model.response()

class Chat:
    def __init__(self,config:dict):
        self.openai_chat = ChatInstanceByOpenai(http_url=config["chat"]["http"],api_key=config["chat"]["api_key"])
        self.openai_embedding = EmbeddingInstanceByOpenai(http_url=config["embedding"]["http"],api_key=config["embedding"]["api_key"],embedding_model=config["embedding"]["model"])
        self.ragflow_retrieval = RagflowEmbeddingRetrieval(url_http=config["ragflow"]["http"],api_key=config["ragflow"]["api_key"],embedding_instance=self.openai_embedding)
        self.chat_instance = ChatInstance(self.ragflow_retrieval,self.openai_chat)
        self.session = ChatSession()
        self.current_response = None
        self.current_content = ""
        self.init()

        pass
    
    def get_knowledge_content(self) -> list:
        l =  self.openai_chat.get_content()
        content = l[-1]["content"]
        content = content.split("\n\n\nBased")[0]
        l[-1]["content"] = content
        return l

    def init(self):
        say_hello = "你好请问有什么能帮助你！\n"
        self.session.add_system(say_hello)
        print(say_hello,flush=True,end="")

    def question(self,question:str,stream:bool):
        if self.current_content != "":
            self.session.add_assistant(self.current_content)
            self.current_content = ""
        self.current_response = self.chat_instance.question(question=question,history_conversation=self.session.get_history(),stream=stream)
        self.session.add_user(question)
    def response(self):
        for res in self.current_response:
            self.current_content += res
            yield res
    
    def get_current_full_response_content(self):
        return self.current_content



class ChatSession:
    def __init__(self):
        self.history_conversation = []
        pass
    def add_assistant(self,content:str):
        temp = {
            "role":"assistant",
            "content":content
        }
        self.history_conversation.append(temp)

    def add_user(self,content:str):
        temp = {
            "role":"user",
            "content":content
        }
        self.history_conversation.append(temp)

    def add_system(self,conetent:str):
        temp = {
            "role":"system",
            "content":conetent
        }
        self.history_conversation.append(temp)
    
    def get_history(self) -> list:
        return self.history_conversation

    def clear_all_history(self):
        self.history_conversation = []


# start = time.time()
# chat = ChatInstanceByOpenai(http_url="http://192.168.5.208:8007/v1",api_key="")
# embedding = EmbeddingInstanceByOpenai(http_url="http://192.168.5.208:8006/v1",api_key="",embedding_model="Qwen3-Embedding")
# retrieval = RagflowEmbeddingRetrieval(url_http="http://192.168.5.116:9000",api_key="ragflow-BgpYZvaB8tnkTOY-nYYB2j0xyLZMB5wxGOmxq87MU6Y",embedding_instance=embedding)
# chat = ChatInstance(retrieval,chat)
# for con in chat.question("不太理解铝电解工艺?"):
#     print(con,end="",flush=True)
# end = time.time()
# print(f"总耗时:{end-start}s")

config = {
    "chat":{
        "http":"http://192.168.5.208:8007/v1",
        "api_key":""
    },
    "embedding":{
        "http":"http://192.168.5.208:8006/v1",
        "api_key":"",
        "model":"Qwen3-Embedding"
    },
    "ragflow":{
        "http":"http://192.168.5.116:9000",
        "api_key":"ragflow-BgpYZvaB8tnkTOY-nYYB2j0xyLZMB5wxGOmxq87MU6Y"
    }
}
chat = Chat(config=config)
# chat.question("什么是铝电解?",stream=True)
# for res in chat.response():
#     print(res,end="",flush=True)
# print(chat.get_current_full_response_content())
while True:
    # 获取用户输入
    user_input = input("\n你：")
    
    # 退出逻辑
    if user_input.lower() == "quit":
        print("👋 对话结束！")
        break
    print(user_input)
    # 发起对话（自动携带上下文）
    start = time.time()
    chat.question(user_input,stream=True)
    for res in chat.response():
        print(res,end="",flush=True)
    end = time.time()
    print(f"总耗时:{end - start}")
    print("\n\n\n")
    print(chat.get_knowledge_content())