###
#CAPP 30122 W'22: Speaker Attribution System 

#Lamont Samuels 
#Jan 2022
###

KEY = 0 
VAL = 1 
GROWTH_RATIO = 2 
TOO_FULL = 0.75 

from markovian.collections.hash_table import Hashtable

class LPHashtable(Hashtable):
    def __init__(self, initsize, defalutvalue):
        self._size = initsize
        self._defaultvalue = defalutvalue
        self._cells = [None] * self._size
        self.capacity = 0

    def _hash(self,key):
        multiplier = 37
        hash_value = 0 
        for c in key:
            hash_value = hash_value * multiplier + ord(c)
        return  hash_value % self._size

    def linear_probing(self,key):
        cell_index = self._hash(key)
        cell = self._cells[cell_index]
        while cell is not None and cell[0] != key:
            if cell_index < self._size - 1:
                cell_index = cell_index + 1
            else: 
                cell_index = 0
            cell = self._cells[cell_index]
        return cell_index

    def _rehash(self):
        temp = self._cells
        self._size *= GROWTH_RATIO
        self._cells = [None] * self._size
        for cell in temp:
            if cell is not None:
                key, value = cell
                cell_index = self.linear_probing(key)
                self._cells[cell_index] = (key, value)
        


    def __setitem__(self, key, value):
        cell_index = self.linear_probing(key)
        if self._cells[cell_index] is None:
            self.capacity += 1
        self._cells[cell_index] = (key,value)
        if self.capacity / self._size > TOO_FULL:
            self._rehash()


    def __getitem__(self,key):
        cell_index = self.linear_probing(key)
        if self._cells[cell_index] is not None:
            return self._cells[cell_index][1]
        else:
            return self._defaultvalue 
        
    def __contains__(self, key):
        cell_index = self.linear_probing(key)
        return self._cells[cell_index] is not None