import sys

msg = 'hello world'


class A(object):

    def set(self, name):
        self.name = name

    def show(self, show_name):
        if show_name:
            print self.name
        else:
            print msg
