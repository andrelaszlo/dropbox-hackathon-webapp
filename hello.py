import web
import os

urls = (
    '/(.*)', 'hello'
)

app = web.application(urls, globals())

class hello:
    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'

# For serving using any wsgi server
wsgiapp = app.wsgifunc()

if __name__ == "__main__":
    app.run()
    port = int(os.environ.get('PORT', 9000))
    web.httpserver.runsimple(app, server_address=('0.0.0.0', port))
