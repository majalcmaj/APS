class MethodAccessedTuple:
    def __init__(self, val1, val2):
        self._val1 = val1
        self._val2 = val2

    @property
    def val1(self):
        return self._val1

    @property
    def val2(self):
        return self._val2

    def __str__(self):
        return "(" + str(self._val1) + ", " + str(self._val2) + ")"
