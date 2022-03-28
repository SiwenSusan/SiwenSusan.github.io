'''
Linking restaurant records in Zagat and Fodor's list using restraurant
names, cities, and street addresses.

Siwen Chen

'''
import csv
import jellyfish
import pandas as pd
import util
from util import get_jw_category

zagat_filename = "data/zagat.csv"
fodors_filename = "data/fodors.csv"
known_links_filename = "data/known_links.csv"
unmatch_pairs_filename  = "data/unmatch_pairs.csv"

zagat = pd.read_csv(zagat_filename)
fodor = pd.read_csv(fodors_filename)
known = pd.read_csv(known_links_filename)
unmatch = pd.read_csv(unmatch_pairs_filename)

def find_matches(output_filename, mu, lambda_, block_on_city=False):
    '''
    Put it all together: read the data and apply the record linkage
    algorithm to classify the potential matches.

    Inputs:
      output_filename (string): the name of the output file,
      mu (float) : the maximum false positive rate,
      lambda_ (float): the maximum false negative rate,
      block_on_city (boolean): indicates whether to block on the city or not.
    '''

    # Hard-coded filename
    m_probability = probability(known)
    u_probability = probability(unmatch)

    label_(m_probability,u_probability)
    label = label_(m_probability,u_probability)
    dict1 = labeled(label)
    sorted_list = sorted_(label)
    label_r(sorted_list,mu,lambda_)

    dict2 = label_r(sorted_list,0.005,0.005)

    reference_table = main_goal(dict1,dict2)

    list1 = []
    for z in range(len(zagat)):
      list1.append(z)

    list2 = []
    for f in range(len(fodor)):
      list2.append(f)

    combination = []
    for x in list2:
      for y in list1:
        combination.append((y,x))

    final_dict = {}
    for i in range(len(combination)):
      z_index =combination[i][0]
      f_index =combination[i][1]
      name_category = get_jw_category(jellyfish.jaro_winkler(zagat.loc[z_index][1],fodor.loc[f_index][1]))
      city_category = get_jw_category(jellyfish.jaro_winkler(zagat.loc[z_index][2],fodor.loc[f_index][2]))
      address_category = get_jw_category(jellyfish.jaro_winkler(zagat.loc[z_index][3],fodor.loc[f_index][3]))
      similarity_tuple= name_category, city_category, address_category
      final_dict[combination[i]] = similarity_tuple

    for k,v in final_dict.items():
      for w,z in reference_table.items():
        if v == w:
            final_dict[k] = z



### YOUR AUXILIARY FUNCTIONS HERE

def probability(match_umatch_csv):
    
    possible = []
    list1 = ["low","medium","high"]
    list2 = ["low","medium","high"]
    list3 =["low","medium","high"]
    for x in list3:
        for y in list2:
            for z in list1:
                possible.append((z,y,x))
    z = []
    f = []
    m = []
    names = []
    for i in range(len(match_umatch_csv)):
        z_index = match_umatch_csv.loc[i][0]
        f_index = match_umatch_csv.loc[i][1]
        z.append(z_index)
        f.append(f_index)
        name_category = get_jw_category(jellyfish.jaro_winkler(zagat.loc[z_index][1],fodor.loc[f_index][1]))
        names.append(fodor.loc[f_index][1])
        city_category = get_jw_category(jellyfish.jaro_winkler(zagat.loc[z_index][2],fodor.loc[f_index][2]))
        address_category = get_jw_category(jellyfish.jaro_winkler(zagat.loc[z_index][3],fodor.loc[f_index][3]))
        similarity_tuple= name_category, city_category, address_category
        m.append(similarity_tuple)
        
    frequency = {}
    
    for i in possible:
        frequency [i]= 0 
    for item in m:
        frequency[item] += 1/len(m)
    
    return frequency

def label_(m_probability,u_probability):
    label = {}
    w = []
    for item in m_probability:
        label[item] = ""
        if m_probability[item] == u_probability[item]: 
            label[item] = "possible_match"
    return label
   
def labeled (label):
    labeled = {}
    for k,v in label.items():
        if v == "possible_match":
            labeled[k] = v
    return labeled

def sorted_(label):
    w = []
    a_list = []
    for k, v in label.items():
        if v == '':
            w.append(k)  

    for i in w: 
        t = tuple([i,m_probability[i], u_probability[i]])
        a_list.append(t)
    
    sorted_list = util.sort_prob_tuples(a_list)
    return sorted_list

def label_r(sorted_list,mu,lamda_):
    a_sum = 0
    b_sum = 0
    label_r = {}
    for i in range(len(sorted_list)):
        label_r[sorted_list[i][0]] = "possible_match"
    for i in range(len(sorted_list[::-1])):
        b_sum +=(sorted_list[::-1][i][1])
        if b_sum <= lamda_:
            label_r[sorted_list[::-1] [i][0]] = "unmatch"
    for i in range(len(sorted_list)):
        a_sum += sorted_list[i][2]
        if a_sum <= mu:
            label_r[sorted_list[i][0]] = "match"
    return label_r

def main_goal(dict1,dict2):
    dict3 = dict1.copy()   
    dict3.update(dict2)    
    return dict3
    
        