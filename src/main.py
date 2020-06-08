#!/usr/bin/env python
# coding: utf-8

# The purpose of this algorithm is to assign seats to maximize 
# social distancing for highest priority passengers
# and limit air travel for unnecessary purposes
# 1. SEAT ALL GROUPS

# 1a. FIND each group based on uuids in list
# 1b. SEND GROUP DATAFRAME to group AssignSeat

# in group_AssignSeat function:
# 2a. select offset 1 at a time
# 2b. Seat 1 at a time, and use seat state 'G' instead of 'P'
# 2c. Need to update SocialDistance block to understand 'G' is valid to have in SD block, but not to over-assign
# 2d. Recalculate Airplane buffer, remaining assignments, and free seats 

# 3a. Repeat until all group has been seated, add their Seat and offset to df passenger dataframe
# 3b. Repeat until all groups size > 1 seated (make sure seat states are always updated back to 'P' before
#      Moving on to next group)


import os, sys
import numpy as np
import pandas as pd

#from assign_seats import BoardPassengers
#from block_seats import SocialDistance

from find_seats import find_next_seat, group_find_next_seat

from offset_analyze import AnalyzeSocialDistance


LOCAL_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_DIR = os.path.dirname(LOCAL_SRC_DIR)
LOCAL_BASE_DIR = os.path.dirname(LOCAL_REPO_DIR)
sys.path.append(LOCAL_REPO_DIR)

from tests import random_passengers
from models import Airplane, Passenger





###################################################################################################    
# Function: SocialDistance (Input)
# Input:    (airplane:   Airplane class object
#            offset: dictionary of x and y offset to properly space passenger apart from other passengers)
#                    including a method to define block, full_block, shaved_corners, cardinal_only
#
# Ouput: this has no Output, but it does Update the Airplane class Object
#
# Object Update: this Method updates the "airplane.next_seat" by using the "airplane.skip_seat()" method
#         which assigns a int(1) to the seat_state as it passes to the next available seat cursor
#
# Comment: 
#          
#   

def SocialDistance(airplane, occupied_state, offset):     
    # use modular functions to create Social Distance: 'SD' block list of seats 
#     try:
    blocked_seat_list = create_sd_block_list(airplane, offset)

    print("BLOCKED SEAT IN SD FUNCTION: ", blocked_seat_list)
    # now check the blocked seat list to ensure no passengers are encroaching on Social Distance Offset
    check_flag = check_blocked_seats(airplane, blocked_seat_list)


    if check_flag:
        # continue onward, this blocked seat list is GOOD!
        return blocked_seat_list
    else:
        print("SKIP IN SOCIAL DISTANCE")
        print(airplane.next_seat)
        print()
        skip_seat(airplane, airplane.next_seat, occupied_state)
        print(airplane.next_seat)            

        return SocialDistance(airplane, occupied_state, offset)

    
#     except Exception as e:
#         print("SocialDistance Error: {}".format(e))
#         print(airplane.view_plane())
#         print(occupied_state)


### DEFINE SPACING OFFSETS
# global default offset for social distancing
default_offset = {'x': 0, 'y': 0, 'method': 'cardinal_only'}

# Default Offset declared in globals as x: 0 y: 0, the conventional seating method
offset_1 = {'x': 2, 'y': 1, 'method': 'full_block'}
offset_2 = {'x': 2, 'y': 1, 'method': 'shaved_corners'}
offset_3 = {'x': 1, 'y': 1, 'method': 'full_block'}
offset_4 = {'x': 1, 'y': 1, 'method': 'cardinal_only'}
offset_5 = {'x': 1, 'y': 0, 'method': 'cardinal_only'}
my_sd_offsets = [default_offset, offset_1, offset_2, offset_3, offset_4, offset_5]

# SET ORDER PRIORITY FOR OFFSETS
my_order_on_attr = 'max_accommodation'

# DEFINE AIRPLANE CHOICES
airplane_choices = {0:'Boeing_737', 1:'Boeing_787', 2:'Airbus_380'}

# TESTING AND DEBUGGING PARAMETERS
DEBUG = True
# DEBUG = False
test_capacity = 0.66
age_threshold = 50

# TEST PLANE
# option = 0
# option = 1
option = 2
my_plane = Airplane(airplane_choices[option])
offset_info = {}



########################################################################################
### DEBUG ###
# # randomly assign plane capacity, setting a threshold at 15%
# min_threshold = 0.25 
# capacity = round(max(min_threshold, random.random()),3)

if DEBUG:
    my_plane.create_cabin(test_capacity)

    if offset_info == {}:
        offset_info = AnalyzeSocialDistance(my_plane, my_sd_offsets, my_order_on_attr, view_charts=True)
    
    # No create the passengers and put in DataFrame
    passengers_df = random_passengers.create_random_passengers(my_plane.booked_seats, view_stats=False)
    print(passengers_df.head())
    
    # Board the Passengers!
#    passengers_df = BoardPassengers(my_plane, passengers_df, offset_info)




###################################################################################################    
# Function: BoardAirplane (Input)
# Input:    (airplane:   Airplane class object
#                   df : dataframe of passengers            
#                   offset: dictionary of x and y offset to properly space passenger apart from other passengers)
#                    including a method to define block, full_block, shaved_corners, cardinal_only
#
# Ouput: this has no Output, but it does Update the Airplane class Object
#
# Object Update: this Method updates the "airplane.next_seat" by using the "airplane.skip_seat()" method
#         which assigns a int(1) to the seat_state as it passes to the next available seat cursor
#
# Comment: 
#          
#   
def test_AssignSeating(airplane, df, offset_dict):
    my_plane.create_cabin(test_capacity)
    offset_info = {}
    if offset_info == {}:
        offset_info = AnalyzeSocialDistance(my_plane, my_sd_offsets, my_order_on_attr, view_charts=True)
    
    # No create the passengers and put in DataFrame
    passengers_df = random_passengers.create_random_passengers(my_plane.booked_seats, view_stats=False)
    print(passengers_df.head())



def AssignSeating(airplane, df, offset_dict):
    offset_info = {}
    # Validations on Passenger List
    assert not df.empty, "No Passengers to Board"
    
    # Initialize seats to 0
#    df = init_passenger_seating(df)    
    
    # Sort passengers 
    sort_on = ['group_size', 'age']
    df = df.sort_values(by=sort_on, ascending=False)
    df = df.reset_index(drop=True)
        
    # Find unique groups
#    unique_groups = find_unique_groups(df)
    
#    for group in unique_groups: 
#        df = group_AssignSeat(airplane, df, group, offset_dict)
#        airplane.update()
#        find_next_seat(airplane)
#        airplane.view_plane()
 
    return df


##############################################################################################################
### Actual Main Starts here
if __name__ == '__main__':

    DEBUG = True
    
    if DEBUG:
        # create random passengers
        # use airplane model, build with random capacity
        
    
    test_AssignSeating()
#    AssignSeating()




if not DEBUG:
    # CHOOSE AIRPLANE MODEL
    option = len(airplane_choices)
    attempts = 3
    
    # have a prompt to select airplane: use input to select 0, 1, 2
    print("Choose an Airplane Model")
    for opt, plane in airplane_choices.items():
        print("\tEnter {} for {}".format(opt, plane))
          
    while option not in list(airplane_choices.keys()):
        input_plane_option = input("Enter Option: ")
        print()
        
        try:
            assert isinstance(int(input_plane_option), int), "\nNOT A VALID ENTRY. TRY AGAIN"
            option = int(input_plane_option)
            assert option in list(range(0,len(airplane_choices))), "\nNOT A VALID AIRPLANE CHOICE"
        except Exception as e:
            attempts -= 1
            print(e)
            print("\tRemaining Attempts: {}\n".format(attempts))
            
        
    ### BUILD AIRPLANE
    my_plane = Airplane(airplane_choices[option])
    my_plane.create_cabin()
    
    ### ANALYZE POSSIBLE OFFSETS FOR AIRPLANE
    offset_info = AnalyzeSocialDistance(my_plane, my_sd_offsets, my_order_on_attr, view_charts=True)
    
