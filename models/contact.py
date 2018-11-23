# _*_ coding: utf-8 _*_

from ext import db

from models.mixin import BaseMixin


class Contact(BaseMixin, db.Model):
    __tablename__ = 'contacts'
    to_id = db.Column(db.Integer)
    from_id = db.Column(db.Integer)

    __table_args__ = (
        db.UniqueConstraint('from_id', 'to_id', name='uk_from_to'),
        db.Index('idx_to_time_from', to_id, 'created_at', from_id),
        db.Index('idx_time_to_from', 'created_at', to_id, from_id),
    )


class userFollowState(BaseMixin, db.Model):
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)

    __table_args_ = {
        'mysql_charset': 'utf8'
    }
    