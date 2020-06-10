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
        # check_row = int(airplane.next_seat[:-1])
        check_row = int(airplane.start_row + airplane.rows)
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
        print("FIND NEXT SEAT: NOT SURE WHAT HAPPENED HERE")



###################################################################################################        

def group_find_next_seat(airplane, skip_ok=True):

    # Group Search Method:
    # CASE 1: Find adjacent seat to right until aisle
    # CASE 2: GO UP one row (prev_row - 1) and left most option (window or aisle)
    # CASE 3: Cycle back to back row in next column over      

    # This just means we should not call this function if we have not assigned ANY seats yet
    if skip_ok == True:
        prev_seat = airplane.last_assigned_seat
    else:
        prev_seat = airplane.next_seat
      
    # translate col letter to number
    col_index_lookup = {}
    
    for i in range(0, len(airplane.seat_letters)):
        col = airplane.seat_letters[i]
        col_index_lookup[col] = i
                   

    available_state = False
    attempts = airplane.total_seats
    
    while attempts >= 0 and not available_state:
       attempts -= 1
       # get index/col info for seat
       prev_row = int(prev_seat[:-1])
       prev_col = prev_seat[-1]  
       prev_col_index = col_index_lookup[prev_col]
                   
       # initialize next_col_index then run checks
       next_col_index = prev_col_index
          
       
       # for aisle to the right seats in L and M columns cycle back and move forward a row
       if next_col_index+1 < len(airplane.seat_letters) and airplane.seat_letters[next_col_index+1] == ' ':
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
       
       # # THIS WAS RIGHT SHIFT FOR PREVIOUS METHOD COMBO PRIORITY SEATING 
       # # now for aisle to the left seats in M and R column
       # elif next_col_index < len(airplane.seat_letters)-1 and airplane.seat_letters[next_col_index-1] == ' ':
       #     # just in case we have some wierd middle aisle of one seat run this loop
       #     while next_col_index < len(airplane.seat_letters)-1 and airplane.seat_letters[next_col_index+1] != ' ':
       #         next_col_index += 1
       #     next_row = prev_row

      
       # all middle seats L M R columns, make sure don't hit edge of Right window, and no increment into aisle
       elif next_col_index+1 < len(airplane.seat_letters) and airplane.seat_letters[next_col_index+1] != ' ':
           next_col_index += 1
           next_row = prev_row  
           
      # if at the R window, go back to aisle and move up row, unless at front of plane
       elif next_col_index+1 == len(airplane.seat_letters) and prev_row != airplane.start_row:
           while airplane.seat_letters[next_col_index-1] != ' ':
               next_col_index -= 1
           next_row = prev_row - 1
           
       # now if at Right Window and Start Row, the plane is most likely full    
       elif next_col_index+1 == len(airplane.seat_letters) and prev_row == airplane.start_row:
           print("PLANE IS POSSIBLY FULL")
           print("Was it OK to skip in this check?\t", skip_ok)
           airplane.view_plane()
       else:
           print("MISSING THIS CASE")
       
 
       # THAT'S ALL THE CASES ABOVE, NOW CONFIRM SEAT IS OPEN, ELSE CHECK AGAIN
       # Now Run Checks on seat state to not overwrite
       check_seat = str(next_row) + airplane.seat_letters[next_col_index]
       check_seat_state = airplane.this_seat_state(check_seat)
       if isinstance(check_seat_state, int):
           if check_seat_state == 0:
               available_state = True
           elif skip_ok and check_seat_state > 0:
               available_state = True
           else:
               prev_seat = check_seat
               
                  
       elif isinstance(check_seat_state, str):
           prev_seat = check_seat
       # Now ensure we don't overwrite a reserved seat for social distancing
       elif isinstance(check_seat_state, list):
           in_group = True
           for blocked_seat in check_seat_state:
               x_o = int(blocked_seat[0])
               y_o = int(blocked_seat[1])
               # x_o, y_o = convert_string_tuple_to_x_y(blocked_seat)
               blocked_col_index = next_col_index + x_o
               blocked_col = airplane.seat_letters[blocked_col_index]
               blocked_row = next_row + y_o
               blocked_seat_check = airplane.cabin.loc[blocked_row, blocked_col]
               
               if blocked_seat_check == 'P':
                   in_group = False
           
           # We are just skipping seats for the group, we are allowed to overwrite SD within same group
           if in_group:
               available_state = True
           else:
               prev_seat = check_seat

       
       # outside elif on list check
       else:
           prev_seat = check_seat
 
    # outside While Loop set next seat last step if at 00set to none  
    if attempts < 0:
        airplane.next_seat = None
        print("Plane maybe Full, try with skips?")
    else:
        airplane.next_seat = check_seat    
      
    return                 


###################################################################################################  


def single_find_next_seat(airplane, skip_ok=True):
    attempts = airplane.total_seats
    
    # if not skip_ok:
    #     seek_row = int(airplane.next_seat[:-1])
    #     seek_col_index = int(airplane.next_seat[-1])
    #     seek_col = airplane.seat_letters[seek_col_index]
    # else:
        
    
    seek_row = airplane.start_row + airplane.rows
    seek_col_index = -1
    # seek_col = airplane.seat_letters[seek_col_index]
    
    # check_seat_state = airplane.cabin.loc[seek_row, seek_col]
    
    available_state = False

    
    while attempts >= 0 and not available_state:
        attempts -= 1
        
        if seek_col_index < len(airplane.seat_letters)-1:
            seek_col_index += 1
            seek_col = airplane.seat_letters[seek_col_index]
            if seek_col == ' ':
                seek_col_index += 1
                seek_col = airplane.seat_letters[seek_col_index]
        
        else:
            seek_col_index = 0
            seek_col = airplane.seat_letters[seek_col_index]
            if seek_row > airplane.start_row:
                seek_row -= 1

            else:
                print("END OF THE LINE IN SIMPLE")
                airplane.next_seat = None
        
        check_seat_state = airplane.cabin.loc[seek_row, seek_col]
        if isinstance(check_seat_state, int):
            if check_seat_state == 0:
                available_state = True
            elif skip_ok:
                available_state = True
            else:
                available_state = False
                
        elif isinstance(check_seat_state, float):
            print("HOW IS IT A-FLOAT, ITS A PLANE....")
        else:
            pass

        
    if attempts < 0:
        print("GAME OVER, unless not yet skipping")
        airplane.next_seat = None
    
    else:
        airplane.next_seat = str(seek_row) + seek_col
