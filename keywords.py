import requests
import xml.etree.ElementTree as ET
import json
from secret import SECRETS

class Keywords:
    def __init__(self):
        self.YAHOO_KEYWORD_API_URL = 'http://jlp.yahooapis.jp/KeyphraseService/V1/extract'
        self.GOO_NE_API_URL = 'https://labs.goo.ne.jp/api/entity'
        
    
    def extract_from_sentence(self, sentence):
        # Fetch keywords with Yahoo API
        data = {
            'sentence': sentence,
            'appid': SECRETS['YAHOO_APP_ID']
        }
        response = requests.post(self.YAHOO_KEYWORD_API_URL, data=data)
        keyphrases = set()
        
        for child in ET.fromstring(response.text):
            keyphrase = child[0].text # Result/Keyphrase
            keyphrases.add(keyphrase)


        # Fetch NEs with Goo API
        data = {
            'sentence': sentence,
            'app_id': SECRETS['GOO_APP_ID'],
            'class_filter': 'LOC'
        }
        headers = {'Content-type':'application/json'}
        result = requests.post(self.GOO_NE_API_URL, data=json.dumps(data), headers=headers).json()

        nes = set()
        for ne in result['ne_list']:
            nes.add(ne[0])
            
        return (keyphrases - nes, nes)
