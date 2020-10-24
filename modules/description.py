from api import *
from .module import Module


class EntityDescription(Module):
    """
    Class representing a description of an entity question.
    """

    def __init__(self, question, entity):
        self.question = question
        self.entity = entity
        self.api = Api()

    def answer(self):
        # entity_uri = self.api.search_uri(self.entity)
        #print(self.entity)
        return self.api.create_description_answer(self.entity)
