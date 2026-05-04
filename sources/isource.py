from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class ISource(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def close(self):
        pass
    @abstractmethod
    def is_opened(self) -> bool:
        pass