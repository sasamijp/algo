import random
import itertools
import card


def all_cards():
    return [card.Card(n, c) for n, c in itertools.product(list(range(12)), [0, 1])]


def all_cards_same_color():
    return [card.Card(n, 0) for n in range(12)]


def random_cards(n):
    return random.sample(all_cards(), n)
