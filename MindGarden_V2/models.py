from datetime import datetime, timedelta
import sqlite3
import time

GLOBAL_EASE = 1

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
            return node._data
        else:
            node = self._tail
            self._tail = node._prev
            self._tail._next = None
            node._prev = None 
            return node._data

    def is_empty(self):
        return self._head == None

    def __len__(self):
        if not self._head:
            return 0
        else:
            i = 0
            cur = self._head
            while cur != None:
                i += 1
                cur = cur._next
            return i

    def __repr__(self):
        return self.__str__()

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

class User:
    def __init__(self):
        self._name = ""
        self._join_date = datetime.now()
        self._deck_collection = {}
        self._stats = UserStats()
    
    def add_deck(self, deck):
        if not deck.get_name() in self._deck_collection:
            self._deck_collection[deck.get_name()] = deck
            self._stats.add_deck_stats(deck)
        else:
            print("A deck with that name already exists! Try another name.")

class UserStats:
    def __init__(self, user):
        self._deck_stats = {}
    
    def add_deck_stats(self, deck):
        self._deck_stats[deck.get_name()] = deck.stats()

class DeckStats:
    def __init__(self):
        self._date_added = time.time()
        self._total_reviews = 0
        self._time_studied = 0
        self._quality_rate = 0

class CardStats:
    def __init__(self, card):
        self._date_added = time.time()
        self._last_review_time = 0
        self._interval = 1 
        self._next_due = None
        self._review_count = 0
        self._difficulty_sum = 0
        self._ease = 1.69
        self._response_time_sum = 0
        self._very_easy_count = 0
        self._char_count = len(card.get_front()) + len(card.get_back())

    def update_stats(self, start_time, end_time, difficulty):
        self.set_last_review_time(start_time)

        self.sm2(difficulty)
        self._review_count += 1
        self._difficulty_sum += difficulty
        self._response_time_sum += (end_time - start_time)
        if difficulty == 1:
            self._very_easy_count += 1

        self.set_next_due(start_time)
    
    def sm2(self, difficulty):
        if difficulty <= 3:
            if self._review_count == 0:
                self._interval = 1
            elif self._review_count == 1:
                self._interval = 3
            else:
                self.interval = round(self.interval * self._ease)
        # Update ease factor
        self._ease += (0.1 - (difficulty - 1) * (0.08 + (difficulty - 1) * 0.02))
        self._ease = max(0.3, self._ease)  
        

    
    def set_last_review_time(self, date):
        self._last_review_time = date
    
    def set_next_due(self, start_time):
        cur_date = datetime.fromtimestamp(start_time)
        self._next_due = (cur_date + timedelta(days=self._interval)).strftime("%Y-%m-%d")

    def get_average_difficulty(self):
        return (self._difficulty_sum / self._review_count) if self._review_count > 0 else None
    
    def get_avg_response_time(self):
        return round((self._response_time_sum / self._review_count), 1) if self._review_count > 0 else None
    
    def get_success_rate(self):
        return ((self._very_easy_count / self._review_count) * 100) if self._review_count > 0 else None

    def get_time_since_last_review(self):
        secs = time.time() - self._last_review_time
        return round((secs / 1440), 4)

    def get_next_due(self):
        return self._next_due


    def get_stats(self):
        stats = {
            "Date Added": datetime.fromtimestamp(self._date_added).strftime("%Y-%m-%d"),
            "Last Review Date": datetime.fromtimestamp(self._last_review_time).strftime("%Y-%m-%d"),
            "Hours Since Last Review": self.get_time_since_last_review(),
            "Interval": self._interval,
            "Next Due": self._next_due,
            "Review Count": self._review_count,
            "Average Difficulty": self.get_average_difficulty(),
            "Ease": self._ease,
            "Average Response Time": str(self.get_avg_response_time()) + " seconds",
            "Success Rate (%)": self.get_success_rate(),
            "Character Count": self._char_count
        }
        return stats
        

class Card():
    def __init__(self, card_type="basic"):
        self._type = card_type
        self._reversed_card = None
        self._front = ""
        self._back = ""
        self._deck = None
        self._stats = CardStats(self)

    def update_stats(self, start_time, end_time, difficulty):
        self._stats.update_stats(start_time, end_time, difficulty)

    def set_type(self, mytype):
        if mytype.lower() == "basic and reversed":
            self._reversed_card = Card('reversed')

    def set_front(self, front):
        self._front = front

        if self._reversed_card:
            self._reversed_card.set_back(front)
    
    def set_back(self, back):
        self._back = back

        if self._reversed_card:
            self._reversed_card.set_front(back)
    
    def set_deck(self, deck):
        self._deck = deck
    
    def get_stats(self):
        return self._stats.get_stats()
    
    def get_next_due(self):
        return self._stats.get_next_due()

    def get_reversed_card(self):
        return self._reversed_card

    def get_front(self):
        return self._front

    def get_back(self):
        return self._back

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"( Front: {self._front} | Back: {self._back} )"


class Deck(DeckStats):
    def __init__(self, name):
        self._name = name
        self._study_deck = StudyDeck()
        self._new_cards_deck = NewCardsDeck()
        self._max_new = 3
        self._stats = DeckStats()

    def add_card(self, card):
        self._new_cards_deck.queue_card(card)
        if card.get_reversed_card():
            self._new_cards_deck.queue_card(card.get_reversed_card())

    def study(self):
        review_queue = self.create_review_queue()
        session_start = time.time()
        print(session_start)
        review_count = 0
        while not review_queue.is_empty():
            cur_card = review_queue.dequeue()
            start_time = time.time()
            print("+---------------------------------------------------------+")
            print("                                                          |")
            print(f"Card Front:\n\n{cur_card.get_front()}\n")
            print("                                                          |")
            print("+---------------------------------------------------------+")

            user_input = input()
            if user_input == "":
                print("+---------------------------------------------------------+")
                print("                                                          |")
                print(f"Card Back\n\n{cur_card.get_back()}\n")
                print("                                                          |")
                print("+---------------------------------------------------------+")
            elif user_input == "BREAK":
                break
            
            difficulty = int(input("How hard was that card? (1-5): "))
            if difficulty >= 4:
                review_queue.queue(cur_card)
            else:
                end_time = time.time()
                cur_card.update_stats(start_time, end_time, difficulty)
                review_count += 1
                self._study_deck.add_card(cur_card.get_next_due(), cur_card)
        
        session_end = time.time()
        print("You are done reviewing this deck for today!")
    
    def create_review_queue(self):
        date = datetime.now().isoformat().split("T")[0]
        
        if date in self._study_deck:
            study_queue = self._study_deck.get_deck()[date]
        else:
            study_queue = LinkedListQueue()

        ratio = max(len(study_queue) // (min(self._max_new, len(self._new_cards_deck.get_deck()))), 1)


        cur_review_queue = LinkedListQueue()
        for _ in range(self._max_new):
            if self._new_cards_deck.get_deck().is_empty():
                break
            else:
                cur_review_queue.queue(self._new_cards_deck.get_deck().dequeue())
                i = 0
                while i < ratio and not study_queue.is_empty():
                    cur_review_queue.queue(study_queue.dequeue())
                    i += 1

        while not study_queue.is_empty():
            cur_review_queue.queue(study_queue.dequeue())

        return cur_review_queue


    def get_stats(self):
        return self._stats

    def get_name(self):
        return self._name

    def get_study_deck(self):
        return self._study_deck

    def get_new_cards_deck(self):
        return self._new_cards_deck

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._study_deck) + "| " + str(self._new_cards_deck)

class StudyDeck():
    def __init__(self):
        self._deck = {}

    def add_card(self, due_date, card):
        if due_date not in self._deck:
            self._deck[due_date] = LinkedListQueue()
        self._deck[due_date].queue(card)

    def get_deck(self):
        return self._deck

    def __contains__(self, other):
        return other in self._deck
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self._deck)

class NewCardsDeck():
    def __init__(self):
        self._deck = LinkedListQueue()

    def queue_card(self, card):
        self._deck.queue(card)
    
    def get_deck(self):
        return self._deck

    def next_card(self):
        return self._deck.dequeue()

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "New Cards " + str(self._deck)



def test():
    test_deck = Deck("test")

    d = Card()

    test_deck.add_card(d)

    for i in range(5):
        c = Card()
        c.set_type("basic and reversed")
        c.set_front(i)
        c.set_back(i * i)
        test_deck.add_card(c)

    
    
    test_deck.study()
    return d, test_deck


def main():
    card, deck = test()
    h = input()
    print(card.get_stats())
    print(deck.get_study_deck())
    
    

main()


    