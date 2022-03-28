"""
CAPP 30122: Course Search Engine Part 1

Siwen Chen
"""
# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg=invalid-name, redefined-outer-name, unused-argument, unused-variable


import queue
import json
import sys
import csv
import re
import bs4
import util

from bs4 import BeautifulSoup

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])


def processing(num_pages_to_crawl,course_map_filename):
     
    '''
    Create an empty queue,put the starting url into the queue.
    
    Get a url from the queue(first in, first out), 
    
    first,make a get request to fetch the raw HTML content
    
    second,parse the html content
    
    third,scan for more urls from the url,check if the connected urls are valid. 
    Get the url one at a time, if this_link works, put it into queue
    
    look into the page to get all the words,construct the index as the crawler visits the pages,
    and create a data dictionary to store the data.
    
    Input: 
    
    num_pages_to_crawl(int): represents when you stop crawling. 
    e.g. If num_pages_to_crawl is equal to 100 then we won't visit the 101 page. 
    
    course_map_filename(json):use json file to map the course code to identifier 
    
    
    Output: a dictionary to map the course_identifier to the words in the title and course description 

    '''  
    
    file = open(course_map_filename).read()
    course_map = json.loads(file)

    
    dictionary = {}

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    
    limiting_domain = "classes.cs.uchicago.edu"    
    
    q = queue.Queue()
    size = 0
    maxsize = num_pages_to_crawl 
    
    request = util.get_request(starting_url)
    q.put(util.get_request_url(request))
    
    visited_urls = []
    count_visited = 1
    
    while not q.empty():
        current_url = q.get()
        request = util.get_request(current_url)
        visited_urls.append(util.get_request_url(request))
        if request is None:
            continue
        else:
            data = util.read_request(request)
        if data == "":
            continue
        else:
            soup = BeautifulSoup(data,"html5lib")
        
        if count_visited < num_pages_to_crawl:
            for url in soup.find_all("a"):
                url = url.get("href")
                if url is None:
                    continue
                if not util.is_absolute_url(url):
                    url = util.convert_if_relative_url(current_url,url)
                    if url is None:
                        continue
                url = util.remove_fragment(url)
                valid = util.is_url_ok_to_follow(url, limiting_domain)
                if valid:
                    request = util.get_request(url)
                    url = util.get_request_url(request)
                    if url not in q.queue and url not in visited_urls:
                        q.put(url)
                count_visited += 1

        indexing(soup, dictionary, course_map)
        
    return dictionary

def indexing(soup, dictionary, course_map):
    '''
    The indexing process as the crawler visits the pages,

    
    Objective:
    1.get course_code
    2.Get words from each page title and description  
    a.normal class b.for the sequence : main title and description and unique description 
    3.use json file to map the course code to identifier 
    4.update the dictionary 
    
    course_code(string) e.g CMSC 12200
    
    Used the util.find_sequence(tag),  the function returns a list of the div tag objects for the subsequence;
    otherwise,
    it returns an empty list.
    
    Input: 
    soup
    dictioanry
    course_map : read file to map the course code to identifier 
    
    '''

    course_divs = soup.find_all("div", class_='courseblock main')
    for div in course_divs:
        soup = BeautifulSoup(str(div),"html5lib")
        title = soup.find('p', class_='courseblocktitle').text
        title = re.sub(r'[^a-zA-Z0-9\s]', '', title).split()
        dpt_name = title[0]
        course_code = ' '.join(title[:2])
        name = title[2:-2]
        desc = soup.find(class_ = "courseblockdesc").text
        
        cleaned = set()
        for w in name + [dpt_name]:
            w = w.lower()
            if w not in INDEX_IGNORE:
                cleaned.add(w)
        for w in re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', desc):
            w = w.lower()
            if w not in INDEX_IGNORE:
                cleaned.add(w)
            
        subseqs = util.find_sequence(div)
        if len(subseqs) == 0:
            course_identifier = course_map[course_code]
            for clean in cleaned:
                if clean not in dictionary:
                    dictionary[clean] = [course_identifier]
                elif course_identifier not in dictionary[clean]:
                    dictionary[clean].append(course_identifier)
                
        for subseq in subseqs:
            
            sub_soup = BeautifulSoup(str(subseq),"html5lib")
            sub_title = sub_soup.find('p', class_='courseblocktitle').text
            sub_title = re.sub(r'[^a-zA-Z0-9\s]', '', sub_title).split()
            sub_course_code = ' '.join(sub_title[:2])
            sub_course_identifier = course_map[sub_course_code]
            sub_dpt_name = title[0]
            sub_name = sub_title[2:-2]
            sub_desc = sub_soup.find(class_ = "courseblockdesc").text
            sub_cleaned = set()
            for w in sub_name + [sub_dpt_name]:
                w = w.lower()
                if w not in INDEX_IGNORE:
                    sub_cleaned.add(w)
            for w in re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', sub_desc):
                w = w.lower()
                if w not in INDEX_IGNORE:
                    sub_cleaned.add(w)
                        
            for clean in sub_cleaned.union(cleaned):
                if clean not in dictionary.keys():
                    dictionary[clean] = [sub_course_identifier]
                elif sub_course_identifier not in dictionary[clean]:
                    dictionary[clean].append(sub_course_identifier)

def CSV_file(dictionary,index_filename):
    '''
    convert into CSV file from the dictioanry. 
    
    Make the csv A course identifier  |  a word format
    '''
    with open(index_filename, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter="|")
        for word, ids in dictionary.items():
            for _id in ids:
                spamwriter.writerow([_id,word])
    return csvfile

def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index index.
    '''

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    dictionary = processing(num_pages_to_crawl,course_map_filename)
    
    csv_file = CSV_file(dictionary,index_filename)
        
    return csv_file
    


if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
