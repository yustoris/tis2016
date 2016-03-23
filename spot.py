import requests
import xml.etree.ElementTree as ET
import json
import foursquare
from functools import reduce
from secret import SECRETS

class Spot:
    def __init__(self):
        self.FOURSQUARE_API_URL = 'https://api.foursquare.com/v2/venues/search'
        self._foursquare_client = foursquare.Foursquare(
            client_id=SECRETS['FOURSQUARE_CLIENT_ID'],
            client_secret=SECRETS['FOURSQUARE_CLIENT_SECRET'],
            lang='ja'
        )
        categories = self._foursquare_client.venues.categories()
        self._categories = self._flatten_categories(categories)

    def _flatten_categories(self, nested_categories):
        result = []
        for categories in nested_categories['categories']:
            result.append((categories['name'], categories['id']))
            for sub_category_name in self._flatten_categories(categories):
                result.append(sub_category_name)
        return result

    def _match_category_ids(self, keywords):
        matched_category_ids = [category[1] for category in self._categories if category[0] in keywords]
        return matched_category_ids
        
    def recommend_spot(self, location, keywords):
        target_categories = self._match_category_ids(keywords)
        params={
            'near':location,
            'categoryId':reduce(lambda i, s:i+','+s, target_categories)
        }
        response = self._foursquare_client.venues.search(params=params)
        # Instantly return
        ret = {
            'name': response['venues'][0]['name'],
            'reason': 'TODO' # Add recommend reason
        }
        return ret
