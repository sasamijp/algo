import random
import numpy as np
import card
import pattern_utils as util
import copy
import ai

a_win=0
b_win=0

'''
ai_select_action() returns dict:
{
    "actionType": "attack" or "stay",
    "attackCardID": int,
    "targetCardId": int,
    "number": int
}
'''


def ai_select_action(current_turn, randp):
    print(current_turn)
    ret = {"actionType": "attack",
           "attackCardID": current_turn["card_data"]["attack_card"].id}
    attackable_cards = [card for card in current_turn["card_data"]["opponent_card"] if
                        not card.open]

    # print(ai.candidates(current_turn))
    candidates = ai.get_candidates(current_turn, randp)

    probs = ai.get_i_probabilities(candidates)

    candidate = random.choice(candidates)
    # print(probs)
    # print([(i, p) for i, p in enumerate(probs)
    #     if not current_turn["card_data"]["opponent_card"][i].open])

    if current_turn['turn_histories']['my_number'] == 1:

        attack_pos = max(
            [(i, p) for i, p in enumerate(probs)
             if not current_turn["card_data"]["opponent_card"][i].open],
            key=lambda t: t[1]
        )[0]
    else:
        attack_pos = random.choice([i for i, c in enumerate(current_turn["card_data"]["opponent_card"]) if
                      not c.open])
    # print(attack_pos)

    # if randp:
    #     choose = random.choice([(c, pos) for pos, c in enumerate(random.choice(candidates))
    #                             if not current_turn["card_data"]["opponent_card"][pos].open])
    # else:
    #     ppp = 0
    #     if current_turn["turn"]["turn_t"] / 2 % 2 == 0:
    #         ppp = -1
    #     # print(ppp)
    #     choose = [(c, pos) for pos, c in enumerate(random.choice(candidates))
    #               if not current_turn["card_data"]["opponent_card"][pos].open][ppp]
    #

    candidate[attack_pos].id = current_turn["card_data"]["opponent_card"][attack_pos].id
    cand_card = candidate[attack_pos]

    # print("cand_card:", cand_card.to_dict())
    # ret["targetCardID"] = attackable_cards[0].id
    ret["targetCardID"] = cand_card.id
    ret["number"] = cand_card.n
    # print("opponent:", [card.id for card in current_turn["card_data"]["opponent_card"]])

    return ret


def deal():
    talon = util.all_cards()
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
            a_win += 1

        if all(card.open for card in self.players[1]):
            b_win += 1

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

            a = ai_select_action({
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
            }, randp)
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
        print(a_win, b_win)
        #exit()
