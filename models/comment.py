# _*_ coding: utf-8 _*_


class CommentMixin(object):

    def add_comment(self):
        pass

    def del_comment(self):
        pass

    def get_comments(self):
        pass

    @pcache()
    def _get_comments(self):
        pass

    @property
    def n_comments(self):
        pass

    @cache()
    def get_n_comments(self):
        pass
