###
#CAPP 30122 W'22: Speaker Attribution System 

#Lamont Samuels 
#Jan 2022
###
from abc import ABC, abstractmethod

class Hashtable(ABC):

    @abstractmethod
    def __getitem__(self, key):
        '''
        Similar to the get method for a Python dictionary (e.g., d["key"]), this function retrieves the value associated with the specified key in the hash table, or return the default value if it has not previously been inserted.
        '''
        pass 

    @abstractmethod
    def __setitem__(self, key, value):
        ''' 
        Similar to the set method for a Python dictionary (e.g., d["key"] = value ), this function will change the value associated with key "key" to value "val".If "key" is not currently present in the hash table, insert it with value "val".
        '''
        pass 

    @abstractmethod
    def __contains__(self, key):
        ''' 
        Similar to the contains method for a Python dictionary (e.g., "key" in d), this will return true if the key is inside the hash table; otherwise, if not then return false. 
        '''
        pass  
