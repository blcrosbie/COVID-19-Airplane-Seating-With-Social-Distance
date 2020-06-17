# -*- coding: utf-8 -*-

import os, sys
import time
import pandas as pd



LOCAL_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_DIR = os.path.dirname(LOCAL_SRC_DIR)
LOCAL_BASE_DIR = os.path.dirname(LOCAL_REPO_DIR)

LOCAL_MODELS_DIR = os.path.join(LOCAL_REPO_DIR, "models")
sys.path.append(LOCAL_MODELS_DIR)

from airplane import Airplane
from passenger import Passenger



def aisle_select(airplane, seat):
    seat_col = seat[-1]
    seat_col_index = [i for i in range(0, len(airplane.seat_letters)) if airplane.seat_letters[i] == seat_col]
    
    if airplane.columns > 2:
        left_aisle = [i for i in range(0, int(1+len(airplane.seat_letters)/2)) if airplane.seat_letters[i] == ' ']
        right_aisle = [i for i in range(int(len(airplane.seat_letters)/2), len(airplane.seat_letters)) if airplane.seat_letters[i] == ' ']
        
        if seat_col_index[0] <= left_aisle[0]:
            aisle = left_aisle[0]
        else:
            aisle = right_aisle[0]
    
    else:
        aisle = ' '
        
        
    return aisle
        

def show_boarding(df, airplane):
    
    for row in df.index:
        this_passenger = Passenger(pID=df.loc[row, 'pID'], seat=df.loc[row, 'seat'])
        this_passenger.get_info(df.loc[row, 'age'], df.loc[row, 'group'], df.loc[row, 'group_size'], df.loc[row, 'has_travelled'], df.loc[row, 'has_preexisting_condition'])
        x = df.loc[row, 'offset_x']
        y = df.loc[row, 'offset_y']
        method = df.loc[row, 'offset_method']
    
        Boarding_Count_Msg = "Airplane Capacity: {0}%\nBoarding Passenger {1} out of {2}\n".format(round(100*len(df)/airplane.total_seats, 1), row, len(df))
        Passenger_Info_Msg = "Assigned Seat: {0}\nAge: {1}\nHas Pre-Existing Condition: {2}\nGroup Size: {3}\nOffset x: {4}, y: {5}, method: {6}\n\n    ".format(this_passenger.assigned_seat, this_passenger.age, this_passenger.has_preexisting_condition, this_passenger.group_size, x, y, method)    
        Status_Msg = Boarding_Count_Msg + Passenger_Info_Msg
        
        seat = this_passenger.assigned_seat
        aisle = aisle_select(airplane, seat)
        
        seat_row = int(seat[:-1])
        seat_col = seat[-1]
        
        for row in airplane.cabin.index:
            if row == seat_row:
                # do the last aisle position
                airplane.cabin.iloc[row-airplane.start_row, aisle] = '|P|'
                
                # show passenger reaching final row
                sys.stdout.write(Status_Msg)
                airplane.cabin.to_csv(sys.stdout)
                time.sleep(0.05)
                os.system("clear")
    
                # reset to aisle and put passenger in seat
                airplane.cabin.iloc[row-airplane.start_row, aisle] = '| |'
                airplane.cabin.loc[row, seat_col] = 'P'
                
                # show with passenger in seat
                sys.stdout.write(Status_Msg)
                airplane.cabin.to_csv(sys.stdout)
                os.system("clear")
                break
                
            elif row%4 == 0:
                
                airplane.cabin.iloc[row-airplane.start_row, aisle] = '|P|'
            
                # View Plane in console every time
                sys.stdout.write(Status_Msg)
                airplane.cabin.to_csv(sys.stdout)
                time.sleep(0.01)
                os.system("clear")
        
                # reset to aisle symbol
                airplane.cabin.iloc[row-airplane.start_row, aisle] = '| |'
            else:
                pass
            
    sys.stdout.write(Status_Msg)
    airplane.cabin.to_csv(sys.stdout)


        
  
    
    
LOCAL_RESULTS_DIR = os.path.join(LOCAL_REPO_DIR, "results")
fn = os.path.join(LOCAL_RESULTS_DIR, "Airbus_380/run_003.csv")
airplane_model = os.path.basename(os.path.dirname(fn))


my_plane = Airplane(airplane_model)
my_plane.create_cabin(1)




passenger_df = pd.read_csv(fn, dtype=object)
try:
    passenger_df = passenger_df.drop(['Unnamed: 0'], axis=1)
except:
    pass      

#-------------------------------
# my attempt at animation
#-------------------------------
    
show_boarding(passenger_df, my_plane)
time.sleep(10)



