# _*_ coding: utf-8 _*_

from marshmallow import Schema, fields


class PostSchema(Schema):
    id = fields.Str()
    n_likes = fields.Integer()
    n_comments = fields.Integer()
    n_collects = fields.Integer()
    is_liked = fields.Boolean()
    is_commented = fields.Boolean()
    is_collected = fields.Boolean()
    html = fields.Str()     # for comment


class AuthorSchema(Schema):
    id = fields.Str()
    bio = fields.Str()
    name = fields.Str()
    avatar_path = fields.Str()