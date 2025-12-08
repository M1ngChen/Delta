
from abc import ABC,abstractmethod


class BaseHttpInstance(ABC):
    def __init__(self,http_url:str,api_key:str):
        self.http_url = http_url
        self.api_key = api_key
        pass

    @abstractmethod
    def create_instance(self):
        pass

class HttpChatInstance(BaseHttpInstance):
    def __init__(self,http_url:str,api_key:str):
        super().__init__(http_url,api_key)
        pass

    @abstractmethod
    def push_content_segment(self,document:str,content:str):
        pass

    @abstractmethod
    def question(self,question:str,history_conversation_list:list,stream:bool):
        pass

    @abstractmethod
    def response(self):
        pass