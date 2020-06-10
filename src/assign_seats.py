# -*- coding: utf-8 -*-

import pandas as pd

from passenger import Passenger
from block_seats import SocialDistance
from find_seats import find_next_seat, group_find_next_seat, single_find_next_seat

###############################################################################


def count_flags(*flags_to_check):
    flag_count = 0
    for flag in flags_to_check:
        if flag == True:
            flag_count +=1
            
    return flag_count


def init_passenger_seating(df): 
    
    # Ensure group size is set
    if 'group_size' not in list(df.columns):
        df['group_size'] = df['group'].apply(lambda x: len(x) if len(x)>1 else 1)
    else:
        pass
    

    # add in some meta data for the True/False Flags to help sort
    df['number_of_flags'] = df[['has_preexisting_condition', 'has_travelled']].apply(lambda x: count_flags(*x), axis=1)

    
    try:
        sub_df = df[df['seat'] == 0]
        assert len(sub_df) == len(df), "Already Initialized"
    except:
        df['seat'] = 0
        df['offset_order'] = 0
        df['offset_x'] = 0
        df['offset_y'] = 0
        df['offset_method'] = 0
        
    return df


###############################################################################

def order_offset_list(offset_dict, primary_order=0, depth=2):
    order_list = []
    
    for o in range(0, len(offset_dict)):
        # balance in order defined in lookup
        for key, info in offset_dict.items():
            if info['order'] == o and o >= primary_order:
                order_list.append(info)
                
    return order_list



def offset_selector(airplane, passenger, offset_dict):
    
    # randomly selected these, probably should research a bit more to be specific
    min_age = 10
    max_age = 55
    
    # based on current airplane occupancy and booking, what is the best possible offset
    order_of_offsets = order_offset_list(offset_dict)
    
    if airplane.free_seats == 0:
        best_offset = order_of_offsets[-1]
        return best_offset
        
    else:
        best_offset = None

    # start from the least spacing and go to most spacing offset method
    o = 0
    while best_offset is None and o < len(order_of_offsets)-1:
        offset = order_of_offsets[o]
        buffer = float(order_of_offsets[o]['buffer_ratio'].split(':')[1])
        
        # recalculate requirements
        buffer = int(1+buffer)
        enough_space = (buffer <= airplane.free_seats)
        
        if passenger.group_size > 1:
            hyst = 2
        else:
            hyst = 0
        
        if enough_space and passenger.has_preexisting_condition and o >= hyst:
            best_offset = offset
        
        elif enough_space and passenger.group_size == 1:
                
            # allow o >= 1 for travel history
            if passenger.has_travelled and o >= 2:
                best_offset = offset

            # allow o >= 2
            elif passenger.age > max_age and o >= 3:
                best_offset = offset
                
            # allow o >= 3
            elif passenger.age < min_age and o >= 3:
                best_offset = offset
            
            # Don't allow all the group passengers to take all the offsets unless they qualify above
            elif o >= 4:
                best_offset = offset          
            
            # this else, is for passengers that shouldn't qualify for social distancing in earlier elif's
            else:
                o += 1

            
        # this else, is for when not enough space in current offset, just skip to next one
        else:
            o += 1
    
    # this if, used after while loop is done, and we run out of offset cases to check        
    if best_offset is None:
        best_offset = order_of_offsets[-1]


    
    return best_offset



###################################################################################################
# Function: seat_distance(Input)
# Input:    (airplane: airplane class, 
#           seat_1 : a seat of origin, 
#           seat_2: any other seat in Airplane class Object)
#
# Ouput: tuple showing the x distance from secondary seat to the seat of origin 
#
# Comment: Origin is where Passenger with possibleSocial Distance Requirement is assigned
#          and the distance tuple will be inserted into cell of DataFrame to inform how 
#          far away the passenger is, to avoid close proximity

def seat_distance(airplane, seat_1, seat_2):
    seat_1_row = int(seat_1[:-1])
    seat_1_col = seat_1[-1]

    seat_2_row = int(seat_2[:-1])
    seat_2_col = seat_2[-1]

    seat_1_index = 0
    seat_2_index = 0

    for ndx in range(0, len(airplane.seat_letters)):
        if seat_1_col == airplane.seat_letters[ndx]:
            seat_1_index = ndx

        if seat_2_col == airplane.seat_letters[ndx]:
            seat_2_index = ndx

    # + means go right from seat 1, - go left
    x_distance = seat_1_index - seat_2_index

    # + means move up (lower row #) - move back (higher row #)
    y_distance = seat_1_row - seat_2_row

    return (x_distance, y_distance)




###################################################################################################
# Function: SeatPassenger(Input)
# Input:    (airplane:   Airplane class object
#            offset: use default if not specified
#                  needs a list:   block - this is list of tuples, containing row/col pair for each seat in the
#                   block of reserved seats for social distancing
#  
#
# Ouput: None
#
# Object Update: This function iupdates the airplane Class object with new seat states in this 
#                seat_list, The main seat of interest will get a 'P', and each block will be updated with
#                a distance from the main seat of interest (airplane.next_seat)

def SeatPassenger(airplane, blocked_seat_list=[], occupied_state='P'):
    # check for offset and set default if not specified

    # Quick check if Plane is Full
    if airplane.next_seat is None:
        # CHECK FULL
        print("SEAT PASSENGER CHECK: Airplane Possible Full")
        return

    if blocked_seat_list == []:
        # this is default offset, no blocked seats SocialDistance function
        pass

    else:   

        # now if there IS a seat_list, fill the seat states in with distance tuples
        for seat_tuple in blocked_seat_list:
            row = int(seat_tuple[0])
            col = seat_tuple[1]
            block_seat = str(row) + col
            
            distance = seat_distance(airplane, airplane.next_seat, block_seat)

            if airplane.cabin.loc[row, col] == 'P' or airplane.cabin.loc[row, col] == 'G':
                pass
                                                
            # if currently an integer, overwrite
            elif isinstance(airplane.cabin.loc[row, col], int):
                new_list = list()
                new_list.append(distance)
                airplane.cabin.loc[row, col] = new_list
    
            elif isinstance(airplane.cabin.loc[row, col], list):
                # this is the case where a distance is already initialized in seat_state
                xy_list = airplane.cabin.loc[row, col]
                if distance not in xy_list:
                    xy_list.append(distance)
                    airplane.cabin.loc[row, col] = xy_list
            
            # elif isinstance(airplane.cabin.loc[row, col], int):
            #     new_list = list()
            #     new_list.append(str(distance))
            #     airplane.cabin.loc[row, col] = new_list
    
            # elif isinstance(airplane.cabin.loc[row, col], list):
            #     # this is the case where a distance is already initialized in seat_state
            #     xy_list = airplane.cabin.loc[row, col]
            #     if str(distance) not in xy_list:
            #         xy_list.append(str(distance))
            #         airplane.cabin.loc[row, col] = xy_list
                    
            elif isinstance(airplane.cabin.loc[row, col], str):
                # this is the case where a distance is already initialized in seat_state
                print("SHOULD NOT BE HERE")
                xy_list = []
                xy_list.append(airplane.cabin.loc[row, col])
                if str(distance) not in xy_list:
                    xy_list.append(str(distance))
                    airplane.cabin.loc[row, col] = xy_list
                                
            else:
                print("HOW DID I GET HERE in SEAT PASSENGER")

    
    # assign actual passenger to seat, after blocked list is set
    current_row = int(airplane.next_seat[:-1])
    current_col = airplane.next_seat[-1]
    airplane.cabin.loc[current_row, current_col] = occupied_state
    airplane.last_assigned_seat = airplane.next_seat 
    
    
    return



###############################################################################

def update_seat_roster(df, sub_df):
    # now update the main df_passenger dataframe with this information from each df_group
    for row in sub_df.index:
        df.loc[row, :] = sub_df.loc[row, :]
    
    return df


###############################################################################
# SINGLE SEATING FUNCTION
###############################################################################
    
def single_AssignSeat(airplane, df, offset_info):
    sort_on = ['number_of_flags', 'age']
    df = df.sort_values(by=sort_on, ascending=False)
    
    for row in df.index: 
        pID = df.loc[row, 'pID']
        this_psgr = Passenger(pID)
    
        age = df.loc[row, 'age']
        group = []
        has_travelled = df.loc[row, 'has_travelled']
        has_precon = df.loc[row, 'has_preexisting_condition']
    
        this_psgr.fill_questionare(age, group, has_travelled, has_precon)        
        this_offset_detail = offset_selector(airplane, this_psgr, offset_info)
        this_offset = this_offset_detail['offset']

        df.loc[row, 'offset_order'] = this_offset_detail['order'] 
        df.loc[row, 'offset_x'] = this_offset['x']
        df.loc[row, 'offset_y'] = this_offset['y']
        df.loc[row, 'offset_method'] = this_offset['method']
            
        blocked_seat_list = SocialDistance(airplane, this_offset, occupied_state='P')
        SeatPassenger(airplane, blocked_seat_list, occupied_state='P')
        
        # assert prev_assigned_seat != airplane.last_assigned_seat, "Unsuccessful Seating!"
        
        df.loc[row, 'seat'] = airplane.last_assigned_seat
        
        single_find_next_seat(airplane)
        airplane.update()

        
    return df



###############################################################################

###############################################################################
# GROUP SEATING FUNCTIONS
###############################################################################



def group_ToggleState(airplane, group_df):
    # this should be performed after every group AssignSeat is completed    
    for psgr in group_df.index:
        seat = group_df['seat'][psgr]
        seat_row = int(seat[:-1])
        seat_col = seat[-1]
        old_seat_state = airplane.cabin[seat_col][seat_row]     
        if old_seat_state == 'G':
            airplane.cabin.loc[seat_row, seat_col] = 'P'
            
    assert ((airplane.cabin == 'G').sum(axis=1)).sum(axis=0) == 0, "CLEAN UP GROUPS!"
    return


def find_members_in_group(df, member_list):
    # Build group data frame by filtering down from all groups of this size to just members
    try:
        group_df = pd.DataFrame()
        for memberID in member_list:
            this_member = df[df['pID'] == memberID]
            group_df = pd.concat([group_df, this_member], axis=0)

        return group_df
    
    except Exception as e:
        print(e)



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
        # this_row = group_df[group_df.index == row]
        pID = group_df.loc[row, 'pID']
        this_psgr = Passenger(pID)

        age = group_df.loc[row, 'age']
        group = group_df.loc[row, 'group']
        has_travelled = group_df.loc[row, 'has_travelled']
        has_precon = group_df.loc[row, 'has_preexisting_condition']

        this_psgr.fill_questionare(age, group, has_travelled, has_precon)        
        this_offset_detail = offset_selector(airplane, this_psgr, offset_dict)
        this_offset = this_offset_detail['offset']

        group_df.loc[row, 'offset_order'] = this_offset_detail['order'] 
        group_df.loc[row, 'offset_x'] = this_offset['x']
        group_df.loc[row, 'offset_y'] = this_offset['y']
        group_df.loc[row, 'offset_method'] = this_offset['method']

        #group passenger seating method
        # Allowed Group Passenger Seat_State = 'G'        
        blocked_seat_list = SocialDistance(airplane, this_offset, occupied_state='G')
        SeatPassenger(airplane, blocked_seat_list, occupied_state='G')
        
        #if prev_assigned_seat is not None and success < len(group_list)-1:
        #    assert prev_assigned_seat != airplane.last_assigned_seat, "Unable to Seat"
        
        group_df.loc[row, 'seat'] = airplane.last_assigned_seat
        success += 1
        group_find_next_seat(airplane)
        airplane.update()


    assert success == len(group_list), "NOT ALL PASSENGERS IN GROUP SEATED"
    group_ToggleState(airplane, group_df)  
    group_find_next_seat(airplane)
    
    return group_df

###################################################################################################