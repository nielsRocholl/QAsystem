from api import *
from .module import Module
from lookup_table import LookupTable


class XofY(Module):
    """
    Class representing a property (X) of entity (Y) question.
    """

    def __init__(self, question, entity, property):
        self.question = question
        self.entity = entity
        self.property = property
        self.api = Api()
        self.lookup_table = LookupTable()

    def answer(self):
        for i in range(5):
            entity_uri = self.api.search_uri(self.entity, i)
            if entity_uri is None:
                return None

            if self.property == "discovered" or self.property == "invented" or self.property == "founded":
                if not "When" in self.question and not "date" in self.question:
                    self.property = self.lookup_table.replace_property(self.property)

            if self.property == "born":
                if "Where" in self.question:
                    self.property = "place of birth"

            if self.property == "die":
                if "Where" in self.question:
                    self.property = "place of death"
                if "How" in self.question:
                    self.property = "cause of death"

            property_uri = self.api.search_uri(self.property, property_search=True)
            if property_uri is None:
                # print('could not find uri of', self.property)
                # try replacing with lookup table
                self.property = self.lookup_table.replace_property(self.property)
                property_uri = self.api.search_uri(self.property, property_search=True)
                if property_uri is None:
                    return None
                # print('Replaced with {} ({})'.format(self.property, property_uri))

            query = self.api.create_X_of_Y_query(entity=entity_uri, property=property_uri)
            answer = self.api.better_search(query)

            # Try replacing property again and check again.
            if answer is None:
                # print('No answer for property: {} ({})'.format(self.property, property_uri))
                self.property = self.lookup_table.replace_property(self.property)
                property_uri = self.api.search_uri(self.property, property_search=True)
                # print('No answer - replaced with {} ({})'.format(self.property, property_uri))
                if property_uri is None:
                    return None
                query = self.api.create_X_of_Y_query(entity=entity_uri, property=property_uri)
                answer = self.api.better_search(query)
                # print("answer2: ", answer)

            if answer != None:
                break

        return answer
