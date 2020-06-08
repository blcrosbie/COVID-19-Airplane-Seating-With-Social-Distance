# -*- coding: utf-8 -*-

# use information based on Model of airplane, for economy seating

import pandas as pd

# 1. Boeing 787 
#    - rows in economy : 17 
#    - columns: 3
#    - seats per col (spc): 3-3-3  # ABC DEF GHJ

    
# 2. Boeing 737
#    - rows in economy : 18
#    - columns: 2
#    - seats per col: 3-3 # ABC DEF

# 3. Airbus 380
#    - rows in economy : 43
#    - columns: 3
#    - seats per col: 3-4-3 # ABC DEFG HJK


# create global lookup for airplane models
airplane_dictionary = {
        'Boeing_787': {'start_row': 14, 'rows': 17, 'columns': 3, 'seat_letters': ['A', 'B', 'C', ' ', 'D', 'E', 'F', ' ', 'G', 'H', 'J']},
        'Boeing_737': {'start_row': 8, 'rows': 18, 'columns': 2, 'seat_letters': ['A', 'B', 'C', ' ', 'D', 'E', 'F']},
        'Airbus_380': {'start_row': 43, 'rows': 40, 'columns': 3, 'seat_letters': ['A', 'B', 'C', ' ', 'D', 'E', 'F', 'G', ' ', 'H', 'J', 'K']}}

# global character str for aisle visual
aisle = '| |'
# Create Airplane Class Object

class Airplane:

    def __init__(self, model):
        self.make = model.split('_')[0]
        self.model = model.split('_')[1]
        print("Building {} {} ...\n".format(self.make, self.model))
        self.start_row = airplane_dictionary[model]['start_row']
        self.rows = airplane_dictionary[model]['rows']
        self.columns = airplane_dictionary[model]['columns']
        self.seat_letters = airplane_dictionary[model]['seat_letters']
        self.capacity = 0
        self.next_seat = None
        self.last_assigned_seat = None
        

    # Create: 
    
    def create_cabin(self, capacity):
        df_rows = list(range(self.start_row, (self.start_row + self.rows + 1)))
        df_cols = self.seat_letters
        cabin = pd.DataFrame(index=df_rows, columns=df_cols, dtype=object).fillna(0)
        
        # assign the initialized pandas dataframe to the Airplane attribute self.cabin
        self.cabin = cabin
        # create columns with ' ' to visualize open aisles
        for col in self.cabin.columns:
            if col == ' ':
                self.cabin[col] = aisle
            else:
                self.cabin[col] = self.cabin[col].astype(object)
        
        # User defined
        self.capacity = capacity
        
        # each cell of DataFrame for open seat has a state set to int(0)
        # summing all 0's will provide an available seat count
        self.total_seats = ((self.cabin == 0).sum(axis=1)).sum(axis=0)
        
        # remaining seats will be the # of passengers on this flight based on the booked capacity (random)
        self.booked_seats = int(self.total_seats*capacity)
        self.remaining_seats_to_assign = self.booked_seats
        
        # the buffer is the count of seats devoted to social distancing 
        self.buffer_seats = 0
        
        # available seats are non-buffer, and are vacant for passengers
        self.free_seats = self.total_seats - self.booked_seats
        
        # Seat Names will appear like: '35C' for the ticket assigned seat
        # self.next_seat acts as a "cursor" to the airplane
        # we initialize the cursor at the last row number and first seat column letter
        self.next_seat = str(max(df_rows)) + str(df_cols[0])  
        
        # the last assigned seat will be tracked as the last seat that had the state 
        # toggled from int(0) or int(1) to 'P', the self.first_skip will be set to None
        self.first_skip = None
        
        # open row counter will allow us to easily assign open rows if capacity of the flight is low enough
        self.open_rows = self.columns * self.rows
        
        # create the prioritized columns list based on airplane model and available seat selection
        self.priority_seat_order = self.prioritize_columns()
    
    # Read: 
    
    def view_plane(self, pretty=True, details=True):
        if details:
            self.details()
            
        if pretty:
            pretty_cabin = self.cabin.copy()
            for row in pretty_cabin.index:
                for col in pretty_cabin.columns:
                    if isinstance(pretty_cabin.loc[row, col], list):
                        pretty_cabin.loc[row, col] = '+'
                    elif isinstance(pretty_cabin.loc[row, col], str) and pretty_cabin.loc[row, col] != 'P':
                        pretty_cabin.loc[row, col] = '+'
                            
                    else:
                        pass
                        
            print(pretty_cabin)
            
        else:
            print(self.cabin, '\n')
    
    # Update - look at seat details: 
    
    def update(self):
        
        remain = self.booked_seats
        remain -= ((self.cabin == 'P').sum(axis=1)).sum(axis=0)
        remain -= ((self.cabin == 'G').sum(axis=1)).sum(axis=0)
        self.remaining_seats_to_assign = remain
        
        buf = self.total_seats
        buf -= ((self.cabin == 0).sum(axis=1)).sum(axis=0)
        buf -= ((self.cabin == 'P').sum(axis=1)).sum(axis=0)
        buf -= ((self.cabin == 'G').sum(axis=1)).sum(axis=0)
        buf -= ((self.cabin == 1).sum(axis=1)).sum(axis=0)
        self.buffer_seats = buf
        
        self.free_seats = self.total_seats - self.booked_seats - self.buffer_seats 
        assert self.free_seats >= 0, "Buffer Overflow!"
    
    
    def details(self):
        # Get Stats on Plane
        print("{} {} \n".format(self.make, self.model))
        print("Total Seats: {}".format(self.total_seats))
        print("Capacity: {}%".format(round(self.capacity*100, 3)))
        print("Booked Seats: {}".format(self.booked_seats))     
        print("Remaining Seats to Assign: {}".format(self.remaining_seats_to_assign))
        print("Buffer Seats: {}".format(self.buffer_seats))
        print("Free Seats: {}".format(self.free_seats))

#         self.count_open_rows()
#         print("Total Open Rows: {}".format(self.open_rows))
        
        print("Last Assigned Seat: {}".format(self.last_assigned_seat))
        print("Next Seat to Assign: {}".format(self.next_seat))
        print("\n")
        

    # Delete - Clear out plane with new initialized DataFrame
    def deplane(self):
        self.next_seat = str(self.start_row + self.rows) + str(self.seat_letters[0])
        self.last_assigned_seat = None
        # plane_index = list(range(self.start_row, self.start_row+self.rows+1))
        # self.cabin = pd.DataFrame(index=plane_index, columns=self.seat_letters, dtype=object).fillna(0)
        for col in self.seat_letters:
            if col == ' ':
                self.cabin[col] = aisle
            else:
                self.cabin[col] = 0
                self.cabin[col] = self.cabin[col].astype(object)
            
        
        self.remaining_seats_to_assign = self.booked_seats
        self.free_seats = self.total_seats - self.booked_seats
        self.buffer_seats = 0

    def __del__(self):
        self.deplane()
        
        
    
###################################################################################################


    def prioritize_columns(self):
        seat_columns = self.seat_letters[:]
        search_priority_list = list()
                
        # possible use "this" row as a way to switch window/aisle alternating priority
#        this_row = int(self.next_seat[:-1])
        
        # start with windows
        search_priority_list.append(seat_columns[0])
        search_priority_list.append(seat_columns[(len(seat_columns)-1)])
        

        # then add in aisle seats

        for i in range(1, len(seat_columns)-1):
            check_col = seat_columns[i]
            next_col = seat_columns[i+1]
            prev_col = seat_columns[i-1]
            
            if next_col == ' ' or prev_col == ' ':
                search_priority_list.append(check_col)

        # this should add all aisle seats, now fill in middle seats in order

        for i in range(1, len(seat_columns)-1):
            col = seat_columns[i]
            if col not in search_priority_list:
                search_priority_list.append(col)
            
        
        search_priority_list.remove(' ')
        return search_priority_list
                              

        
# ###################################################################################################  
            
    def find_last_assigned_seat(self):
        # limit while loop checks
        attempts = self.total_seats
        
        # start from the top
        check_row = self.start_row
        max_row = self.start_row + self.rows
        
        # initialize seat state
        seat_state = 0
        
        # to go from R to L, need to subtract i index
        max_col_ndx = len(self.seat_letters)
        
        while attempts >= 0 and (seat_state != 'P' and seat_state != 'G'):
            
            for i in range(1, max_col_ndx+1):
                check_col = self.seat_letters[max_col_ndx - i]
                if check_col == ' ':
                    pass
                else:
                    seat_state = self.cabin.loc[check_row, check_col]
                    
                    if seat_state == 'P':
                        self.last_assigned_seat = str(check_row) + check_col
                        break
            
            if check_row < max_row:
                check_row += 1
            
            attempts -= 1
            
        if attempts < 0:
            print("No Seats have been assigned on this flight")
            self.last_assigned_seat = None
            
     
    
###################################################################################################              
        
    def seats_in_row(self, seat):
        # find seat count in current row
        current_seat = seat
#        current_row = int(current_seat[:-1])
        current_col = current_seat[-1]
        
        current_index = 0
        for i in range(0, len(self.seat_letters)):
            if current_col == self.seat_letters[i]:
                current_index = i
            else:
                pass
            
        left_add = 0
        right_add = 0
        seats_in_row = 0
        
        while (current_index - left_add) > 0:
            if self.seat_letters[current_index - left_add] == ' ':
                left_add -= 1
                break
            else:
                left_add += 1

            
        while (current_index + right_add) < len(self.seat_letters):
            if self.seat_letters[current_index + right_add] != ' ':
                right_add += 1
            else:
                break
                
        seats_in_row = left_add + right_add
        return seats_in_row
        
###################################################################################################  

    def count_open_rows(self):
        open_row_count = 0
        row_sections = ('').join(self.seat_letters).split()            
        
        for row in range(self.start_row, self.start_row+self.rows+1):
            for section in row_sections:
                open_seats_in_row = 0
                
                for col in section:
                    check_seat = str(row) + col
                    num_seats_in_this_row = self.seats_in_row(check_seat)
                    seat_state = self.cabin.loc[row, col]

                    if seat_state == 0:
                        open_seats_in_row += 1

                
                if open_seats_in_row == num_seats_in_this_row:
                    open_row_count += 1
              
        self.open_rows = open_row_count         

###################################################################################################           
    # Method name: self.next_seat_state(Input)
    # Input:       (self: airplane class object)
    #
    # Reads the current state of the seat in assign queue (cursor) referenced as self.next_seat
    # Seat States:
    
    def next_seat_state(self):
        row = int(self.next_seat[:-1])
        col = self.next_seat[-1]
        
        return self.cabin.loc[row, col]
    
    def this_seat_state(self, seat):
        row = int(seat[:-1])
        col = seat[-1]
        
        return self.cabin.loc[row, col]
    
#     @staticmethod
    def free_seat_state(self, seat):
        row = int(seat[:-1])
        col = seat[-1]
        self.cabin.loc[row, col] = 0
        return
        
    
    ###################################################################################################        
    # Method name: self.skip_seat(Input)
    # Input:       (self: airplane class object)
    #
    # Skips over the current seat, fills in with int(1) seat state and updates "next_seat"
    #      
    def skip_seat(self):    
        if isinstance(self.next_seat_state, int):
            skip_row = int(self.next_seat[:-1])
            skip_col = self.next_seat[-1]
            # if the seat state is 0 or 1, then it is fine to toggle to skipped seat state status=1
            self.cabin.loc[skip_row, skip_col] += 1    
    
        else:
            print("WHAT HAPPENED IN SKIP SEAT!")
        
        return
