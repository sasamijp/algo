import random
from pprint import pprint

import itertools
import numpy as np
import card
import pattern_utils
import copy
import ai_algorithm as ai
from typing import List, Dict

a_win = 0
b_win = 0

'''
ai_select_action() returns dict:
{
    "actionType": "attack" or "stay",
    "attackCardID": int,
    "targetCardId": int,
    "number": int
}
'''

def ai_A_select_action(current_turn):
    ret = {"actionType": "attack",
           "attackCardID": current_turn["card_data"]["attack_card"].id}
    attackable_pos = [i for i, card in enumerate(current_turn["card_data"]["opponent_card"])
                      if not card.open]

    candidates = ai.get_candidates(current_turn)
    print("C:", len(candidates))
    attack_pattern = ai.get_attack_pattern(candidates, attackable_pos)
    #print("A:", attack_pattern)

    # 可能なアタックについて成功したターンの次の可能アタック数を計算
    scores = ai.get_attack_scores(attack_pattern, current_turn, attackable_pos)

    # 位置iについてのアタック成功確率を計算
    # probs = ai.get_i_probabilities(candidates)
    probs = ai.get_i_n_probabilities(candidates, attack_pattern)

    # それぞれのアタックについての期待値を次の可能アタック数とアタック成功確率から計算
    gains = ai.get_expect_gain(probs, attack_pattern, scores)

    print("P:", probs)
    print("S:", scores)
    #print("G:", gains)

    max_gain = max(
        [(a, g) for a, g in zip(attack_pattern, gains)
         if not current_turn["card_data"]["opponent_card"][a[0]].open],
        key=lambda t: t[1]
    )

    attack_pos = max_gain[0][0]
    attack_num = max_gain[0][1]

    #print("M:", max_gain)

    ret["targetCardID"] = current_turn["card_data"]["opponent_card"][attack_pos].id
    ret["number"] = attack_num

    return ret


def ai_B_select_action(current_turn):
    ret = {"actionType": "attack",
           "attackCardID": current_turn["card_data"]["attack_card"].id}

    candidates = get_candidates(current_turn)

    assert len(candidates) > 0

    print("C:", len(candidates))

    probs = get_i_probabilities(candidates)

    candidate = random.choice(candidates)

    # if current_turn['turn_histories']['my_number'] == 1:

    attack_pos = max(
        [(i, p) for i, p in enumerate(probs)
         if not current_turn["card_data"]["opponent_card"][i].open],
        key=lambda t: t[1]
    )[0]
    # else:
    #    attack_pos = random.choice(
    #        [i for i, c in enumerate(current_turn["card_data"]["opponent_card"]) if
    #         not c.open])

    candidate[attack_pos].id = current_turn["card_data"]["opponent_card"][attack_pos].id
    cand_card = candidate[attack_pos]

    ret["targetCardID"] = cand_card.id
    ret["number"] = cand_card.n

    return ret


# i番目の要素を選んでアタックした場合の成功確率を計算
def get_i_probabilities(candidates) -> List[float]:
    hand_size = len(candidates[0])
    return [1 / float(len(list(set([cand[i].n for cand in candidates])))) for i in range(hand_size)]


# ゲームの状態から手札の候補を計算
def get_candidates(current_turn):
    # pprint(current_turn)
    hands_size = len(current_turn["card_data"]["opponent_card"])
    opponent_ids = [c.id for c in current_turn["card_data"]["opponent_card"]]

    card_kinds = pattern_utils.all_cards()
    my_hands = [(c.n, c.c) for c in current_turn["card_data"]["my_card"]]

    card_kinds = [c for c in card_kinds
                  if (c.n, c.c) not in my_hands and
                  (c.n, c.c) != (current_turn["card_data"]["attack_card"].n,
                                 current_turn["card_data"]["attack_card"].c)
                  ]

    candidates = all_hands_pattern(hands_size, card_kinds)
    # print(1, len(candidates))

    # 相手の手札の見える分の情報から候補を削る
    for i, c in enumerate(current_turn["card_data"]["opponent_card"]):
        if c.open:
            # print(i, c.to_dict())
            candidates = [cards for cards in candidates if (cards[i].n, cards[i].c) == (c.n, c.c)]
    # print(2, len(candidates))

    # 過去のアタック失敗情報から候補を削る
    for a in current_turn["turn_histories"]["attacks"]:
        if (not a["is_succeed"]) and \
                        a["attack_player"] == current_turn["turn_histories"]["my_number"]:
            candidates = [cards for cards in candidates
                          if not cand_failed(cards, opponent_ids, a["target_id"], a["said_number"])]
    # print(3, len(candidates))

    return candidates


def cand_failed(cards, opp_ids, a_id, a_num):
    for i, c in enumerate(cards):
        if opp_ids[i] == a_id and c.n == a_num:
            return True
    return False


def all_hands_pattern(hands_count, all_cards):
    s_all = sorted(all_cards)
    all_minus = itertools.combinations(s_all, hands_count)
    return [sorted(combination) for combination in all_minus]


def deal():
    talon = pattern_utils.all_cards()
    random.shuffle(talon)
    players = [[talon.pop() for i in range(4)],
               [talon.pop() for i in range(4)]]
    return players, talon


def get_card_by_id(cards, id):
    return [i for i, card in enumerate(cards) if card.id == id][0]


def get_hidden_cards(cards):
    return [copy.copy(c).hide() for c in cards]


class Game:
    def __init__(self, players=None, talon=None):
        if players is None or talon is None:
            self.players, self.talon = deal()
        else:
            self.players, self.talon = players, talon
        self.__sort_all()
        self.at = 0

    def __is_end(self):
        global a_win, b_win
        if all(card.open for card in self.players[0]):
            b_win += 1

        if all(card.open for card in self.players[1]):
            a_win += 1

        return all(card.open for card in self.players[0]) or \
               all(card.open for card in self.players[1])

    def __apply(self, a):
        # print([c.id for c in self.players[1-self.at]])
        target_card = get_card_by_id(self.players[1 - self.at], a["targetCardID"])
        success = self.players[1 - self.at][target_card].attack(a["number"])
        attack_card = get_card_by_id(self.talon, a["attackCardID"])
        self.talon[attack_card].open = not success
        if not success:
            self.players[self.at].append(self.talon[attack_card])
            del self.talon[attack_card]
        self.__sort_all()
        attacker_was = self.at
        self.at = int(success) * self.at + int(not success) * (1 - self.at)

        attack_info = {
            "is_succeed": success,
            "attack_player": attacker_was,
            "target_id": a["targetCardID"],
            "attack_card": a["attackCardID"],
            "said_number": a["number"]
        }

        return attack_info

    def __sort_all(self):
        for i in [0, 1]:
            self.players[i].sort()

    def execute(self, randp, vervose=False):
        if vervose:
            print("simulation start:")
            print(self.talon)
            print(self.players)
            print()

        t = 0
        h = []
        while not self.__is_end():
            if vervose:
                print()
                print("talon:", len(self.talon))
                print("player0", self.players[0])
                print("player1:", self.players[1])

            if len(h) > 0 and h[-1]["is_succeed"]:
                attack_card = self.talon[get_card_by_id(self.talon, h[-1]["attack_card"])]
            else:
                attack_card = self.talon[0]

            if self.at == 0:
                a = ai_A_select_action({
                    "turn": {
                        "turn_t": t,
                        "is_mine": True,
                        "can_stay": False
                    },
                    "card_data": {
                        "my_card": self.players[self.at],
                        "opponent_card": get_hidden_cards(self.players[1 - self.at]),
                        "deck_card": self.talon[1:],
                        "attack_card": attack_card
                    },
                    "turn_histories": {
                        "attacks": h,
                        "my_number": self.at
                    }
                })
            else:
                a = ai_B_select_action({
                    "turn": {
                        "turn_t": t,
                        "is_mine": True,
                        "can_stay": False
                    },
                    "card_data": {
                        "my_card": self.players[self.at],
                        "opponent_card": get_hidden_cards(self.players[1 - self.at]),
                        "deck_card": self.talon[1:],
                        "attack_card": attack_card
                    },
                    "turn_histories": {
                        "attacks": h,
                        "my_number": self.at
                    }
                })

            if vervose:
                print("attacker:", self.at)
                print("said:", get_card_by_id(self.players[1 - self.at], a['targetCardID']), "番目が",
                      a['number'])

            h.append(self.__apply(a))

            if vervose:
                print("success:", h[-1]["is_succeed"])
            t += 1
        return t


if __name__ == "__main__":
    for i in range(100):
        p, t = deal()
        g1 = Game(players=copy.copy(p), talon=copy.copy(t))
        print(g1.execute(False, vervose=True))
        print("新しいの:", a_win, "古いの:", b_win)
        exit()
