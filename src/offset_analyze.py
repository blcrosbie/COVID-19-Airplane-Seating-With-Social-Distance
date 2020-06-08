# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

from assign_seats import SeatPassenger
from block_seats import SocialDistance
from find_seats import find_next_seat


def calculate_max_accommodation(airplane, offsets, view_charts):
    # get the maximum amount of seats that the airplane can accommodate with proper spacing
    max_accommodation = {}
    
    for i in range(1, len(offsets)):
        sd_offset = offsets[i]
        dont_try_hard = airplane.total_seats
        assign_success = 0
        
        if view_charts:
            print("Calculating Max Accommodation for Offset: {}".format(sd_offset))
        
        
        while dont_try_hard > 0 and airplane.next_seat is not None:
            dont_try_hard -= 1
            
            before_assignment = airplane.next_seat
            blocked_list = SocialDistance(airplane, sd_offset)
            SeatPassenger(airplane, blocked_list)
            find_next_seat(airplane)
            
            if airplane.next_seat != before_assignment:
                assign_success += 1 
                
            else:
                # print(dont_try_hard)
                airplane.next_seat = None
                
                
        
        update_key = 'offset_' + str(i)
        max_accommodation.update({update_key: assign_success})
        
        # to visualize the plane with seated passengers
        if view_charts:
            print("Max Accommodation Results: {}".format(sd_offset))
            print("\tTotal Seats: {}".format(airplane.total_seats))
            print("\tCapacity: {}%".format(round(100*assign_success/airplane.total_seats,1)))
            print("\tPassengers Accommodated: {}".format(assign_success))
            print("\tBuffer Seats: {}\n".format(airplane.total_seats - assign_success))           
            
            airplane.view_plane(pretty=True, details=False)
            print("\n")
            
        
        airplane.deplane()
        
    return max_accommodation
        
                

def get_buffer_ratio(no_offset_count, offset_count, buffer_count):
    fraction = offset_count / (offset_count + buffer_count)
    inverse = 1/fraction
    ratio_to_1 = inverse - 1
    ratio = round(ratio_to_1, 3)
    
    return ratio



def calculate_buffer_ratio(airplane, offsets, offset_max_seats, view_charts):
    # now run a cycle through seats from all open rows to total seats to find the last seat count
    # where each offset is useful

    options_df_col = list(offset_max_seats.keys())
    options_df_col.append('no_offset')
    options_df_col.append('accommodated_passengers')
    options_df_col.append('seats_reserved_for_SD')

    # Initialize the DataFrame
    options_df = pd.DataFrame(columns=options_df_col)

    # initialize save_info
    total_seats = airplane.total_seats
    save_info = {}

    # this is the index for save info dataframe
    tests = 0

    # skip over default in index 0
    for i in range(1, len(offsets)):
        update_key = 'offset_' + str(i)

        offset_max_count = offset_max_seats[update_key]
        save_info.update({'accommodated_passengers': 0, 'seats_reserved_for_SD':0})

        # need to run another for loop to build the factor based on capacity of plane
        for s in range(0, total_seats+1):

            if s <= offset_max_count:
                seats_with_offset = offset_max_count
                no_offset_seats = 0
        
            else:
                factor = 1 - ((s-offset_max_count)/(total_seats-offset_max_count))
                seats_with_offset = int(factor*offset_max_count)
                no_offset_seats = s - seats_with_offset 
                
            buffer_count = total_seats - seats_with_offset - no_offset_seats
            accommodated_passengers = seats_with_offset + no_offset_seats

            # update info for the factor and passenger count on current "offset_i"
            save_info.update({update_key: seats_with_offset})
            save_info.update({'no_offset': no_offset_seats})
            save_info.update({'accommodated_passengers': accommodated_passengers})
            save_info.update({'seats_reserved_for_SD': buffer_count})
            save_info.update({'capacity': round(100*s/total_seats, 2)})


            for j in range(1, len(offsets)):

                # skip the current my_key and the default
                next_ndx = (i+j)%len(offsets)

                if next_ndx != 0:
                    next_key = 'offset_' + str((i+j)%len(offsets))

                    # for now fill with 0's
                    next_factor = 0
                    save_info.update({next_key: next_factor})


            save_info_df = pd.DataFrame(save_info, index=[tests])
            tests+=1
            options_df = pd.concat([options_df, save_info_df], sort=True, axis=0)

            
    buffer_dict = {}
    if view_charts:
        capacity_dict = {}
    
    # find offset ratio for buffer seats
    for i in range(1, len(offsets)):
        o_key = 'offset_' + str(i)
        # observe_df = options_df[options_df[o_key] <= options_df['accommodated_passengers']]
        # observe_df = observe_df[observe_df[o_key] > 0]

        observe_df = options_df[options_df[o_key] > 0]
        observe_df = observe_df.sort_values(['capacity'], ascending=True)
        chart_df = observe_df.reset_index(drop=True)
         
        this_buffer = 'buffer_' + str(i)
        # Buffer calculations
        chart_df[this_buffer] = chart_df[['no_offset', o_key, 'seats_reserved_for_SD']].apply(lambda x: get_buffer_ratio(*x), axis=1)
                 
        # slope_my_offset = round((max(chart_df[o_key]) - min(chart_df[o_key]))/len(chart_df), 3)
        # slope_reserve = round((max(chart_df['seats_reserved_for_SD']) - min(chart_df['seats_reserved_for_SD']))/len(chart_df),3)  
        
        # offset_seats = offset_max_count - 1
        # reserve = chart_df[chart_df[o_key] == offset_seats]
        # print(reserve)
        
        # offset2buffer_ratio = round(slope_reserve/slope_my_offset,3)
        offset2buffer_ratio = max(chart_df[this_buffer])
        max_buffer = max(chart_df[this_buffer])
        # min_buffer = min(chart_df[this_buffer])
        avg_buffer = round(chart_df[this_buffer].mean(),3)
        
        max_buffer_ratio = '1:' + str(max_buffer) 
        buffer_ratio = '1:' +str(avg_buffer)
        max_buffer_key = 'max_buffer_' + o_key
        buffer_dict[o_key] = buffer_ratio
        buffer_dict[max_buffer_key] = max_buffer_ratio
        
        if view_charts:
            x = list(chart_df['capacity'])
            y = list(chart_df[o_key])
            capacity_dict.update({o_key: {'capacity': x, 'accommodation_count': y}})  
        
        
    if view_charts:
        for i in range(1, len(offsets)):
            o_key = 'offset_' + str(i)
            x = capacity_dict[o_key]['capacity']
            y = capacity_dict[o_key]['accommodation_count']            
            plt.plot(x, y, label=o_key)
            
        plt.xlabel("Airplane capactity %")
        plt.ylabel("Accommodated passengers with Social Distancing")
        plt.legend(capacity_dict.keys())
        plt.title("Accommodation per Capacity")
        
    
    return buffer_dict


# Assign order to offset dictionary based on which method maximizes spacing (min value for max_accommodation):
def prioritize_dictionary_on_attribute(dictionary, attribute, depth=1, ascending=True):
    # pass in a dictionary of depth 1 or 2
    # specify the attribute you want to prioritize
    # ascending default to true, set False if you want to search for maxes first
    # depth = 1 means all key,vals are in the same, level, depth = 2 is closer to a json object
    
    new_order_key = 'order'
    prev_check = None 
    
    for o in range(0, len(dictionary)):
        check_key = None

        for key, val in dictionary.items():
            
            # find the val based on specified attribute
            if depth == 1:
                print("OOPS DIDNT DO THIS YET")
                break
                if key == attribute:
                    this_val = dictionary[attribute]
            
            elif depth == 2:
                this_val = int(val[attribute])
                this_key = key
            
            else:
                print("too deep, need more recursion maybe")
                break

            
            # initializing check value, if ascending check is min, if descending check is max
            if check_key is None:
                check_val = this_val
                check_key = key
            
            # previous check will show the last (min/max) to set the next order
            if prev_check is None:
                prev_check = -1 if ascending else this_val
                
            if ascending:
                if this_val <= check_val and this_val >= prev_check:
                    if new_order_key not in list(dictionary[this_key].keys()):
                        check_val = this_val
                        check_key = key
                    
            else:
                if this_val >= check_val and this_val <= prev_check:
                    if new_order_key not in list(dictionary[this_key].keys()):
                        check_val = this_val
                        check_key = key

        # set order
        if depth == 1:
            dictionary[new_order_key] = o
        elif depth == 2:
            dictionary[check_key][new_order_key] = o
        else:
            print("too deep!")
            
        # this will store the last min/max to bound the next order checks
        prev_check = check_val
    
    return 


def AnalyzeSocialDistance(airplane, offsets, no_offset, order_on, view_charts=False):
    # this function returns a dictionary to show the max total each social distance offset may accommodate
    # along with the ratio of buffer seats required to satisfy the spacing intervals
    offsets_analyzed = {'no_offset': {'offset': no_offset, 'max_accommodation': airplane.total_seats, 'buffer_ratio': '1:0'}}
    
    # find max accommodation per offset 
    max_accommodation = calculate_max_accommodation(airplane, offsets, view_charts)
    
    # find buffer seat ratios
    buffer_ratios = calculate_buffer_ratio(airplane, offsets, max_accommodation, view_charts)
       
    # combine details into analyzed dictionary 
    for i in range(1, len(offsets)):
        offkey = 'offset_' + str(i)   
        max_buffer_key = 'max_buffer_' + offkey
        
        offsets_analyzed.update({offkey: {'offset': offsets[i],
                                          'max_accommodation': max_accommodation[offkey],
                                          'buffer_ratio': buffer_ratios[offkey],
                                          'max_buffer_ratio': buffer_ratios[max_buffer_key]
                                          }})
    
    # Add an order detail to offsets
    if order_on == 'max_accommodation':
        depth = 2  # theres dictionary depth recursion caclulator, already wrote this in DataWrangler, but for now
        ascending = True
        prioritize_dictionary_on_attribute(offsets_analyzed, order_on, depth, ascending)
    else:
        print("Need to add method of prioritization on {}".format(order_on))
    
    
    return offsets_analyzed  
    



            
      



