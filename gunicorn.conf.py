wsgi_app = "web2rss.app:app"

workers = 2
threads = 4
timeout = 600
preload_app = True
max_requests = 256
max_requests_jitter = 32

capture_output = True
accesslog = "-"
errorlog = "-"
