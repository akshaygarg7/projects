from abc import ABC, abstractmethod

class BaseProxy(ABC):
    @abstractmethod
    def invoke(self, input):
        pass
