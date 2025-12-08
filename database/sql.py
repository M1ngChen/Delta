




from abc import ABC,abstractmethod
from typing import List


class SQL(ABC):
    def __init__(self,config):
        super().__init__()
        self.config = config

    @abstractmethod
    def create_instance(self):
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def query(self,sql:str) -> List[dict]:
        pass

    @abstractmethod
    def insert(self,table:str,template_key:str,template_value:str,value:tuple):
        pass
    
    @abstractmethod
    def insert_batch(self,table:str,template_key:str,template_value:str,value:List[tuple]):
        pass
    
    @abstractmethod
    def update(self,table:str,update_data:List[tuple],condition:str):
        pass

    @abstractmethod
    def delete(self,table:str,condition:str):
        pass