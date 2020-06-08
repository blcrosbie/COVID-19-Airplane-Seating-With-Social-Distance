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



from randomize import create_passenger_roster

LOCAL_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_DIR = os.path.dirname(LOCAL_SRC_DIR)
LOCAL_BASE_DIR = os.path.dirname(LOCAL_REPO_DIR)

LOCAL_MODELS_DIR = os.path.join(LOCAL_REPO_DIR, "models")
sys.path.append(LOCAL_MODELS_DIR)

from airplane import Airplane
from passenger import Passenger

from find_seats import find_next_seat, group_find_next_seat
from offset_analyze import AnalyzeSocialDistance
from assign_seats import SeatPassenger
from block_seats import SocialDistance



##############################################################################################################
# STEP 1: GET AIRPLANE

def initialize_airplane(debug=False, capacity=0.0, option=0):
    
    if debug:
        plane = Airplane(airplane_choices[option])
        plane.create_cabin(capacity)
    
    else:
        # CHOOSE AIRPLANE MODEL
        option = len(airplane_choices)
        attempts = 3
        
        # have a prompt to select airplane: use input to select 0, 1, 2
        print("Choose an Airplane Model")
        for opt, apln in airplane_choices.items():
            print("\tEnter {} for {}".format(opt, apln))
              
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
        plane = Airplane(airplane_choices[option])
        capacity = plane.booked_seats/plane.total_seats
        plane.create_cabin(capacity)
        
    
    return plane
    

##############################################################################################################
# STEP 2: OFFSET ANALYSIS FOR SPECIFIC CASE

def initialize_offsets(default_offset, debug=False):
    # global default offset for no social distancing

    
    if debug:
        no_offset = default_offset
        # Default Offset declared in globals as x: 0 y: 0, the conventional seating method
        # THIS COULD BE REDEFINED TO ALLOW CUSTOMIZATION: SET BY MAX X and Y from user
        offset_1 = {'x': 2, 'y': 1, 'method': 'full_block'}
        offset_2 = {'x': 2, 'y': 1, 'method': 'shaved_corners'}
        offset_3 = {'x': 1, 'y': 1, 'method': 'full_block'}
        offset_4 = {'x': 1, 'y': 1, 'method': 'cardinal_only'}
        offset_5 = {'x': 1, 'y': 0, 'method': 'cardinal_only'}
        
        sd_offsets = [no_offset, offset_1, offset_2, offset_3, offset_4, offset_5]
        
        
    else:
        ## ask user for MAX value X, Y
        ## iterate through decrement from max to 0, cycle through full-block, shaved-corners, cardinal-only
        ## once Y=0 and X=1 and cardinal only, finish list
        # no_default = set_default_offset
        # sd_offsets = [no_offset]
        pass
    

    return sd_offsets
    

def analyze_offsets(airplane, sd_offset_list, default_offset, view_charts=False, debug=False):

    if debug:
        # order priority for offsets
        default_order_on_attr = 'max_accommodation'

    else:
        # another user prompt to ask for Order Prirority
        pass
    
    offsets_analyzed_dict =  AnalyzeSocialDistance(airplane, sd_offset_list, default_offset, default_order_on_attr, view_charts=view_charts)
    
    return offsets_analyzed_dict



##############################################################################################################
# STEP 3: INPUT PASSENGERS: USER UPLOAD CSV OR RANDOMIZE FOR TESTING
    
def initialize_passengers(debug=False, passengers_booked=0):
    
    if debug:    
        df = create_passenger_roster(passengers_booked, view_stats=False)
    else:
        # import csv with passengers
        pass
    
    return df


###################################################################################################
        


def group_AssignSeat(airplane, df, group_list, offset_dict):
    success = 0
 
    # Filter from all groups to groups of this size        
    group_df = find_members_in_group(df[df['group_size'] == len(group_list)], group_list)
    sort_on = ['number_of_flags', 'age']
    group_df = group_df.sort_values(by=sort_on, ascending=False)
    group_df = group_df.reset_index(drop=True)


    # iterate through each member in this group
    for row in group_df.index:
        this_row = group_df[group_df.index == row]
        pID = group_df.loc[row, 'pID']
        this_psgr = Passenger(pID)

        age = group_df.loc[row, 'age']
        group = group_df.loc[row, 'group']
        has_travelled = group_df.loc[row, 'has_travelled']
        has_precon = group_df.loc[row, 'has_preexisting_condition']

        this_psgr.fill_questionare(age, group, has_travelled, has_precon)        
        this_offset = offset_selector(airplane, this_psgr, offset_dict)

        group_df.loc[row, 'offset_order'] = this_offset['order'] 
        group_df.loc[row, 'offset_x'] = this_offset['x']
        group_df.loc[row, 'offset_y'] = this_offset['y']
        group_df.loc[row, 'offset_method'] = this_offset['method']

        #group passenger seating method
        prev_assigned_seat = airplane.last_assigned_seat
        # Allowed Group Passenger Seat_State = 'G'
        print("BEFORE SEATING: ")
        print("PREV: ", prev_assigned_seat)
        print("NEXT SEAT TO ASSIGN: ",airplane.next_seat)
        SeatPassenger(airplane, occupied_state='G', **this_offset)
        print("AFTER SEATING: ")
        print("JUST ASSIGNED: ", airplane.last_assigned_seat)
        if prev_assigned_seat is not None and success < len(group_list)-1:
            assert prev_assigned_seat != airplane.last_assigned_seat, "Unable to Seat"

        group_df.loc[row, 'seat'] = airplane.last_assigned_seat
        success += 1
        group_find_next_seat(airplane)
        print("NEXT SEAT TO ASSIGN: ", airplane.next_seat)
        airplane.update()

    print("SUCCESSFUL SEATING COUNT: ",success)
    assert success >= len(group_list)-1, "NOT ALL PASSENGERS IN GROUP SEATED"
    group_ToggleState(airplane, group_df)
    
    # update MAIN df with seat assignments
    df = update_seat_roster(df, group_df)
    
    
    return df


###############################################################################
    
def single_AssignSeat(airplane, df, offset_info):
    # make a passenger from this row
    for row in df.index:
        this_row = df[df.index == row]
        pID = df.loc[row, 'pID']
        this_psgr = Passenger(pID)

        age = df.loc[row, 'age']
        group = []
        has_travelled = df.loc[row, 'has_travelled']
        has_precon = df.loc[row, 'has_preexisting_condition']

        this_psgr.fill_questionare(age, group, has_travelled, has_precon)        
        this_offset = offset_selector(airplane, this_psgr, offset_info)

        df.loc[row, 'offset_order'] = this_offset['order'] 
        df.loc[row, 'offset_x'] = this_offset['x']
        df.loc[row, 'offset_y'] = this_offset['y']
        df.loc[row, 'offset_method'] = this_offset['method']

        prev_assigned_seat = airplane.last_assigned_seat
        SeatPassenger(airplane, **this_offset)
        
        assert prev_assigned_seat != airplane.last_assigned_seat, "Unsuccessful Seating!"
        
        df.loc[row, 'seat'] = airplane.last_assigned_seat
        
        find_next_seat(airplane, occupied_state='P')
        airplane.update()

        
    return df


##############################################################################################################
# STEP 4: Assign the Seat and fill in Social Distance block offsets 

def AssignSeating(airplane, df, offset_dict):
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



###################################################################################################    
# STEP 0:
    
# DECLARE SOME GLOBAL PARAMETERS

# DEFINE AIRPLANE CHOICES
airplane_choices = {0:'Boeing_737', 1:'Boeing_787', 2:'Airbus_380'}

### DEFINE SPACING OFFSETS
# global default offset for social distancing
default_offset = {'x': 0, 'y': 0, 'method': 'cardinal_only'}

# Initialize Offset Info
offset_info = {}


# TEST vs. PROD

# if in test mode, use 1 of the 3 airplan models
# else allow user to choose, interactive input mode


# if in test mode, create artificial passengers
# else:    input csv of passenger roster

# CONTINUE ON SAME FROM THERE

if __name__ == '__main__':
    
    DEBUG = True
    test_capacity = 0.66
    age_threshold = 50
    test_option = 2
    
    # 1. BUILD PLANE
    my_plane = initialize_airplane(debug=DEBUG, capacity=test_capacity, option=test_option)
    
    # 2a. set the spacing offsets
    my_sd_offsets = initialize_offsets(default_offset, debug=DEBUG)
        
    # 2b. ANALYZE OFFSET FOR THIS CASE PROBLEM
    my_offset_info = analyze_offsets(my_plane, my_sd_offsets, default_offset, debug=DEBUG)
    
    # 3. RANDOM PASSENGERS
    #passengers_df = initialize_passengers(debug=DEBUG, passengers_booked=my_plane.booked_seats)

    
    # 3. Start Seating Group Passengers
    
    
    

    
