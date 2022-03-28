'''
Course search engine: search

Siwen Chen
'''

from math import radians, cos, sin, asin, sqrt, ceil
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course_information.sqlite3')


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is list of strings
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enrollment is a pair of integers
      - walking_time is an integer
      - building_code ia string
      - terms is a list of strings string: ["quantum", "plato"]

    Returns a pair: an ordered list of attribute names and a list the
     containing query results.  Returns ([], []) when the dictionary
     is empty.
    '''
    assert_valid_input(args_from_ui)
    # connect to database
    conn = sqlite3.connect('course_information.sqlite3')

    #create a cursor
    c = conn.cursor()

    conn.create_function("time_between", 4,compute_time_between)

    maping_courses_table = {"dept":"courses.dept",
                        "day": "meeting_patterns.day",
                        "time_start" : "meeting_patterns.time_start",
                        "time_end":"meeting_patterns.time_end",
                        "building_code" : "sections.building_code",
                        "walking_time" : "time_between(gps.lon, gps.lat, target_gps.lon, target_gps.lat) AS walking_time",
                        "enrollment" : "sections.enrollment",
                        "title" : "courses.title",
                        "section_num" : "sections.section_num",
                        "course_num" : "courses.course_num",
                        "terms" : "catalog_index.word"
                         }

    # Select part

    searches = args_from_ui.keys() #e.g.['course.dept', 'catalog_index.word']


    if len(searches) == 0:
        return ([], [])

    else:
        lst_column = ['dept','course_num','title'] # minimum list for an ordered list of attribute names

    if "building_code" in searches:
        lst_column.extend(['section_num','day','time_start','time_end','enrollment','building_code',"walking_time"])
        

    else:
        for l in ['day','enrollment','time_start','time_end']:
            if l in searches:
                lst_column.extend(['section_num','day','time_start','time_end','enrollment'])
                break


    where_dict = {"dept": "courses.dept = ?", 
            "enrollment" : " sections.enrollment BETWEEN ? AND ?",
            "time_start":" meeting_patterns.time_start >= ?",
            "time_end" : " meeting_patterns.time_end <= ?",
            "building_code": " target_gps.building_code = ?",
            "walking_time": " walking_time <= ?"}

    if 'day' in searches:
        where_dict["day"] = 'meeting_patterns.day IN (' + ','.join(["? "] * len(args_from_ui['day'])) +  ')'
    if 'terms' in searches:
        where_dict['terms'] = """courses.course_id IN (
                                SELECT catalog_index.course_id 
                                FROM catalog_index 
                                WHERE catalog_index.word IN (""" + ','.join(["? "] * len(args_from_ui['terms'])) +  ')' +\
                            """ GROUP BY catalog_index.course_id
                                HAVING COUNT(*) = """ + str(len(args_from_ui['terms'])) + ')'

    ss = []
    for i in lst_column:
        s = maping_courses_table[i]
        ss.append(s)



    str_select = "SELECT " +  ", " .join(ss) 


    #From part
    f = ['courses']
    w = []
    #if "terms" in searches:
    #    f.append("catalog_index")
    #    w.append("courses.course_id = catalog_index.course_id")

    if len(lst_column) > 3:
        f.append("meeting_patterns")
        f.append("sections")
        w.append("courses.course_id = sections.course_id")
        w.append("sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id")

    if len(lst_column) == 10:
        f.append("gps")
        f.append('gps AS target_gps')
        w.append("sections.building_code = gps.building_code")

   
    str_from = "FROM " + ", " .join(f) 
    args = []
    for k,v in where_dict.items():
        if k in args_from_ui.keys():
            w.append(v)
            if type(args_from_ui[k]) == list:
                args.extend(args_from_ui[k])
            else:
                args.append(args_from_ui[k])

    str_where = "WHERE " + " AND " .join(w)



    r = c.execute(str_select + " " +  str_from + " " + str_where + ";", args)

    query_results = r.fetchall()
    column_names = get_header(c)
    conn.close()
    return (column_names,query_results)


########### auxiliary functions #################
########### do not change this code #############

def assert_valid_input(args_from_ui):
    '''
    Verify that the input conforms to the standards set in the
    assignment.
    '''

    assert isinstance(args_from_ui, dict)

    acceptable_keys = set(['time_start', 'time_end', 'enrollment', 'dept',
                           'terms', 'day', 'building_code', 'walking_time'])
    assert set(args_from_ui.keys()).issubset(acceptable_keys)

    # get both buiding_code and walking_time or neither
    has_building = ("building_code" in args_from_ui and
                    "walking_time" in args_from_ui)
    does_not_have_building = ("building_code" not in args_from_ui and
                              "walking_time" not in args_from_ui)

    assert has_building or does_not_have_building

    assert isinstance(args_from_ui.get("building_code", ""), str)
    assert isinstance(args_from_ui.get("walking_time", 0), int)

    # day is a list of strings, if it exists
    assert isinstance(args_from_ui.get("day", []), (list, tuple))
    assert all([isinstance(s, str) for s in args_from_ui.get("day", [])])

    assert isinstance(args_from_ui.get("dept", ""), str)

    # terms is a non-empty list of strings, if it exists
    terms = args_from_ui.get("terms", [""])
    assert terms
    assert isinstance(terms, (list, tuple))
    assert all([isinstance(s, str) for s in terms])

    assert isinstance(args_from_ui.get("time_start", 0), int)
    assert args_from_ui.get("time_start", 0) >= 0

    assert isinstance(args_from_ui.get("time_end", 0), int)
    assert args_from_ui.get("time_end", 0) < 2400

    # enrollment is a pair of integers, if it exists
    enrollment_val = args_from_ui.get("enrollment", [0, 0])
    assert isinstance(enrollment_val, (list, tuple))
    assert len(enrollment_val) == 2
    assert all([isinstance(i, int) for i in enrollment_val])
    assert enrollment_val[0] <= enrollment_val[1]


def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return int(ceil(mins))


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".")+1:]
        header.append(s)

    return header
