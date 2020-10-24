from api import *
from .module import Module


class Count(Module):
    """
    Class representing a "count" question.
    """
    def __init__(self, question, entity, property):
        self.question = question
        self.entity = entity
        self.property = property
        self.api = Api()

    def answer(self):
        answer = None
        for i in range(5):
            entity_uri = self.api.search_uri(self.entity, i)
            property_uri = self.api.search_uri(self.property, property_search=True)
            if entity_uri and property_uri:
                query = self.api.create_count_query(entity=entity_uri, property=property_uri)
                answer = self.api.better_search(query)
            if answer != None:
                break
        return answer