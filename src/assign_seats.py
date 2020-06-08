# -*- coding: utf-8 -*-

import pandas as pd


###############################################################################
def count_flags(*flags_to_check):
    flag_count = 0
    for flag in flags_to_check:
        if flag == True:
            flag_count +=1
            
    return flag_count

###############################################################################

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
    best_offset = None
    buffer = 0
    # req_seats = 1
    
    # start from the least spacing and go to most spacing offset method
    o = 0
    enough_space = False
    
    while best_offset is None and o < len(order_of_offsets):
        offset = order_of_offsets[o]['offset']
        buffer = float(order_of_offsets[o]['buffer_ratio'].split(':')[1])
        
        # recalculate requirements
        buffer = int(1+buffer)
        enough_space = (buffer <= airplane.free_seats)
        
        if enough_space:
            # allow o >= 0 for preexisting conditions
            if passenger.has_preexisting_condition:
                best_offset = offset
                # best_buffer = buffer
                order = o

            # allow o >= 1 for travel history
            elif passenger.has_travelled and o >= 1:
                best_offset = offset
                # best_buffer = buffer
                order = o

            # allow o >= 2
            elif passenger.age > max_age and o >= 2:
                best_offset = offset
                # best_buffer = buffer
                order = o
                
            # allow o >= 3
            elif passenger.age < min_age and passenger.group_size == 1 and o >= 3:
                best_offset = offset
                # best_buffer = buffer
                order = o
            
            # Don't allow all the group passengers to take all the offsets unless they qualify above
            elif passenger.group_size > 1 and o >= 4:
                best_offset = offset
                # best_buffer = buffer
                order = o
        else:
            best_offset = order_of_offsets[-1]
            buffer = 0
            order = len(order_of_offsets)-1
        
        
        # Don't forget the decrement
        o += 1

    print(o)
    best_offset.update({'order':order})
    
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

            distance = seat_distance(airplane, airplane.last_assigned_seat, block_seat)

            if airplane.cabin.loc[row, col] == 'P' or airplane.cabin.loc[row, col] == 'G':
                pass
        
            elif isinstance(airplane.cabin.loc[row, col], str):
                print("SHOULD NOT BE STRING UNLESS G or P above")
                                                
            # if currently an integer, overwrite
            elif isinstance(airplane.cabin.loc[row, col], int):
                new_list = list()
                new_list.append(str(distance))
                print(new_list)
                print(type(new_list))
                airplane.cabin.loc[row, col] = new_list
    
            elif isinstance(airplane.cabin.loc[row, col], list):
                # this is the case where a distance is already initialized in seat_state
                xy_list = airplane.cabin.loc[row, col]
                if str(distance) not in xy_list:
                    xy_list.append(str(distance))
                    airplane.cabin.loc[row, col] = xy_list
                    
            elif isinstance(airplane.cabin.loc[row, col], str):
                # this is the case where a distance is already initialized in seat_state
                xy_list = []
                xy_list.append(airplane.cabin.loc[row, col])
                if str(distance) not in xy_list:
                    xy_list.append(str(distance))
                    airplane.cabin.loc[row, col] = xy_list
                                
            else:
                print(type(airplane.cabin.loc[row, col]))
                print(airplane.cabin.loc[row, col])

    
    # assign actual passenger to seat, after blocked list is set
    current_row = int(airplane.next_seat[:-1])
    current_col = airplane.next_seat[-1]
    airplane.cabin.loc[current_row, current_col] = occupied_state
    airplane.last_assigned_seat = airplane.next_seat       
    
    
    return




###############################################################################
###############################################################################
###############################################################################
# GROUP SEATING FUNCTIONS


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

###############################################################################

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

###################################################################################################
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
def update_seat_roster(df, sub_df):
    # now update the main df_passenger dataframe with this information from each df_group
    for row in sub_df.index:
        df.loc[row, :] = sub_df.loc[row, :]
    
    return df