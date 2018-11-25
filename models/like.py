# _*_ coding: utf-8 _*_

from ext import db

from models.mixin import BaseMixin
from corelib.mc import rdb, cache


MC_KEY_LIKE_N = 'like_n:%s:%s'


class LikeItem(BaseMixin, db.Model):
    __tablename__ = 'like_items'
    user_id = db.Column(db.Integer)
    target_id = db.Column(db.Integer)
    target_kind = db.Column(db.Integer)

    __table_args_ = (
        db.Index('idx_ti_tk_u_id', target_id, target_kind, user_id),
    )

    @classmethod
    def __flush_event__(cls, target):
        rdb.delete(MC_KEY_LIKE_N %(target.target_id, target.target_kind))

    @classmethod
    @cache(MC_KEY_LIKE_N % ('{target_id}', '{target_kind}'))
    def get_count_by_target(cls, target_id, target_kind):
        return cls.query.filter_by(target_id=target_id,
                                   target_kind=target_kind).count()

    @classmethod
    def get(cls, user_id, target_id, target_kind):
        return cls.query.filter_by(user_id=user_id, target_id=target_id,
                                   target_kind=target_kind).first()


class LikeMixin(object):
    def like(self, user_id):
        item = LikeItem.get_by_target(user_id, self.id, self.kink)
        if item:
            return False
        LikeItem.create(user_id=user_id, target_id=self.id,
                        target_kind=self.kind)
        return True

    def unlike(self, user_id):
        item = LikeItem.get_by_target(user_id, self.id, self.kind)
        if item:
            item.delete()
            return True
        return False

    @property
    def n_likes(self):
        return LikeItem.get_count_by_target(self.id, self.kind)
