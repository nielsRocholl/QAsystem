import re
import numpy
import spacy
from spacy import displacy
from spacy.attrs import LOWER, POS, ENT_TYPE, IS_ALPHA
from spacy.symbols import nsubj, pobj, dobj, PUNCT, SPACE, NOUN, PROPN, ADJ, amod, AUX, VERB, nsubjpass
from spacy.tokens import Doc
from modules.boolean import Boolean
from modules.count import Count
from modules.description import EntityDescription
from modules.x_of_y import XofY


# Removes entity from question to parse property


class Classifier:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def classify(self, question):
        """
        Classifies the question to belong to one of the modules. Returns one of these module objects.
        :param question: The question to classify
        :return: The specific question module.
        """
        for classifier in [
            self.classify_count,
            self.classify_boolean,
            self.classify_x_of_y,
            self.classify_description
        ]:
            classification = classifier(question)
            if classification is not None:
                # print('=> Classified as {}'.format(type(classification)))
                return classification

        return None

    def classify_count(self, question):
        # Return Count module if question is a count question else None.
        matches = ["how many", "how much"]
        if any(x in question.lower() for x in matches):
            entity = self.parse_entity(question)
            property = self.parse_property(question)
            return Count(question, entity, property)
        return None

    def classify_boolean(self, question):
        # Return Boolean module if question is a boolean question else None.
        # Question can refer to the instance of an entity, then a property is not named
        is_instance_of = re.search("(Is|Are) (.*) (an|a) (.*)[?]", question)

        # Question can refer to a different (named) property of an entity
        is_property = re.search("(Is|Are) (.*) (the|an|a) (.*) (of) (.*)[?]", question)
        if is_instance_of:
            entity = is_instance_of.group(2)
            guess = is_instance_of.group(4)
            return Boolean(question, entity, "instance of", guess)
        if is_property:
            guess = is_property.group(2)
            entity = is_property.group(6)
            property = is_property.group(4)
            return Boolean(question, entity, property, guess)
        return None

    def classify_description(self, question):
        """
        e.g.:
        What does Y stand for?
        What does Y denote?
        What does Y mean?
        What is [the/a/an] Y?

        Do parse entity and look if there is no property? Or do we use regex?
        Regex might incorrectly identify a Xofy question to be a descriptive question.
        """
        # This should handle all common description questions.
        count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape("of"), question))
        new = re.search("(What|Who) (does|is)(the|an)? (.+)((stand for)|mean|denote)?[?]?", question, re.IGNORECASE)
        if new and count == 0:
            entity = strip(new.group(4))
            return EntityDescription(question, entity)
        else:
            return None

    def classify_x_of_y(self, question):
        # Since this classification is used last we can simply parse property and entity
        x_of_y = re.search("(What is the) (.*) (of|for) (.*)[?]", question)
        if x_of_y:
            property = x_of_y.group(2)
            entity = x_of_y.group(4)
        else:
            property = self.parse_property(question)
            entity = self.parse_entity(question)

        if property is None or entity is None:
            return None
        return XofY(question, entity, property)

    # If no entity is found from noun chunks, loop through complete tokenlist
    def backup_entity_parse(self, question):
        ent = tuple()
        for token in question:
            if (token.dep == pobj or token.dep == dobj or token.dep_ == 'compound' or token.dep == amod or token.dep ==
                nsubjpass or token.dep == nsubj) and (token.pos == NOUN or token.pos == PROPN or token.pos == ADJ):
                ent += (token,)
            if (token.dep_ == 'compound' or token.dep == amod) and token.head.dep_ != 'ROOT':
                index1 = token.i
                index2 = token.head.i
                with question.retokenize() as retokenizer:
                    attrs = {"LEMMA": token.text + " " + token.head.text}
                    retokenizer.merge(question[index1:index2], attrs=attrs)
                ent += (token,)
        return ent

    def parse_entity(self, question):
        ent = None
        parse = self.nlp(question)

        # Parse based on entity model
        ent = parse.ents

        # Catch phrases which define some entity 'first, second, third'
        ent = tuple(e for e in ent if ent[0].label_ != "ORDINAL")

        # Search for (proper) nouns with right dependency
        if not ent:
            for pn in parse.noun_chunks:
                if pn.root.dep == dobj or pn.root.dep == pobj or pn.root.dep_ == "compound":
                    ent += (pn,)

        # If no entity is found check for subject dependency of noun
        if not ent:
            for pn in list(parse.noun_chunks):
                if pn.root.dep == nsubj:
                    ent += (pn,)

        # Use backup entity parser
        if not ent:
            ent = self.backup_entity_parse(parse)

        # Add number to entity (if necessary) i.e. Apollo 15
        for token in list(parse):
            if token.dep_ == "nummod":
                ent += (token,)

        if not ent:
            return None

        # Combine elements
        ents = list(ent)
        entity = None
        if len(ents) > 0:
            entity = ''
            for e in ents:
                entity += str(e) + ' '

        if entity:
            stopwords = ['an', 'a', 'the', 'which', 'what', 'who', 'when']
            querywords = entity.split()
            result = [word for word in querywords if word.lower() not in stopwords]
            entity = ' '.join(result)

        return entity

    def remove_span(self, doc, index):
        nlp_list = list(doc)
        del nlp_list[index]
        return self.nlp(" ".join([e.text for e in nlp_list]))

    def force_property_parse(self, question):
        properties = {
            "language": "languages",
            "languages": "languages",
            "awards": "award received"
        }
        for word in question.lower().split():
            if word in properties:
                return properties[word]
        return None

    def backup_property_parse(self, question):
        prop = None
        for token in question:
            if (token.dep_ == 'compound' or token.dep == amod) and token.head.dep_ != "ROOT" and token.head.dep_ != \
                    "compound" and (token.head.dep != pobj and token.head.dep != dobj):
                index1 = token.i
                index2 = token.head.i
                with question.retokenize() as retokenizer:
                    attrs = {"LEMMA": token.text + " " + token.head.text}
                    retokenizer.merge(question[index1:index2], attrs=attrs)
                prop = token.text
            if token.pos == NOUN and token.head.pos == AUX:
                prop = token.text
            if token.dep_ == "ROOT":
                if (token.pos != AUX and token.pos == VERB) or token.pos == NOUN:
                    prop = token.text
                    break
            if token.i + 1 >= len(question):
                break
        return prop

    # Parses most basic questions for now
    def parse_property(self, question):
        property = self.force_property_parse(question)
        if property:
            return property

        entity = self.parse_entity(question)
        parse = self.nlp(question)

        if entity:
            entity = entity.split()
            # Remove the entity from the question
            for ent in entity:
                entity_index = next((token.i for token in parse if token.text == ent), None)
                if entity_index is not None:
                    parse = self.remove_span(parse, entity_index)

        filtered = [token for token in parse if not token.is_stop and token.pos is not PUNCT and token.pos is not SPACE]
        if len(filtered) == 1:
            return filtered[0].text
        elif len(filtered) > 1:
            return self.backup_property_parse(parse)
        return None


def strip(line):
    stopwords = {'stand', 'for', 'mean', 'the', 'an', '?', 'denote', 'stand', " "}
    resultwords = [word for word in re.split("\W+", line) if word.lower() not in stopwords][0]
    return resultwords
