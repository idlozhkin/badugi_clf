import joblib
from Const import State
from poker import Card
import random
import csv
from Bot import prediction1, prediction2, upgrade_clf
from datetime import datetime
import pandas as pd
import joblib


class Game:
    def __init__(self):
        self.columns_names = ["count_change", "bank", "round_bank", "round", "win_probability", "dro", "position",
                              "answer", "choose"]
        self.temp_df = pd.DataFrame(columns=self.columns_names)
        self.count_change = -1
        self.clf = None
        self.user_clf = None
        self.deck = list(Card)
        random.shuffle(self.deck)
        self.finished_learn = [False]
        self.state = None
        self.bank = 0
        self.round_bank = 0
        self.cost = 5

    def hand_to_comb(self, hand):
        comb = [hand[0]]
        for i in range(16):
            temp_comb = [hand[j] for j in range(len(hand)) if (i & (1 << j))]
            if self.checker(temp_comb) and self.compare_comb(temp_comb.copy(), comb.copy()) == 1:
                comb = temp_comb
        return comb

    def win_probability(self, comb):
        res = 0
        mc_count = 10000
        for i in range(mc_count):
            if self.compare_comb(comb.copy(), self.hand_to_comb(random.sample(list(Card), 4)).copy()) == 1:
                res += 1
        return res / mc_count

    def set_state(self, i):
        self.state = State.values[i]
        print(self.get_state())

    def get_state(self):
        return self.state

    def betting(self, p, file_writer, turn, answer, user):
        data = []
        data += [self.count_change]
        self.count_change = (4 - len(self.hand_to_comb(p.hand)))
        data += [self.bank, self.round_bank, turn, self.win_probability(self.hand_to_comb(p.hand))]
        data += [len(self.hand_to_comb(p.hand))]
        if p.name == "p1":
            data += [1]
        else:
            data += [2]
        if answer:
            data += [1]
        else:
            data += [0]

        if user:
            # in_ = str(prediction1(data[4], len(self.hand_to_comb(p.hand)), answer, turn, data[0]))
            in_ = input("%s action (0 for check/fold, 1 for call/raise):" % p.name)
            # in_ = str(self.clf.predict([data])[0])
            # print(f"{p.name} action: {in_}")
        else:
            # in_ = str(prediction2(data[4], len(self.hand_to_comb(p.hand)), answer, turn, data[0]))
            in_ = str(self.clf.predict([data])[0])
            print(f"{p.name} action: {in_}")

        if in_ == "0":
            if self.round_bank > 0:
                p.make_fold()
            else:
                p.make_check()
            data += [0]
        else:
            if self.round_bank > 0:
                p.make_call(self.cost)
                self.round_bank += self.cost
                data[1] = self.round_bank
            else:
                p.make_bet(self.cost)
                self.round_bank += self.cost
                data[1] = self.round_bank
            data += [1]
        if user:

            self.temp_df = self.temp_df.append(pd.Series(data, index=self.columns_names), ignore_index=True)
        file_writer.writerow(data)

    def change_hand(self, p):
        for i in range(4):
            if p.hand[i] not in self.hand_to_comb(p.hand):
                p.hand[i] = self.deck.pop()
        p.hand.sort(key=lambda a: (a.suit, a.rank))

    @staticmethod
    def compare_comb(comb1, comb2):
        if len(comb1) < len(comb2):
            return 2
        if len(comb1) > len(comb2):
            return 1

        comb1.sort(key=lambda a: a.rank, reverse=True)
        comb2.sort(key=lambda a: a.rank, reverse=True)
        for i in range(len(comb1)):
            if comb1[i].rank < comb2[i].rank:
                return 1
            if comb1[i].rank > comb2[i].rank:
                return 2
        return 0

    @staticmethod
    def checker(comb):
        if not comb:
            return False
        temp = []
        for i in comb:
            if i.suit in temp:
                return False
            else:
                temp.append(i.suit)
        temp = []
        for i in comb:
            if i.rank in temp:
                return False
            else:
                temp.append(i.rank)
        return True

    def result(self, hand1, hand2):
        comb1 = self.hand_to_comb(hand1)
        comb2 = self.hand_to_comb(hand2)

        return self.compare_comb(comb1.copy(), comb2.copy())

    def start_game(self, p1, p2, first_turn, count_):  # ♠♥♦♣
        start_time = datetime.now()
        wr = [0, 0]
        with open("poker_db.csv", mode="w", encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
            file_writer.writerow(self.columns_names)
            for i in range(count_):
                self.clf = joblib.load('model.sav')
                self.count_change = -1
                self.deck = list(Card)
                random.shuffle(self.deck)
                self.bank = 2
                p1.blind(1)
                p2.blind(1)
                self.round_bank = 0

                p1.hand = [self.deck.pop() for _ in range(4)]
                p1.hand.sort(key=lambda a: (a.suit, a.rank))
                p2.hand = [self.deck.pop() for _ in range(4)]
                p2.hand.sort(key=lambda a: (a.suit, a.rank))
                if first_turn:
                    print(f"p1 hand: {p1.hand}, p1 comb: {self.hand_to_comb(p1.hand)}")
                else:
                    print(f"p2 hand: {p2.hand}, p2 comb: {self.hand_to_comb(p2.hand)}")

                for j in range(3):
                    self.set_state(2 * j)

                    self.betting(p1, file_writer, j, False, first_turn)
                    self.betting(p2, file_writer, j, True, not first_turn)
                    if not p2.hand:
                        p1.win(self.bank + self.round_bank)
                        wr[0] += 1
                        break
                    if self.round_bank == self.cost:
                        self.betting(p1, file_writer, j, True, first_turn)

                    if not p1.hand:
                        p2.win(self.bank + self.round_bank)
                        wr[1] += 1
                        break
                    self.bank += self.round_bank
                    print(f"round bank: {self.round_bank} total bank: {self.bank}")
                    self.round_bank = 0

                    self.set_state(2 * j + 1)

                    self.change_hand(p1)
                    if first_turn:
                        print(f"p1 hand: {p1.hand}, p1 comb: {self.hand_to_comb(p1.hand)}")
                    else:
                        print(f"p2 hand: {p2.hand}, p2 comb: {self.hand_to_comb(p2.hand)}")
                    self.change_hand(p2)

                if count_ > 50:
                    if i % 10 == 9 and i > 10:
                        self.user_clf = upgrade_clf(self.temp_df, self.finished_learn)
                else:
                    if i % 3 == 2 and i > 10:
                        self.user_clf = upgrade_clf(self.temp_df, self.finished_learn)

                if self.finished_learn:
                    self.clf = self.user_clf
                    filename = 'new_model.sav'
                    joblib.dump(self.clf, filename)


                if p1.hand and p2.hand:
                    if self.result(p1.hand.copy(), p2.hand.copy()) == 1:
                        wr[0] += 1
                        p1.win(self.bank)
                    else:
                        p2.win(self.bank)
                        wr[1] += 1
                print(f"score {wr[0]}:{wr[1]}")
                print(f"duration: {datetime.now() - start_time}")
