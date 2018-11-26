# _*_ coding: utf-8 _*_

from ext import db

from models.mixin import BaseMixin
from corelib.mc import rdb, cache


MC_KEY_COLLECT_N = 'collect_n:%s:%s'


class CollectItem(BaseMixin, db.Model):
    __tablename__ = 'collect_items'
    user_id = db.Column(db.Integer)
    target_id = db.Column(db.Integer)
    target_kind = db.Column(db.Integer)

    __table_args__ = (
        db.Index('idx_ti_tk_ui', target_id, target_kind, user_id),
    )

    @classmethod
    def __flush_event__(cls, target):
        rdb.delete(MC_KEY_COLLECT_N % (target.target_id, target.target.target_kind))

    @classmethod
    @cache(MC_KEY_COLLECT_N % ('{target_id}', '{target_kind}'))
    def get_count_by_target(cls, target_id, target_kind):
        return cls.query.filter_by(target_id=target_id,
                                   target_kind=target_kind).count()

    @classmethod
    def get(cls, user_id, target_id, target_kind):
        return cls.query.filter_by(user_id=user_id, target_id=target_id,
                                   target_kind=target_kind).first()


class CollectMixin(object):
    def collect(self, user_id):
        item = CollectItem.get_by_target(user_id, self.id, self.kind)
        if item:
            return False
        CollectItem.create(user_id=user_id, target_id=self.id,
                           target_kind=self.kind)
        return True

    def uncollect(self, user_id):
        item = CollectItem.get_by_target(user_id, self.id, self.kind)
        if item:
            item.delete()   # `delete` defined in BaseMixin
            return True
        return False

    @property
    def n_collect(self):
        return CollectItem.get_count_by_target(self.id, self.kind)
