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
import json

from randomize import create_passenger_roster

LOCAL_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_DIR = os.path.dirname(LOCAL_SRC_DIR)
LOCAL_BASE_DIR = os.path.dirname(LOCAL_REPO_DIR)

LOCAL_MODELS_DIR = os.path.join(LOCAL_REPO_DIR, "models")
sys.path.append(LOCAL_MODELS_DIR)

from airplane import Airplane
from offset_analyze import AnalyzeSocialDistance
from assign_seats import init_passenger_seating, group_AssignSeat, single_AssignSeat
from find_seats import single_find_next_seat
# from assign_seats import SeatPassenger
# from block_seats import SocialDistance



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

    if os.path.exists('offset.json'):
        with open('offset.json', 'r') as fp:
            offsets_analyzed_dict = json.load(fp)
        
    else:
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
        print("Creating Random Passenger Roster...")
        df = create_passenger_roster(passengers_booked, view_stats=False)
    else:
        # import csv with passengers
        pass
    
    return df

    



##############################################################################################################
# STEP 4: Assign the Seat and fill in Social Distance block offsets 


# build unique group lists from total dataframe
def find_unique_groups(df):
    # Now Find the Unique Groupings of Passengers
    all_groups_df = df[df['group_size'] > 1]
    
    try:
        assert not all_groups_df.empty, "NO GROUPS IN PASSENGER LIST"
        unique_groups_list = all_groups_df['group'].drop_duplicates().reset_index(drop=True).to_list()
    
    except Exception as e:
        print(e)
        
    return unique_groups_list



def update_seat_roster(df, sub_df):
    # now update the main df_passenger dataframe with this information from each df_group
    for row in sub_df.index:
        this_pID = sub_df.loc[row, 'pID']
        update_line = df[df['pID'] == this_pID]
        update_row = update_line.index[0]

        df.loc[update_row, :] = sub_df.loc[row, :]
    
    return df


###############################################################################

def AssignSeating(airplane, df, offset_dict, debug=False):
    # Validations on Passenger List
    assert not df.empty, "No Passengers to Board"
    
    if debug:
        print("Assigning {} Seats ...".format(airplane.booked_seats))
    
    # Initialize seats to 0
    df = init_passenger_seating(df)  
    
    # Sort passengers 
    sort_on = ['group_size', 'age']
    df = df.sort_values(by=sort_on, ascending=False)
    df = df.reset_index(drop=True)
    
    # Start with Grouped Passengers
    all_groups = find_unique_groups(df)
    for group in all_groups:
        group_df = group_AssignSeat(airplane, df, group, offset_dict)
        df = update_seat_roster(df, group_df)
   
    
    # Finish with Singles, prioritize spacing on preexisting, travel, age
    single_df = df[df['group_size'] == 1]
    
    if debug:
        print("Number of Free seats for Buffer: ", airplane.free_seats)
        print("Number of Passengers with Pre-Existing Conditions: ", len(single_df[single_df['has_preexisting_condition'] == True]))
    
    single_df = single_AssignSeat(airplane, single_df, offset_dict)
    df = update_seat_roster(df, single_df)

    
    # run clean up on last passengers
    if airplane.remaining_seats_to_assign > 0:
        duplicate_seats = df['seat'].drop_duplicates()
        index_dup = list()
        for i in range(0, len(df)):
            if i not in list(duplicate_seats.index):
                index_dup.append(i)
                
        print(index_dup)
        
        for row_skip in index_dup:
            # for each duplicated seat, set it back to a skip seat
            dup_seat = df.loc[row_skip, 'seat']
            dup_row = int(dup_seat[:-1])
            dup_col = dup_seat[-1]
            airplane.cabin.loc[dup_row, dup_col] = 1
            df.loc[row_skip, 'seat'] = 0
            
        
        airplane.next_seat = str(airplane.start_row + airplane.rows) + airplane.seat_letters[0]
        single_find_next_seat(airplane, True)
        print(airplane.next_seat)
        
        for row_reseat in index_dup:
            df.loc[row_reseat, 'seat'] = airplane.next_seat
            new_row = int(airplane.next_seat[:-1])
            new_col = airplane.next_seat[-1]
            airplane.cabin.loc[new_row, new_col] = 'P'
            airplane.update()
            single_find_next_seat(airplane, True)
            
        
        
        

    print("SINGLES FINISHED")   

    return df


###################################################################################################    
# STEP 5: Save Results

def save_results(df, airplane, repo_dir):
    CSV_RESULTS_DIR = os.path.join(repo_dir, "results")
    save_folder = os.path.join(CSV_RESULTS_DIR, airplane.make + '_' + airplane.model)
    
    count = 0
    if count < 10:
        leading_zero = '00'+str(count)
    elif count < 100:
        leading_zero = '0'+str(count)
    else:
        leading_zero = str(count)
        
    save_file = 'run_000.csv'
    
    fn = os.path.join(save_folder, save_file)
    
    while os.path.exists(fn):
        count += 1
        if count < 10:
            leading_zero = '00'+str(count)
        elif count < 100:
            leading_zero = '0'+str(count)
        else:
            leading_zero = str(count)
        
        save_file = 'run_' + leading_zero + '.csv'
        fn = os.path.join(save_folder, save_file)
            
    passengers_df.to_csv(fn, index=False)
    print("Saved Passenger Seating Dataframe:\n{}".format(fn))
    return
    



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
    
    # 3. RANDOM PASSENGERS or import file
    passengers_df = initialize_passengers(debug=DEBUG, passengers_booked=my_plane.booked_seats)

    # 4. Start Seating Group Passengers
    passengers_df = AssignSeating(my_plane, passengers_df, my_offset_info, debug=DEBUG)
    
    # 5. Save CSV results
    save_results(passengers_df, my_plane, LOCAL_REPO_DIR)
    
    print("DONE")

    
    
    
    

    
