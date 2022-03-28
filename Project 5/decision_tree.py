'''
CAPP30122 W'22: Building decision trees

Siwen Chen
'''

import math
import sys
import pandas as pd
import numpy as np

class Node():
    '''
    A Node is used to partition a dataset.
    
    '''
    def __init__(self, data = None, labels = None):
        '''
        The constructor 
        '''
        self.data = data
        self.labels = labels
        self.gini = self._gini_index(self.labels)
        self.split_attr = None
        self.split_attr_val = None
        self.children = []
        self.is_leaf = self.gini == 0
        
    def find_best_split(self):
        '''
        Find the best attribte by iterating over every attribute
        value and calculating the gini ratio
        '''
        if self.is_leaf or len(self.data.columns) == 0  or len(self.data.drop_duplicates()) == 1:
            return
        
        gain_ratios = self._gain_ratios()
        if gain_ratios[0][1] == 0:
            return
        self.split_attr = gain_ratios[0][0]
        
        for attr_val in self.data[gain_ratios[0][0]].unique():
            mask = self.data[gain_ratios[0][0]] == attr_val
            child_data = self.data[mask].drop(columns = [gain_ratios[0][0]])
            child_labels = self.labels[mask]
            child_node = Node(child_data, child_labels)
            child_node.split_attr_val = attr_val
            self.children.append(child_node)
            
    def predict(self, row):
        '''
        Predict the class label given each row
        '''
        for child in self.children:
            if child.split_attr_val == row[self.split_attr]:
                return child.predict(row)
        return self._class_label()
        
    def _gini_index(self, labels):
        '''
        Calculate the gini-index to get the impurity
        Input : labels
        Output: gini_index
        '''
        counter = labels.value_counts()
        total = sum(counter)
        gini_index = 1 - ((counter / total) ** 2).sum()

        return gini_index
    
    def _split_info(self, values):
        '''
        Calculate the split information for that attribute
        Input: values in the attribute
        Output: split_info
        
        '''
        counter = values.value_counts()
        total = sum(counter)
        split_info = -((counter / total) * np.log2(counter / total)).sum()
        return split_info
    
    def _gain_ratios(self):
        '''
        Calculate the gain ratio for by 
        having parent ration minus the weighted ratio,
        and divided by split_info
        '''
        ratios = []
        for attr in self.data.columns:
            split_info = self._split_info(self.data[attr])
            weighted_gini = 0
            for attr_value in self.data[attr].unique():
                indexs = self.data.index[self.data[attr] == attr_value]
                gini = self._gini_index(self.labels[indexs])
                weighted_gini += gini * len(indexs) / len(self.data)
            if split_info == 0:
                gain_ratio = 0
            else:
                gain_ratio = (self.gini - weighted_gini) / split_info
            ratios.append((attr, gain_ratio))
        return sorted(ratios, key=lambda x: (-x[1], x[0]))
    
    def _class_label(self):
        '''
        Deals with the situation that count the attribute value that happens
        must often, when the number is the same return the class label 
        according to the natural ordering of string. 
        '''
        counter = list(self.labels.value_counts().items())
        counter = sorted(counter, key = lambda x: (-x[1], x[0]))[0]
        return counter[0]

class Tree():
    '''
    The tree class process the data, 
    build a tree and predict the classification label
    '''
    def __init__(self, data, labels):
        '''
        The constructor 
        '''
        self.root = Node(data, labels)
        self.build_tree(self.root)
        
    def build_tree(self, node):
        '''
        build the tree according to algorithm we built
        '''
        node.find_best_split()
        for child in node.children:
            self.build_tree(child)
    
    def predict(self, row):
        '''
        identify the label
    
        '''
        return self.root.predict(row)
            
        
    
def go(training_filename, testing_filename):
    '''
    Construct a decision tree using the training data and then apply
    it to the testing data.

    Inputs:
      training_filename (string): the name of the file with the
        training data
      testing_filename (string): the name of the file with the testing
        data

    Returns (list of strings or pandas series of strings): result of
      applying the decision tree to the testing data.
    '''

    # replace return with a suitable return value
    # and remove this comment!
    
    df_train = pd.read_csv(training_filename,dtype=str)
    train_data = df_train.iloc[:,:-1]
    train_labels = df_train.iloc[:,-1]
    tree = Tree(train_data, train_labels)
    df_test = pd.read_csv(testing_filename,dtype=str)
    testing_data = df_test.iloc[:,:-1]
    testing_labels = df_test.iloc[:,-1]
    
    pred = testing_data.apply(tree.predict,axis=1)
    
    return pred

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 {} <training filename> <testing filename>".format(
            sys.argv[0]))
        sys.exit(1)

    for result in go(sys.argv[1], sys.argv[2]):
        print(result)
