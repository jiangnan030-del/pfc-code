 
size = 0.5
box_count = 10
first_name = "Fred"
last_name = 'Baker'

long_string = """
This is a multi-line string.
Triple quotes are used to define strings like this.
"""


id_list = [1, 2, 3, 4]


id_list


id_list.append(903)


id_list


for id_number in id_list:
    print ("id #: ", id_number)


len(id_list)


id_list[0]


id_list[1:3]


id_list[-1]


id_list[0] = 10.0

print (id_list)


id_list.append("this is a string")


id_list


parts = (1,2,3,4,5)


parts



telephone_directory = {"Jim" : 125, "Steve": 128, "Bob" : 144}


telephone_directory


telephone_directory["Jim"]


telephone_directory["Fred"] = 147
telephone_directory[(1,3)] = 0.22344


telephone_directory


del(telephone_directory["Bob"])



for key, value in telephone_directory.items():
    print ("found key: {} with value: {}".format(key, value))


telephone_directory.keys()




def my_function(a, b):
    return a + b


my_function(1.0, 5)


long_string = """
This is a multi-line string.
Triple quotes are used to define strings like this.
"""


long_string.split()

