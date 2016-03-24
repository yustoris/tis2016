from keywords import Keywords
from spot import Spot


class Bot:
    def __init__(self):
        self.keyword_fetcher = Keywords()
        self.spot_client = Spot()

    def fetch_spot(self, sentence):
        result = self.keyword_fetcher.extract_from_sentence(sentence)

        message = {}
        message_body = ''
        spot = self.spot_client.recommend_spot(list(result[1])[0], result[0])
        if spot:
            message_body += spot['name']
            message_body += 'はどうでしょうか？'
            message_body += 'オススメポイントは'
            message_body += spot['reason']
            message_body += ' です'
            message['body'] = message_body
            message['image'] = spot['image']
        else:
            message_body = '申し訳ありません、候補が見つかりませんでした'
            message['body'] = message_body
        
        return message
