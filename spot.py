import requests
import xml.etree.ElementTree as ET
import json
from secret import SECRETS

class Spot:
    def __init__(self):
        self.FOURSQUARE_API_URL = 'https://api.foursquare.com/v2/venues/search'
        

    def _match_category_id(self, keywords):
        pass
        
    
    def recommend_spot(self, location, keywords):
        pass
