from abc import ABC, abstractmethod

class BaseAnalyst(ABC):
    """
    所有分析師模型的基本類別。
    """
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def analyze(self, data):
        """
        對提供的數據進行分析。
        返回包含分析結果、預測和說明的字典。
        """
        pass
