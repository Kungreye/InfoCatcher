# _*_ coding: utf-8 _*_

from ext import db

from models.mixin import BaseMixin
from corelib.mc import rdb, cache


MC_KEY_CONTACT_N = 'contact_n:%s:%s'


class Contact(BaseMixin, db.Model):
    __tablename__ = 'contacts'
    to_id = db.Column(db.Integer)
    from_id = db.Column(db.Integer)

    __table_args__ = (
        db.UniqueConstraint('from_id', 'to_id', name='uk_from_to'),
        db.Index('idx_to_time_from', to_id, 'created_at', from_id),
        db.Index('idx_time_to_from', 'created_at', to_id, from_id),
    )

    @classmethod
    def __flush_event__(cls, target):
        rdb.delete(MC_KEY_CONTACT_N % (target.target_id, target.target_kind))

    @classmethod
    @cache(MC_KEY_CONTACT_N % ('{target_id}', '{target_kind}'))
    def get_count_by_target(cls, target_id, target_kind):
        return cls.query.filter_by(target_id=target_id,
                                   target_kind=target_kind).count()

    @classmethod
    def get(cls, user_id, target_id, target_kind):
        return cls.query.filter_by(user_id=user_id, target_id=target_id,
                                   target_kind=target_kind).first()


class userFollowState(BaseMixin, db.Model):
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)

    __table_args_ = {
        'mysql_charset': 'utf8'
    }
