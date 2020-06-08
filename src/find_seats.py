# -*- coding: utf-8 -*-

###############################################################################

def convert_string_tuple_to_x_y(string_tuple):
    x = 0
    y = 0
    try:
        assert isinstance(string_tuple, str)
    except:
        string_tuple = string_tuple[0]
        
    string_tuple = string_tuple.split('(')[1] # remove open parenthesis
    string_tuple = string_tuple.split(')')[0] # remove close parenthesis
    string_tuple = string_tuple.split(', ') # remove comma+space
    
    x = int(string_tuple[0])
    y = int(string_tuple[1])
    
    return x, y


###################################################################################################                

def find_next_seat(airplane, search_for_state=int(0)):
    # Open Seat is defined as int(0) Seat State
    # *EDIT: this function no longer is recursive
    #        too easily stuck in while loops from testing phase
    if search_for_state == 0:
        check_row = int(airplane.next_seat[:-1])
        search_cols = airplane.priority_seat_order
    else:
        # START from bottom row
        check_row = airplane.start_row + airplane.rows
        search_cols = []
        for col in airplane.seat_letters:
            if col != ' ':
                search_cols.append(col)

    skip_seat_state = int(1)
    found_seat_state = False

    while not found_seat_state and check_row >= airplane.start_row:
        for i in range(0, len(search_cols)):
            check_col = search_cols[i]
            seat_state = airplane.cabin.loc[check_row, check_col]
            if seat_state == search_for_state:
                found_seat_state = True
                next_col = check_col
                next_row = check_row
                airplane.next_seat = str(next_row) + next_col
                return

            else:
                pass

        check_row -= 1


    # After iterating through each row from back to front, 
    # if no seats are OPEN, then find first skipped seat
    if check_row < airplane.start_row and search_for_state != skip_seat_state:            
        find_next_seat(airplane, skip_seat_state)

    elif check_row < airplane.start_row and search_for_state == skip_seat_state:
        # print("CHECK IF AIRPLANE FULL")
        # print(airplane.next_seat)
        # print(airplane.last_assigned_seat)
        return

    else:
        print("NOT SURE WHAT HAPPENED HERE")



###################################################################################################        

def group_find_next_seat(airplane):

    # Group Search Method:
    # CASE 1: Find adjacent seat to right until aisle
    # CASE 2: GO UP one row (prev_row - 1) and left most option (window or aisle)
    # CASE 3: Cycle back to back row in next column over      

    # This just means we should not call this function if we have not assigned ANY seats yet
    prev_seat = airplane.last_assigned_seat

    # get index/col info for seat
    prev_row = int(prev_seat[:-1])
    prev_col = prev_seat[-1]        

    # translate col letter to number
    col_index_lookup = {}
    
    for i in range(0, len(airplane.seat_letters)):
        col = airplane.seat_letters[i]
        col_index_lookup[col] = i
                   
    prev_col_index = col_index_lookup[prev_col]
                   
    # initialize next_col_index then run checks
    next_col_index = prev_col_index

    # for aisle to the right seats in L and M columns cycle back and move forward a row
    if next_col_index+1 != len(airplane.seat_letters) and airplane.seat_letters[next_col_index+1] == ' ':
        while next_col_index > 0 and airplane.seat_letters[next_col_index-1] != ' ':
            next_col_index -= 1
        # Then jump forward one row, once cycled back around in seat columns
        if prev_row > airplane.start_row:
            next_row = prev_row -1
        
        # Jump the aisle from original seat and go to the back 
        else:
            next_row = airplane.start_row + airplane.rows
            # Need to reset and find first open seat in next column
            next_col_index = prev_col_index

            while airplane.seat_letters[next_col_index-1] != ' ':
                next_col_index += 1

            


    # now for aisle to the left seats in M and R column
    elif next_col_index != len(airplane.seat_letters)-1 and airplane.seat_letters[next_col_index-1] == ' ':
        # just in case we have some wierd middle aisle of one seat run this loop
        while next_col_index < len(airplane.seat_letters)-1 and airplane.seat_letters[next_col_index+1] != ' ':
            next_col_index += 1
        next_row = prev_row

    # all middle seats L M R columns
    elif next_col_index < len(airplane.seat_letters)-1:
        next_col_index += 1
        next_row = prev_row

    # if at the R window, go back (our find open seat function jumps here 2nd)
    elif next_col_index == len(airplane.seat_letters)-1 and prev_row != airplane.start_row:
        next_col_index -= 1
        next_row = prev_row
                   
    elif next_col_index == len(airplane.seat_letters)-1 and prev_row == airplane.start_row:
        print("PLANE IS POSSIBLY FULL")
        airplane.view_plane()

    else:
        print("MISSING THIS CASE")

        check_seat = str(next_row) + airplane.seat_letters[next_col_index]
        check_seat_state = airplane.this_seat_state(check_seat)
        if check_seat_state != 'P' and check_seat_state != 'G':
            next_row = prev_row - 1




    next_col = airplane.seat_letters[next_col_index]
    try_next_seat = str(next_row) + next_col
    this_state = airplane.this_seat_state(try_next_seat)
    
    print("THIS IS MY NEXT SEAT STATE: ", this_state)
    print(this_state)
    
    if isinstance(this_state, int):
        airplane.next_seat = try_next_seat
        
    elif isinstance(this_state, list):
        # Now ensure we don't overwrite a reserved seat for social distancing
        in_group = True
        for blocked_seat in this_state:
            x_o, y_o = convert_string_tuple_to_x_y(blocked_seat)
            blocked_col_index = next_col_index + x_o
            blocked_col = airplane.seat_letters[blocked_col_index]
            blocked_row = next_row + y_o
            blocked_seat_check = airplane.cabin.loc[blocked_row, blocked_col]

            if blocked_seat_check == 'P':
                in_group = False
            else:
                pass

        # We are just skipping seats for the group, we are allowed to overwrite SD within same group
        if in_group:
            airplane.next_seat = try_next_seat

    else:
        print("NOT UPDATING ANYTHING ERROR!!!!")
    

    return                 

