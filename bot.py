from keywords import Keywords
from spot import Spot


class Bot:
    def __init__(self):
        self.keyword_fetcher = Keywords()
        self.spot_client = Spot()

    def fetch_spot(self, sentence):
        result = self.keyword_fetcher.extract_from_sentence(sentence)

        message = ''
        spot = self.spot_client.recommend_spot(list(result[1])[0], result[0])
        message += spot['name']
        message += 'はどうでしょうか？'
        message += spot['reason']
        message += 'ですよ'
        
        return message
