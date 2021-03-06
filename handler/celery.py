# _*_ coding: utf-8 _*_

from celery import Celery

app = Celery('handler', include=['handler.tasks'])
app.config_from_object('config')


if __name__ == '__main__':
    app.start()
