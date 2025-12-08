
from abc import ABC,abstractmethod




class BaseText(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def _create_instance(self):
        pass