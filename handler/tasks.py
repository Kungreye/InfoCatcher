# _*_ coding: utf-8 _*_

from celery.utils.log import get_task_logger

from app import app as _app

from handler.celery import app  # celery instance
from models.search import Item, TARGET_MAPPER
from models.consts import K_POST
from corelib.utils import AttrDict


logger = get_task_logger(__name__)


class RequestContextTask(app.Task):     #  `app.Task`, base task class for this app.
    abstract = True

    def __call__(self, *args, **kwargs):
        with _app.test_request_context():
            return super(RequestContextTask, self).__call__(*args, **kwargs)


@app.task(base=RequestContextTask)
def reindex(id, kind, op_type):
    target_cls = TARGET_MAPPER.get(kind)
    if not target_cls:
        logger.info(f'Reindex Error: Unexpected kind {kind}')
        return

    target = target_cls.get(id)

    if not target:
        logger.info(f'Reindex Error: Unexpected {target.__class__.__name__}<id={id}>')  # noqa
        return
    logger.info(f'Reindex: {target.__class__.__name__}<id={id}>')
    if kind != K_POST:
        # at present, only support `Post`
        return

    item = None

    if op_type == 'create':
        item = Item.add(target)
    elif op_type == 'update':
        item = Item.update_item(target)
    elif op_type == 'delete':
        item = Item.get(target.id, target.kind)     # ???
        if item:
            item.delete()

    if item:
        logger.info(f'Reindex Finished: {target.__class__.__name__}<id={id}>')
    else:
        logger.info(f'Reindex Failed: {target.__class__.__name__}<id={id}>')
