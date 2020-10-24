

class LookupTable:
    """A lookup table to replace properties so that wikidata can better understand them."""
    def __init__(self):
        self.table = {
            "originated": "country of origin",
            "originate": "country of origin",
            "originate in": "country of origin",
            "country": "country or origin",
            "members": "has part",
            "member": "has part",
            "pseudonym": "also known as",
            "start": "inception",
            "year": "inception",
            "inception": "start time",
            "made of": "has part",
            "part": "has part",
            "included": "has part",
            "located": "part of",
            "instance": "instance of",
            "subclass": "subclass of",
            "member": "member of",
            "effects": "has effect",
            "causes": "has immediate cause",
            "has immdediate cause": "has cause",
            "big": "mass",
            "mass": "size",
            "study": "educated at",
            "discovered": "discoverer or inventor",
            "discoverers": "discoverer or inventor",
            "invented": "discoverer or inventor",
            "inventors": "discoverer or inventor",
            "created": "discoverer or inventor",
            "founded": "founded by",
            "named": "named after",
            "wrote": "author",
        }

    def replace_property(self, property):
        """
        Find and replace a property using the lookup table
        :param property: The property to replace
        :return: The new property
        """
        if property in self.table:
            return self.table[property]
        return property
