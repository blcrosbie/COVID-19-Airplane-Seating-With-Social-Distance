# -*- coding: utf-8 -*-

import pandas as pd

from offset_analyze import offset_selector



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

def SeatPassenger(airplane, occupied_state='P', **offset):
    # check for offset and set default if not specified
#     try:
        # Quick check if Plane is Full
    if airplane.next_seat is None:
        return

    # Now if Offset is specified or Need to use default
    if offset != default_offset:
        seat_list = SocialDistance(airplane, occupied_state, offset)
    else:
        offset = default_offset
        seat_list = []        

    if seat_list is None:
        # this is a failure on SocialDistance function
        return

    else:          
        # assign the main seat of interest (airplane.next_seat) regardless of seat_list
        current_row = int(airplane.next_seat[:-1])
        current_col = airplane.next_seat[-1]
        airplane.cabin.loc[current_row, current_col] = occupied_state
        airplane.last_assigned_seat = airplane.next_seat

        # Change method of next seat for group assignment method (no skipping around)
        find_next_seat(airplane)

        # now if there IS a seat_list, fill the seat states in with distance tuples
        for seat_tuple in seat_list:
            row = int(seat_tuple[0])
            col = seat_tuple[1]
            block_seat = str(row) + col

            distance = seat_distance(airplane, airplane.last_assigned_seat, block_seat)
            string_distance = (str(distance[0]), str(distance[1]))
            print("Cant handle type: ",type(airplane.cabin.loc[row, col]))
#                 # add case for GROUP PASSENGER = 'G', do not overwrite 'G'
#                 if airplane.cabin.loc[row, col] == 'G' and occupied_state == 'G':
#                     # skip over
#                     pass

            if airplane.cabin.loc[row, col] == 'P' or airplane.cabin.loc[row, col] == 'G':
                pass
        
            elif isinstance(airplane.cabin.loc[row, col], str):
                print("SHOULD NOT BE STRING UNLESS G or P above")
                
                
            elif airplane.cabin.loc[row, col] == aisle:
                print("THERE SHOULD BE NO AISLES!!! YOU MESSED UP!!!!!!")  
                
        
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
                if string_distance not in xy_list:
                    xy_list.append(string_distance)
                    airplane.cabin.loc[row, col] = xy_list
                    
            elif isinstance(airplane.cabin.loc[row, col], str):
                # this is the case where a distance is already initialized in seat_state
                xy_list = []
                xy_list.append(airplane.cabin.loc[row, col])
                if string_distance not in xy_list:
                    xy_list.append(string_distance)
                    airplane.cabin.loc[row, col] = xy_list



#             elif isinstance(airplane.cabin.loc[row, col], str):
#                 # this is the case where a distance is already initialized in seat_state
#                 first_state = airplane.cabin.loc[row, col]
#                 new_state_list = list()
#                 new_state_list.append(first_state)
#                 new_state_list.append(str(distance))
#                 airplane.cabin.loc[row, col] = new_state_list
                
                

            else:
                print(type(airplane.cabin.loc[row, col]))
                print(airplane.cabin.loc[row, col])

    
#     except Exception as e:
#         print("SeatPassenger Error: {}".format(e))           
    
    
    return


        


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
