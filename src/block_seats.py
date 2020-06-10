# -*- coding: utf-8 -*-
# Functions to form social distance block
from find_seats import find_next_seat, group_find_next_seat, single_find_next_seat

def horizontal_block(airplane, offset):
    horizontal_blocked_seats = list()
    
    try:
        # get offset information for x dim
        offset_x = offset['x']

        if offset_x < 1:
            print("This function should not have been called since offset_x = {}".format(offset_x))
            return horizontal_blocked_seats
        else:
            pass

        # obtain the current seat information stored in the Airplane Class Object under airplane.next_seat
        current_seat = airplane.next_seat
        current_row = int(current_seat[:-1])
        current_col = current_seat[-1]

        # Horizontal seat finding requires a quick lookup on which seat letter is in each index
        # find where the current seat is locate in the column (x-horizontal)
        x_start = 0
        for ndx in range(0, len(airplane.seat_letters)):
            if airplane.seat_letters[ndx] == current_col:
                x_start = ndx

        # block horizontal seats based on offset
        for x in range(1, offset_x+1):
            block_right_index = x_start + x
            block_left_index = x_start - x

            # Go Right, Avoid Out of Bounds on Right side of plane
            if block_right_index < len(airplane.seat_letters):
                
                # Avoid Aisles
                if airplane.seat_letters[block_right_index] != ' ':
                    
                    # Find Seat "letter" for the column
                    block_right_col = airplane.seat_letters[block_right_index]
                    
                    # add right seat to blocked seats list
                    blocked_seat = (current_row, block_right_col)    
                    horizontal_blocked_seats.append(blocked_seat)

            # Now Go Left, Avoid Out of Bounds on Left side of plane
            if block_left_index >= 0:
                
                # Avoid Aisles
                if airplane.seat_letters[block_left_index] != ' ':
                    
                    # Find Seat "letter" for the column
                    block_left_col = airplane.seat_letters[block_left_index]
                    
                    # add left seat to blocked seats list
                    blocked_seat = (current_row, block_left_col)
                    horizontal_blocked_seats.append(blocked_seat)
                    
                
    except Exception as e:
        print("horizontal_block Error: {}".format(e))

         
    return horizontal_blocked_seats

###################################################################################################

def vertical_block(airplane, offset):
    vertical_blocked_seats = list()
    
    try:
        # get offset information for y dim
        offset_y = offset['y']

        if offset_y < 1:
            print("This function should not have been called since offset_y = {}".format(offset_y))
            return vertical_blocked_seats
        else:
            pass


        # obtain the current seat information stored in the Airplane Class Object under airplane.next_seat
        current_seat = airplane.next_seat
        current_col = current_seat[-1]
        y_start = int(current_seat[:-1])

        # block vertical seats in adjacent column seat groups (front and back y-vertical)
        for y in range(1, offset_y+1):
            block_front_row = int(y_start - y)
            block_behind_row = int(y_start + y)

            # Avoid Out of Bounds in Front of plane
            if block_front_row >= airplane.start_row:
                # add seat in front to blocked seats list
                blocked_seat = (block_front_row, current_col)
                vertical_blocked_seats.append(blocked_seat)

            # Avoid Out of Bounds in Back of plane
            if block_behind_row <= (airplane.start_row + airplane.rows):
                # add seat behind to blocked seats list
                blocked_seat = (block_behind_row, current_col)
                vertical_blocked_seats.append(blocked_seat)
    
    except Exception as e:
        print("vertical_block Error: {}".format(e))

    return vertical_blocked_seats
    
###################################################################################################

def ordinal_block(airplane, offset):
    ordinal_block_list = list()
    
    try:
    
        # get offset information, need method specified between Full Block and Shaved Corners
        offset_x = offset['x']
        offset_y = offset['y']
        method = offset['method']

        if method.lower() == 'full_block':
            corner = 1
        elif method.lower() == 'shaved_corners':
            corner = 0
        elif method.lower() == 'cardinal_only':
            print("This function should not have been called for method: {}".format(method))
            return ordinal_block_list
        else:
            print("Invalid Method: {}".format(method))
            assert 1 == 0

        if offset_y < 1:
            print("This function should not have been called since offset_y = {}".format(offset_y))
            return ordinal_block_list
        else:
            pass


        # obtain the current seat information stored in the Airplane Class Object under airplane.next_seat
        current_seat = airplane.next_seat
        current_col = current_seat[-1]
        y_start = int(current_seat[:-1])

        # Horizontal seat finding requires a quick lookup on which seat letter is in each index
        # find where the current seat is locate in the column (x-horizontal)
        x_start = 0
        for ndx in range(0, len(airplane.seat_letters)):
            if airplane.seat_letters[ndx] == current_col:
                x_start = ndx

        
        # now block ordinal directions, start each for loop at 1 to avoid duplicating work
        for y in range(1, offset_y+1):
            block_front_row = int(y_start - y)
            block_behind_row = int(y_start + y)

            # block Left and Right in the up and down rows  # REMOVE +1 in offset_x range to shave corners
            for x in range(1, int(offset_x + corner)):
                block_right_index = x_start + x
                block_left_index = x_start - x

                # Avoid Out of Bounds on Right side of plane
                if block_right_index < len(airplane.seat_letters):
                    
                    # Skip over Aisles
                    if airplane.seat_letters[block_right_index] != ' ': 
                        block_right_col = airplane.seat_letters[block_right_index]

                        # Avoid Out of Bounds in Front of plane
                        if block_front_row >= airplane.start_row:
                            blocked_seat = (block_front_row, block_right_col)
                            ordinal_block_list.append(blocked_seat)

                        # Avoid Out of Bounds in Back of plane   
                        if block_behind_row <= (airplane.start_row + airplane.rows):
                            blocked_seat = (block_behind_row, block_right_col)
                            ordinal_block_list.append(blocked_seat)

                
                # Avoid Out of Bounds on Left side of plane
                if block_left_index >= 0:
                    
                    # Skip over Aisles
                    if airplane.seat_letters[block_left_index] != ' ':
                        block_left_col = airplane.seat_letters[block_left_index]

                        # Avoid Out of Bounds in Front of plane
                        if block_front_row >= airplane.start_row:
                            blocked_seat = (block_front_row, block_left_col)
                            ordinal_block_list.append(blocked_seat)

                        # Avoid Out of Bounds in Back of plane
                        if block_behind_row <= (airplane.start_row + airplane.rows):
                            blocked_seat = (block_behind_row, block_left_col)
                            ordinal_block_list.append(blocked_seat)

    except Exception as e:
        print("ordinal_block Error: {}".format(e))
                            
    return ordinal_block_list



###################################################################################################

def create_sd_block_list(airplane, offset):
    # block seats based on offset and method
    # Example for cardinal direction
    # Up:     row+1 
    # Right:  col+1
    # Down:   row-1
    # Left:   col-1
    
    # create a list of Seat tuples (Row, Col) to reference in checking seat states and assigning distances
    blocked_seat_list = list()    
    
    try:
        offset_x = offset['x']
        offset_y = offset['y']
        method = offset['method']

        # if the method is cardinal only: 'co' then simply block horizontal and vertical
        if offset_x > 0:
            blocked_seats = horizontal_block(airplane, offset)
            blocked_seat_list += blocked_seats
        
        if offset_y > 0:
            blocked_seats = vertical_block(airplane, offset)
            blocked_seat_list += blocked_seats

        # now read the method to see if more seats need to be blocked
        if method != 'cardinal_only':
            blocked_seats = ordinal_block(airplane, offset)
            blocked_seat_list += blocked_seats
    
    
    except Exception as e:
        print("create_sd_block_list Error: {}".format(e))
        print("No Offset for Social Distance Specified, Empty List")
        return blocked_seat_list
    
  
    return blocked_seat_list



def build_block(airplane, seat_list):    
    # find min/max row for block within airplane (subset of dataframe)
    min_row = airplane.start_row + airplane.rows + 1
    max_row = airplane.start_row - 1
    max_col_ndx = -1
    min_col_ndx = len(airplane.seat_letters)+1
    
    # check seats in block to find boundary within plane to build the dataframe
    for seat in seat_list:
        row = seat[0]
        col = seat[1]

        for i in range(0, len(airplane.seat_letters)):
            check_col = airplane.seat_letters[i]
            if check_col == col:
                col_ndx = i

        if row < min_row:
            min_row = row
        
        if row > max_row:
            max_row = row

        if col_ndx < min_col_ndx:
            min_col_ndx = col_ndx
        
        if col_ndx > max_col_ndx:
            max_col_ndx = col_ndx



    row_range = list(range(min_row, max_row+1))
    col_range = airplane.seat_letters[min_col_ndx:max_col_ndx+1]

    # build the initial block to check, and pull from plane Dataframe to check seat states
    block_df = airplane.cabin.loc[row_range, col_range]
    try:
        block_df = block_df.drop([' '],axis=1)
    except:
        # no aisles in block_df
        pass
    
    
    return block_df

###################################################################################################

def read_block(block_df, seat_list):
    for row in block_df.index:
        for col in block_df:
            
            # check the seat tuple in list
            block_df_seat = (row, col)
            if block_df_seat not in seat_list:
                # ignore state by overwriting in the block_df *WHY THIS WORKS
                block_df.loc[row, col] = 'X'
            else:
                pass
    
    # calculate the number of passengers in this block after setting 'X' if seat not in reserved list
    number_of_passengers_in_block = int((block_df == 'P').sum(axis=1).sum(axis=0))
    
    return number_of_passengers_in_block
    

# *WHY THIS WORKS:
# Because we have already built in the function to only check for seat availability on seats with 
# integer type states int(0) or int(1) in the "find_open_seat" function, the next seat will only be 
# chosen from seats that don't already have a passenger (duh) or are NOT reserved for social distance
# spacing requirements (denoted either as string tuples or 'X')

   
    
###################################################################################################
# Function: check_blocked_seats(Input)
# Input:    (airplane:   Airplane class object
#           list:   block - this is list of tuples, containing row/col pair for each seat in the
#                   block of reserved seats for social distancing
#  
#
# Ouput: this has True/False check output

def check_blocked_seats(airplane, seat_list):  
    
    # build the initial block to check
    block_df = build_block(airplane, seat_list)
    
    # the block builder will create a rectangular block, to avoid incorrect checks on the block 
    # within the plane run a check and use seat list to avoid over-checking
    passengers_in_block = read_block(block_df, seat_list)

    if passengers_in_block == 0:
        return True
    
    else:
        return False  



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

def SocialDistance(airplane, offset, occupied_state='P'):     
    # use modular functions to create Social Distance: 'SD' block list of seats 
#     try:
    blocked_seat_list = create_sd_block_list(airplane, offset)

    # now check the blocked seat list to ensure no passengers are encroaching on Social Distance Offset
    check_flag = check_blocked_seats(airplane, blocked_seat_list)


    if check_flag:
        # continue onward, this blocked seat list is GOOD!
        return blocked_seat_list
    else:
        before_skip = airplane.next_seat
        airplane.skip_seat()
        
        if occupied_state == 'P':
            single_find_next_seat(airplane, skip_ok=False)
        elif occupied_state == 'G':
            group_find_next_seat(airplane, skip_ok=False)
        else:
            print("ERROR OCCUPIED STATE IN SOCIAL DISTANCE")
                    
        after_skip = airplane.next_seat

        assert after_skip != before_skip, "NOT UPDATING SEAT IN SOCIAL DISTANCE RECURSION"       

        return SocialDistance(airplane, offset, occupied_state)



