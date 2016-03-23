from keywords import Keywords
from spot import Spot


class Bot:
    def __init__(self):
        self.keyword_fetcher = Keywords()

    def fetch_spot(self, sentence):
        result = self.keyword_fetcher.extract_from_sentence(sentence)
        message = ''

        message += 'キーワード: '
        for keyword in result[0]:
            message += keyword + ' '

        message += '場所: '
        for location in result[1]:
            message += location + ' '
        
        return message
        
