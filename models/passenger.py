# -*- coding: utf-8 -*-

class Passenger:
    def __init__(self, pID, seat=None):
        self.pID = pID
        self.assigned_seat = seat
        
    def fill_questionare(self, age, group, has_travelled, has_preexisting_condition):
        # should be straightforward
        self.age = age
        self.group = group
        self.group_size = len(group)        
        self.has_travelled = has_travelled
        self.has_preexisting_condition = has_preexisting_condition  
        
    def get_info(self, age, group, group_size, has_travelled, has_preexisting_condition):
        # should be straightforward
        self.age = age
        self.group = group
        self.group_size = group_size       
        self.has_travelled = has_travelled
        self.has_preexisting_condition = has_preexisting_condition  
        
    def assign_seat(self, seat):
        self.assigned_seat = seat
            
    def check_seat(self):
        print(self.assigned_seat)
#         print(self.group)       

    def check_temperature(self):
        # obviously someone with a temperature should be barred from flying if checked before boarding, but what
        # about during flight, or immediate screening on the ground
        
#        self.temperature_F = random_fever_check()
        print("Current Reading: {}".format(self.temperature_F))
        if self.temperature_F > 99.5:
            print("HAS FEVER")
        else:
            print("OK")
            
    def __del__(self):
        pass
        