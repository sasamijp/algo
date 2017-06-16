import itertools
import copy
import random

import pattern_utils
import card

from pprint import pprint
from typing import List


def cand_failed(cards, opp_ids, a_id, a_num):
    for i, c in enumerate(cards):
        if opp_ids[i] == a_id and c.n == a_num:
            return True
    return False


# i番目の要素を選んでアタックした場合の成功確率を計算
def get_i_probabilities(candidates) -> List[float]:
    hand_size = len(candidates[0])
    return [1 / float(len(list(set([cand[i].n for cand in candidates])))) for i in range(hand_size)]


def get_i_n_probabilities(candidates, attack_patterns):
    probs = [None] * len(attack_patterns)
    for i, a in enumerate(attack_patterns):
        probs[i] = 0
        for c in candidates:
            if c[a[0]].n == a[1]:
                probs[i] += 1
        probs[i] /= len(candidates)
    return probs


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


# 上の関数の引数をまともにしたやつ(本当はひとつにまとめたい)
def get_candidates_(opponent_cards,
                    my_cards,
                    attack_card,
                    history,
                    my_number):
    hands_size = len(opponent_cards)
    opponent_ids = [c.id for c in opponent_cards]

    card_kinds = pattern_utils.all_cards()
    my_hands = [(c.n, c.c) for c in my_cards]

    card_kinds = [c for c in card_kinds
                  if (c.n, c.c) not in my_hands and
                  (c.n, c.c) != (attack_card.n,
                                 attack_card.c)]

    candidates = all_hands_pattern(hands_size, card_kinds)
    # print(1, len(candidates))
    # 相手の手札の見える分の情報から候補を削る
    # pprint(opponent_cards)
    # pprint(my_cards)
    # pprint(card_kinds)
    # pprint(candidates)
    for i, c in enumerate(opponent_cards):
        if c.open:
            # 頼む
            color = c.c
            if (c.n, c.c) in my_hands:
                color = copy.copy(1 - c.c)
            candidates = [cards for cards in candidates if (cards[i].n, cards[i].c) == (c.n, color)]
    # print(2, len(candidates))
    # 過去のアタック失敗情報から候補を削る
    for a in history:
        if (not a["is_succeed"]) and \
                        a["attack_player"] == my_number:
            candidates = [cards for cards in candidates
                          if not cand_failed(cards, opponent_ids, a["target_id"], a["said_number"])]
    # print(3, len(candidates))
    return candidates


def get_attack_pattern(candidates, attackable_i):
    # hand_size = len(candidates[0])
    attacks = []
    for i in attackable_i:
        attacks += [(i, n) for n in list(set([cand[i].n for cand in candidates]))]
    return attacks


def get_attack_scores(attack_pattern, current_turn, attackable_pos):
    scores = [None] * len(attack_pattern)
    for i, a in enumerate(attack_pattern):
        # print(a, "をやった場合")
        # print("成功した場合次の可能アタック分岐")
        c_s = get_succeed_turn_candidates(current_turn,
                                          a[0],
                                          a[1])
        # print(c)

        # print(len(get_attack_pattern(c, attackable_pos)))
        # print("失敗した場合次の可能アタック分岐")
        c_f = get_failed_turn_candidates(current_turn,
                                         a[0],
                                         a[1])
        # print(len(get_attack_pattern(c,
        #                             attackable_pos)))
        # print()

        scores[i] = score(
            len(get_attack_pattern(c_s, attackable_pos)),
            len(get_attack_pattern(c_f, attackable_pos))
        )
    return scores


def score(success_gain: int, fail_gain: int) -> float:
    return success_gain


# current_turnでopponentのiにnumberでattackしたときに失敗した場合の候補を計算
def get_failed_turn_candidates(current_turn, i, number):
    opponent_cards = current_turn["card_data"]["opponent_card"]
    my_cards = current_turn["card_data"]["my_card"]
    attack_card = current_turn["card_data"]["attack_card"]
    history = current_turn["turn_histories"]["attacks"] + [{
        "is_succeed": False,
        "attack_player": current_turn["turn_histories"]["my_number"],
        "target_id": current_turn["card_data"]["opponent_card"][i].id,
        "said_number": number
    }]
    return get_candidates_(opponent_cards,
                           my_cards,
                           attack_card,
                           history,
                           current_turn["turn_histories"]["my_number"])


# 成功した場合の候補
def get_succeed_turn_candidates(current_turn, i, number):
    opponent_cards = copy.deepcopy(current_turn["card_data"]["opponent_card"])
    opponent_cards[i].open = True
    opponent_cards[i].n = number
    my_cards = current_turn["card_data"]["my_card"]
    attack_card = current_turn["card_data"]["attack_card"]
    history = current_turn["turn_histories"]["attacks"]
    return get_candidates_(opponent_cards,
                           my_cards,
                           attack_card,
                           history,
                           current_turn["turn_histories"]["my_number"])


# アタックした後に候補がどのくらい減るのかの期待値を計算
def get_expect_gain(probs, attack_patterns, scores):
    assert len(attack_patterns) == len(scores) == len(probs)
    current_gain = len(attack_patterns)
    return [p * (current_gain - s) * int(s != 0)
            for a, s, p in zip(attack_patterns, scores, probs)]


def all_hands_pattern(hands_count, all_cards):
    s_all = sorted(all_cards)
    all_minus = itertools.combinations(s_all, hands_count)
    return [sorted(combination) for combination in all_minus]


def mc(cdicts):
    return [card.Card(d["number"], d["color"], open=d["open"], id_=d["id"]) for d in cdicts]


def get_hidden_cards(cards):
    return [copy.copy(c).hide() for c in cards]


def ai_select_action(current_turn):
    ret = {"actionType": "attack",
           "attackCardID": current_turn["card_data"]["attack_card"].id}

    candidates = get_candidates(current_turn)

    assert len(candidates) > 0

    probs = get_i_probabilities(candidates)

    candidate = random.choice(candidates)

    if current_turn['turn_histories']['my_number'] == 1:

        attack_pos = max(
            [(i, p) for i, p in enumerate(probs)
             if not current_turn["card_data"]["opponent_card"][i].open],
            key=lambda t: t[1]
        )[0]
    else:
        attack_pos = random.choice(
            [i for i, c in enumerate(current_turn["card_data"]["opponent_card"]) if
             not c.open])

    candidate[attack_pos].id = current_turn["card_data"]["opponent_card"][attack_pos].id
    cand_card = candidate[attack_pos]

    ret["targetCardID"] = cand_card.id
    ret["number"] = cand_card.n

    return ret
