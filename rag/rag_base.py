from abc import ABC,abstractmethod




class RAG(ABC):
    def __init__(self,url_http,api_key):
        self.url_http = url_http
        self.api_key = api_key
        super().__init__()
    @abstractmethod
    def create_instance(self):
        pass

    @abstractmethod
    def retrieval(self,question:str,keyword:bool) -> list:
        pass

    @abstractmethod
    def retrieval_the_content(self,key_words:list,question:str) -> list:
        pass


