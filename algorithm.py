""" 
Algorithm for sending the right data to the frontend. 
State is stored in the db.
Query db, retrieve user data. Sort the user data according to the algorithm. 
"""
from random import shuffle

class Algorithm:
    def __init__(self,data) -> None:
        self.data = data
        shuffle(self.data)
        self.n = 0
        self.maxlen = len(self.data)
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.n < self.maxlen:
            item = self.data[self.n]
            self.n += 1
            return item
        else:
            raise StopIteration
