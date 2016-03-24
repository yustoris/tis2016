import requests
import xml.etree.ElementTree as ET
import json
import foursquare
from keywords import Keywords
from functools import reduce
from secret import SECRETS
from collections import Counter

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
        self._keyword = Keywords()

    def _flatten_categories(self, nested_categories):
        result = []
        for categories in nested_categories['categories']:
            result.append((categories['name'], categories['id']))
            for sub_category in self._flatten_categories(categories):
                result.append(sub_category)
        return result

    def _match_category_ids(self, keywords):
        matched_category_ids = [(category[0], category[1]) for category in self._categories if category[0] in keywords]
        return matched_category_ids
        
    def recommend_spot(self, location, keywords):
        target_categories = self._match_category_ids(keywords)

        target_category_names = set(category[0] for category in target_categories)
        target_category_ids = set(category[1] for category in target_categories)

        params={
            'near':location,
            'categoryId':reduce(lambda i, s:i+','+s, target_category_ids),
            'intent': 'browse',
            'limit':50,
        }

        try :
            response = self._foursquare_client.venues.search(params=params)
        except:
            return None

        ## Reccomend comment
        candidates = []
        for venue in response['venues']:
            venue_id = venue['id']
            candidate = {}

            if venue['stats']['tipCount'] >= 2 and venue['stats']['checkinsCount'] >= 1500:
                venue_detail = self._foursquare_client.venues(venue_id)['venue']

                if len(venue_detail['tips']['groups']) > 1:
                    tips = venue_detail['tips']['groups'][1]['items']
                else:
                    tips = venue_detail['tips']['groups'][0]['items']
                word_counter = Counter()
                for tip in tips:
                    if 'lang' in tip and tip['lang'] != 'ja':
                        continue
                    
                    keywords, _ = self._keyword.extract_from_sentence(tip['text'])
                    for keyword in keywords:
                        like_count = tip['likes']['count']
                        word_counter[keyword] += 1 * (1 if like_count == 0 else like_count)

                print(venue['id'], venue['name'], word_counter)
                tags = []
                for key, count in word_counter.most_common(10):
                    if count > 1:
                        tags.append(key)
                if len(tags) > 0:
                    candidate['name'] = venue['name']
                    candidate['tags'] = tags
                    if 'photos' in venue_detail and venue_detail['photos']['groups'] and venue_detail['photos']['groups'][0]['items']:
                        photo = venue_detail['photos']['groups'][0]['items'][0]
                        candidate['image'] = photo['prefix'] + '128x128' +photo['suffix']
                    candidates.append(candidate)
            if len(candidates) > 0:
                break

        if len(candidates) == 0:
            return None

        # Instantly return most popular candidate
        print(candidates)
        top_candidate = candidates[0]
        ret = {
            'name': top_candidate['name'],
            'reason': reduce(lambda i, s: i+' '+s, top_candidate['tags']), # Add recommend reason
            'image': top_candidate['image']
        }
        return ret
