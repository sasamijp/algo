import itertools
import copy
import random

import pattern_utils
import card

import pprint
from typing import List

cache = []


def cache_exist(hands_count, card_kinds):
    for t in cache:
        if len(card_kinds) != len(t[1]):
            continue
        # print(hands_count, t[0], card_kinds, t[1])
        if t[0] == hands_count and \
                all((c.c, c.n) == (t[1][i].c, t[1][i].n) for i, c in enumerate(card_kinds)):
            print("exist!!!!!!!!!!")
            return t[2]
    return False


def cand_failed(cards, opp_ids, a_id, a_num):
    for i, c in enumerate(cards):
        if opp_ids[i] == a_id and c.n == a_num:
            return True
    return False


# i番目の要素を選んでアタックした場合の成功確率を計算
def get_i_probabilities(candidates) -> List[float]:
    hand_size = len(candidates[0])
    return [1 / float(len(list(set([cand[i].n for cand in candidates])))) for i in range(hand_size)]


# ゲームの状態から手札の候補を計算
def get_candidates(current_turn, randp):
    #pprint.pprint(current_turn["card_data"]["opponent_card"])
    hands_size = len(current_turn["card_data"]["opponent_card"])
    opponent_ids = [c.id for c in current_turn["card_data"]["opponent_card"]]

    card_kinds = pattern_utils.all_cards()
    my_hands = [(c.n, c.c) for c in current_turn["card_data"]["my_card"]]
    # opens = [(c.n, c.c) for c in current_turn["card_data"]["opponent_card"] if c.open]

    card_kinds = [c for c in card_kinds
                  if (c.n, c.c) not in my_hands and
                  (c.n, c.c) != (current_turn["card_data"]["attack_card"].n,
                                 current_turn["card_data"]["attack_card"].c)
                  ]
    # cache_ = cache_exist(hands_size, card_kinds)

    # if cache_:
    #    candidates = cache_
    # else:
    candidates = all_hands_pattern(hands_size, card_kinds)
    # cache.append((hands_size, card_kinds, candidates))

    # 相手の手札の見える分の情報から候補を削る
    for i, c in enumerate(current_turn["card_data"]["opponent_card"]):
        if c.open:
            candidates = [cards for cards in candidates if (cards[i].n, cards[i].c) == (c.n, c.c)]

    # 過去のアタック失敗情報から候補を削る
    for a in current_turn["turn_histories"]["attacks"]:
        if (not a["is_succeed"]) and \
                        a["attack_player"] == current_turn["turn_histories"]["my_number"]:
            candidates = [cards for cards in candidates
                          if not cand_failed(cards, opponent_ids, a["target_id"], a["said_number"])]
    #pprint.pprint(candidates)
    return candidates


def all_hands_pattern(hands_count, all_cards):
    s_all = sorted(all_cards)
    all_minus = itertools.combinations(s_all, hands_count)
    return [sorted(combination) for combination in all_minus]


def mc(cdicts):
    return [card.Card(d["number"], d["color"], open=d["open"], id_=d["id"]) for d in cdicts]


def get_hidden_cards(cards):
    return [copy.copy(c).hide() for c in cards]


if __name__ == '__main__':
    cache = [(5, mc([{'number': 2, 'color': 0, 'id': 4392177504, 'open': False},
                     {'number': 4, 'color': 0, 'id': 4393021568, 'open': False},
                     {'number': 4, 'color': 1, 'id': 4393021624, 'open': False},
                     {'number': 9, 'color': 1, 'id': 4393022184, 'open': False},
                     {'number': 11, 'color': 1, 'id': 4393022408, 'open': True}])),
             (4, mc([{'number': 2, 'color': 0, 'id': 4392177504, 'open': False},
                     {'number': 4, 'color': 0, 'id': 4393021568, 'open': False},
                     {'number': 2, 'color': 1, 'id': 4393021624, 'open': False},
                     {'number': 9, 'color': 1, 'id': 4393022184, 'open': False},
                     {'number': 11, 'color': 1, 'id': 4393022408, 'open': True}]))]
    print(cache_exist(4, mc([{'number': 2, 'color': 0, 'id': 4392177504, 'open': False},
                             {'number': 4, 'color': 0, 'id': 4393021568, 'open': False},
                             {'number': 20000, 'color': 1, 'id': 4393021624, 'open': False},
                             {'number': 9, 'color': 1, 'id': 4393022184, 'open': False},
                             {'number': 11, 'color': 1, 'id': 4393022408, 'open': True}]))
          )
    exit()
    (get_candidates({
        "turn": {
            "turn_t": 0,
            "is_mine": True,
            "can_stay": False
        },
        "card_data": {
            "my_card": mc([{'number': 2, 'color': 0, 'id': 4392177504, 'open': False},
                           {'number': 4, 'color': 0, 'id': 4393021568, 'open': False},
                           {'number': 4, 'color': 1, 'id': 4393021624, 'open': False},
                           {'number': 9, 'color': 1, 'id': 4393022184, 'open': False},
                           {'number': 11, 'color': 1, 'id': 4393022408, 'open': True}]),
            "opponent_card": get_hidden_cards(mc(
                [{'number': 0, 'color': 0, 'id': 4379149424, 'open': True},
                 {'number': None, 'color': 1, 'id': 4393021512, 'open': False},
                 {'number': None, 'color': 1, 'id': 4393021960, 'open': False},
                 {'number': None, 'color': 0, 'id': 4393022240, 'open': False},
                 {'number': None, 'color': 0, 'id': 4393022352, 'open': False}])),
            "deck_card": [],
            "attack_card": []
        },
        "turn_histories": {
            "attacks": [(0, 4393021512, 0, False), (1, 4393022408, 0, True)],
            "my_number": 1

        }
    }))
    '''
{'turn': {'can_stay': False, 'is_mine': True, 'turn_t': 2}, 'card_data': {'deck_card': [1wc, 5bc, 9wc, 6bc, 2bc, 5wc, 3wc, 8wc, 8bc, 7wc, 10bc, 6wc, 0bc], 'attack_card': 1bc, 'my_card': [2wc, 4wc, 4bc, 9bc, 11bo], 'opponent_card': [0wo, Nonebc, Nonebc, Nonewc, Nonewc]}, 'turn_histories': {'my_number': 1, 'attacks': [(0, 4393021512, 0, False), (1, 4393022408, 0, True)]}}
'''
