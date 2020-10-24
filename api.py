from enum import Enum
import requests


class SearchType(Enum):
    STANDARD = 0
    DESCRIPTION = 1
    TWO_STEP = 2
    LABEL = 3


class Api:
    """
    This class handles making queries and searching with these queries on the WikiData API endpoint.
    """
    def search_uri(self, name, index = 0, property_search=False, verbose=False):
        """
        Searches for entity or property objects (Q-, P-) on wikidata.
        :param name: The string name of the entity or property
        :param property_search: Search for property instead of entity
        :param verbose: Prints ids, labels and descriptions of results
        :return: A list of results. Each result is a list with id, label and description. Id is often used.
        """
        WIKI_API_URL = 'https://wikidata.org/w/api.php'
        if name is None:
            return
        params = {'action': 'wbsearchentities',
                  'search': name, 'language': 'en', 'format': 'json'}
        if property_search:
            params['type'] = 'property'
        response = requests.get(WIKI_API_URL, params).json()['search']
        if not response:
            return None
        if verbose:
            for r in response:
                print(r['id'])
                print("test")
        if len(response) > index:
            return response[index]['id']
        else:
            return None

    def get_answer(self, query, search_type=SearchType.STANDARD, verbose=False):
        """
        Queries the WikiData API with given query.
        :param query: The query
        :param search_type: SearchType of query. Can be one of STANDARD, DESCRIPTION, LABEL etc.
        :param verbose: Will print the response url.
        :return: Returns the results of the parsed query.
        """

        url = 'https://query.wikidata.org/sparql'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0"
        }
        response = requests.get(
            url, headers=headers, params={'query': query, 'format': 'json'})
        if verbose:
            print(response.url)
        if response.status_code != 200:
            raise Exception('Bad response with SPARQL')
        data = response.json()
        if not data['results']['bindings']:
            return None

        results = []
        for item in data['results']['bindings']:
            if search_type is SearchType.STANDARD:
                results.append(item['answerLabel']['value'])
            elif search_type is SearchType.DESCRIPTION:
                results.append(item['description']['value'])
            elif search_type is SearchType.TWO_STEP:
                val = item['answer']['value']
                if str(val).startswith('http://www.wikidata.org/entity/'):
                    val = str(val).replace('http://www.wikidata.org/entity/', '')
                results.append(val)
        return results

    def better_search(self, query, verbose=False):
        if verbose:
            print('Search:\n', query)
        url = 'https://query.wikidata.org/sparql'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0"
        }
        response = requests.get(
            url, headers=headers, params={'query': query, 'format': 'json'})
        if response.status_code != 200:
            raise Exception('Bad response with SPARQL')
        response = response.json()
        bindings = response['results']['bindings']
        answer = []
        if bindings:
            vars = response['head']['vars']
            for item in bindings:
                for v in vars:
                    answer.append(item[v]["value"])
            return answer
        return None


    def create_count_query(self, property, entity):
        """
        Creates a query which counts the instances of a property on an entity
        :param property: The property uri (P...)
        :param entity: The entity uri (Q...)
        :return:
        """
        query = """
                SELECT (COUNT (?item) as ?count) WHERE {{
                wd:{} wdt:{} ?item
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                }}
                """
        query = query.format(entity, property)
        return query


    def create_X_of_Y_query(self, property, entity):
        """
        Create a X (property) of Y (entity) query.
        :param property: The X property
        :param entity: The Y entity
        :return: The query
        """
        return '''
        SELECT ?answer ?answerLabel WHERE {
            wd:''' + entity + ''' wdt:''' + property + ''' ?answer.
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }'''

    def create_description_answer(self, query):
        """
        Queries the WikiData API with given query.
        :param query: The entity
        :return: The query
        """
        API_ENDPOINT = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'search': query
        }
        r = requests.get(API_ENDPOINT, params=params)
        print(r.json()['search'][0]['description'])
        return [r.json()['search'][0]['description']]


    def create_label_query(self, entity):
        """
        Create a query to get the label of an entity
        :param entity: The entity
        :return: The query
        """
        return '''
        SELECT ?answerLabel WHERE {
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en" .
                wd:''' + entity + ''' rdfs:label ?answerLabel .
            }
        }
        '''
