import sys


# 自定义异常类型
class ParamError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UndefineError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)