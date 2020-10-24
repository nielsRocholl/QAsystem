from abc import abstractmethod


class Module:
    """class serves as a (abstract) parent class for all modules"""
    @abstractmethod
    def answer(self):
        pass
