


from abc import ABC,abstractmethod


class BaseComponent(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def create_instance(self):
        pass