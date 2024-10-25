import torch
from datetime import datetime, timedelta
import sqlite3

class LinkedListQueue:
    def __init__(self):
        self._head = None
        self._tail = None

    def queue(self, data):
        node = Node(data)
        if not self._head:
            self._head = node
            self._tail = node
        else:
            self._head._prev = node
            node._next = self._head
            self._head = node

    def dequeue(self):
        if not self._head:
            return None
        elif self._head == self._tail:
            node = self._head 
            self._head = None
            self._tail = None
            return node
        else:
            node = self._tail
            self._tail = node._prev
            self._tail._next = None
            node._prev = None 
            return node

    def __str__(self):
        if not self._head:
            return "Empty LL!"
        else:
            mystring = ""
            cur = self._head
            while cur != None:
                mystring += str(cur.get_data())
                if cur._next != None:
                    mystring += " -> "
                cur = cur._next
            return mystring

class Node:
    def __init__(self, data):
        self._data = data
        self._next = None
        self._prev = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Node: {str(self._data)}"

    def get_data(self):
        return self._data


class Card:
    def __init__(self, front, back):
        self._front = front
        self._back = back
        self._time_since_last_review = None
        self._interval = 0
        self._review_count = 0
        self._average_quality = 0
        self._ease = 1.1
        self._last_response_time = 0
        self._success_rate = 0
        self._char_count = len(front) + len(back)

    def get_features(self):
        return [self._time_since_last_review, self._review_count, self._average_quality, 
                self._ease, self._last_response_time, self._success_rate, self._char_count]

    def get_front(self):
        return self._front

    def get_back(self):
        return self._back

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"( Front: {self._front} ; Back: {self._back} )"


class Deck:
    def __init__(self, name):
        self._study_deck = StudyDeck(name)
        self._new_cards_deck = NewCardsDeck()
        self._review_session = 5

    def get_study_deck(self):
        return self._study_deck.get_deck()

    def get_new_cards_deck(self):
        return self._new_cards.get_deck()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._study_deck)

class StudyDeck():
    def __init__(self, name):
        self._name = name + ".db"
        self._deck = self.create_database()


    def create_database(self):
        conn = sqlite3.connect(self._name)
        c = conn.cursor()

        c.execute("""CREATE TABLE cards (
            card text,
            interval real,
            timedue real
            )""")

        conn.commit()
        conn.close()

    def get_deck(self):
        return self._deck



class NewCardsDeck():
    def __init__(self):
        self._deck = LinkedListQueue()

    def queue_card(self, card):
        self._deck.queue(card)
    
    def get_deck(self):
        return self._deck


    def next_card(self):
        return self._deck.dequeue()





def main():
    test_deck = Deck("test")
    print(test_deck.get_study_deck())

main()


    