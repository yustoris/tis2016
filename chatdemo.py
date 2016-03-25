#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options
from bot import Bot

import os

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret=os.environ['COOKIE_SECRET'],
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200
    
    def __init__(self, *args, **kwargs):
          super(ChatSocketHandler, self).__init__(*args, **kwargs)
          self.bot = Bot()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        user_message = {
            "id": str(uuid.uuid4()),
            "pos":'right',
            "talker":'human',
            "body": parsed["body"], 
            }
        user_message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=user_message))
        ChatSocketHandler.update_cache(user_message)
        ChatSocketHandler.send_updates(user_message)
        self._bot_message(parsed['body'])


    def _bot_message(self, message):
        bot_message = self.bot.fetch_spot(message)
        bot_message_out = {
            "id": str(uuid.uuid4()),
            "pos":'left',
            "talker":'robot',
            "body": bot_message['body'],
            }
        if 'image' in bot_message:
            bot_message_out['image'] = bot_message['image']
            
        bot_message_out["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=bot_message_out))
        ChatSocketHandler.update_cache(bot_message_out)
        ChatSocketHandler.send_updates(bot_message_out)
        ## 色
        ## 利用方法の定型文言


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
