# _*_ coding: utf-8 _*_

import os

HERE = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(HERE, 'permdir')

REDIS_URL = "redis://localhost:6379"
CACHE_REDIS_URL = REDIS_URL
