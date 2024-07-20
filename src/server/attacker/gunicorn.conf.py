from config import DATASET

bind = '0.0.0.0:11000'
workers = 40
worker_class = 'gthread'
preload = True
reload = True
daemon = False
threads = 8
timeout = 120
keepalive = 5
pidfile = './logs/dynamic/gunicorn_server.pid'
errorlog  = f'./logs/dynamic/{DATASET}_gc.log'
loglevel = 'info'
capture_output = True
proc_name = 'gunicorn_server'
max_requests = 0
wsgi_app = "attacker.wsgi"