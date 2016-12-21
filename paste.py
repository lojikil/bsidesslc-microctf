import lolweb
from bottle import run, app
from paste.translogger import TransLogger
import logging
import time

start_stamp = time.ctime().replace(' ', '-')

logging.basicConfig(filename="logs/paste-{0}.log".format(start_stamp),
                    filemode="w",
                    level=logging.INFO)
wsgil = logging.getLogger('wsgi')
ch = logging.FileHandler("logs/wsgi-{0}.log".format(start_stamp))
wsgil.addHandler(ch)
app = TransLogger(app())

run(port=8080,
    host='0.0.0.0',
    server='paste',
    app=app)
