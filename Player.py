class Player(object):
    def __init__(self, name):
        self.hand = None
        self.name = name
        self.points = 1000

    def blind(self, sum_):
        self.points -= sum_

    def make_call(self, sum_):
        self.points -= sum_
        print("%s got points: %d" % (self.name, self.points))

    def make_fold(self):
        self.hand.clear()

    def make_check(self):
        print("%s got points: %d" % (self.name, self.points))

    def make_bet(self, sum_):
        self.points -= sum_
        print("%s got points: %d" % (self.name, self.points))

    def win(self, sum_):
        self.points += sum_
        print("%s win %d points, current point: %d" % (self.name, sum_, self.points))
