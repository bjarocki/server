import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import zlib
import json
import datetime
import time
import logging

websockets = set()

class WSHandler(tornado.websocket.WebSocketHandler):

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        websockets.add(self)

    def on_close(self):
        websockets.remove(self)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write([])
    def post(self):
        try:
            if 'Content-Encoding' in self.request.headers and self.request.headers['Content-Encoding'] == 'deflate':
                message = json.loads(zlib.decompress(self.request.body))
                for waiter in websockets:
                    waiter.write_message(message)
            else:
                message = self.request.body
            json_object = json.loads(message)
        except Exception as e:
            print(e)
            logging.error("Error sending message", exc_info=True)


application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r"/post", MainHandler),
])


if __name__ == "__main__":
    try:
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(9999)
        main_loop = tornado.ioloop.IOLoop.instance().start()
    except:
        raise

