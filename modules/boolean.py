from api import *
from .module import Module


class Boolean(Module):
    """
    Class representing a "boolean" question.
    """
    def __init__(self, question, entity, property, guess):
        self.question = question
        self.entity = entity
        self.guess = guess
        self.property = property
        self.api = Api()

    def answer(self):
        answer = None
        for i in range(5):
            entity_uri = self.api.search_uri(self.entity, i)
            property_uri = self.api.search_uri(self.property, property_search=True)
            if entity_uri and property_uri:
                query = self.api.create_X_of_Y_query(entity=entity_uri, property=property_uri)
                answer = self.api.better_search(query)
            if answer:
                break

        if answer:
            if self.guess in answer:
                return ["Yes"]

            if property == "instance of":
                # The answer could also be in "subclass of"
                query = self.api.create_X_of_Y_query(entity=self.entity, property="subclass of")
                answer = self.api.better_search(query)
                if self.guess in answer:
                    return ["Yes"]

        return ["No"]
