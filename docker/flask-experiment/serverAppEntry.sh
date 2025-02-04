#!/bin/bash
gunicorn --bind 0.0.0.0:8082 --worker-class=gevent --worker-connections=1000 --workers=4 wsgi:app --timeout 600