'''
CAPP 30122 W'21: Markov models and hash tables

Lamont Samuels 
Jan 2022
'''

HASH_CELLS = 57

import math

from markovian.collections.lp import LPHashtable

class Markov:

    def __init__(self, k, s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.k = k
        self.s = s
        self.hashtable = LPHashtable(HASH_CELLS,0)
        self.tract_frequecies()
    
    def tract_frequecies(self):
        for i in range(len(self.s)):
            if i + self.k > len(self.s):
                k_string = self.s[i:] + self.s[:i + self.k - len(self.s)]
            else:
                k_string = self.s[i:i+self.k]
            if i + self.k+ 1 > len(self.s):
                k_plus_one_string = self.s[i:] + self.s[:i + self.k+1 - len(self.s)]
            else:
                k_plus_one_string = self.s[i:i+self.k+1]

            self.hashtable[k_string] += 1
            self.hashtable[k_plus_one_string] += 1 

        
    def log_probability(self, s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        '''

        log = 0
        for i in range(len(s)): # s
            if i + self.k > len(s):
                k_string = s[i:] + s[:i + self.k - len(s)]
            else:
                k_string = s[i:i+self.k]
            if i + self.k+ 1 > len(s):
                k_plus_one_string = s[i:] + s[:i + self.k+1 - len(s)]
            else:
                k_plus_one_string = s[i:i+self.k+1]
            M = self.hashtable[k_plus_one_string]
            N = self.hashtable[k_string]
            S = len(set(self.s))
            log += math.log((M+1)/(N+S))
        return log
        
            

            
def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the normalized log probabilities of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    speaker1 = Markov(order, speech1)
    speaker2 = Markov(order, speech2)

    likelihood1 = speaker1.log_probability(speech3)/len(speech3)
    likelihood2 = speaker2.log_probability(speech3)/len(speech3)

    if likelihood1 > likelihood2:
        conclusion = "A"
    else:
        conclusion = "B"

    return (likelihood1, likelihood2, conclusion)
