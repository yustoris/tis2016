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
        if spot:
            message += spot['name']
            message += 'はどうでしょうか？'
            message += spot['reason']
            message += 'ですよ'
        else:
            message = '申し訳ありません、候補が見つかりませんでした'
        
        return message
