class State:
    values = ['first_buy', 'first_change', 'second_buy', 'second_change', 'third_buy', 'third_change']

    def get_value(self, i):
        return self.values[i]


class Action:
    values = ['pass', 'raise']

    def get_value(self, i):
        return self.values[i]
