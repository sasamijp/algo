
class Card:
    def __init__(self,
                 number,
                 color,
                 id_=None,
                 open=False):
        self.n = number
        self.c = color
        self.open = open
        self.id = id
        if id_ is None:
            self.id = int(id(self))

    def __lt__(self, other):
        if other.n == self.n:
            return self.c < other.c
        return self.n < other.n

    def __repr__(self):
        color = "w"
        open = "c"
        if self.c == 1:
            color = "b"
        if self.open:
            open = "o"
        return str(self.n) + color + open

    def to_dict(self):
        return {
            "number": self.n,
            "color": self.c,
            "open": self.open,
            "id": self.id
        }

    def attack(self, num):
        if num == self.n:
            self.open = True
            return True
        return False

    def hide(self):
        if not self.open:
            self.n = None
        return self
