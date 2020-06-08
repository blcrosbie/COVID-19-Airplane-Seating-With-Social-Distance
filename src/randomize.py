# -*- coding: utf-8 -*-

import pandas as pd
import random
import uuid


###############################################################################
def create_passenger_roster(number_of_passengers, view_stats=False):
    # randomize characteristics
    # 0. Age
    # 1. uuid
    # 2. flying with if not solo (lower chance, people should not be taking family vacations right now)
    # 3. has travelled - history: last 14 days of travel (high chance of travel history if travelling again)
    # 4. has_preexisting_condition (should be extremely low percentage of flyers)

    
    # 0. Age Randomization
    # use simple 35 avg, and stdev of 10
    age_list = []
    for seats in range(0, number_of_passengers):
        age_list.append(int(random.gauss(35,10)))
        
    
    passengers = []
    for age in age_list:
        # 1. assign uuid to age list to make start building passenger list
        passenger_id = uuid.uuid4()
        
        # 2. Probability of group travelling defined in function
        group_size = probability_alone(age)
        this_passenger = {'pID': passenger_id, 'age': age, 'group_size':group_size, 'group': []}
        passengers.append(this_passenger)

    passengers = set_groups(passengers)
    df_passengers = pd.DataFrame(passengers)
    df_passengers = group_passengers(df_passengers)
    
    # Run a Sanity check on the DataFrame Length to Ensure all passengers are still in roster
    try:
        assert len(df_passengers) == number_of_passengers, "DROPPED PASSENGERS"
    except Exception as e:
        print(e)
    
    
    # Lambda fun(ctions)
    # These are simply probability factors for true/false We must decide who needs Social Distancing Offsets
    # In some priority order
    # 3. Travel History
    df_passengers['has_travelled'] = df_passengers['age'].apply(lambda x: find_travel_history(x))
    
    # 4. Preexisting Conditions
    df_passengers['has_preexisting_condition'] = df_passengers['age'].apply(lambda x: preexisting_conditions(x))
    
    
#    if view_stats:
#        passenger_statistics(df_passengers)
    
    return df_passengers


###############################################################################



def find_travel_history(age):
    travel_probability = random.random()
    
    if age < 18 and travel_probability > 0.8:
        return True
    elif age < 25 and travel_probability > 0.4:
        return True
    elif age < 30 and travel_probability > 0.5:
        return True
    elif age < 35 and travel_probability > 0.6:
        return True
    elif age < 45 and travel_probability > 0.7:
        return True
    elif age < 55 and travel_probability > 0.8:
        return True
    elif age < 65 and travel_probability > 0.9:
        return True
    elif age >= 65 and travel_probability > 0.95:
        return True
    else:
        return False
    


def get_correction_counts(psgr_list, max_group_size):
    # this is metadata calculator to help set groups by organizing 
    # how many passengers were given the group size random assignment
    # then this needs to be checked to ensure group sizes make sense in the roster
    
    groups_info = []
    for i in range(1, max_group_size+1):
        count = 0
        for psgr in psgr_list:
            if psgr['group_size'] == i:
                count += 1
        
        unique_count = int(count/i)
        correction = count - i*unique_count
        groups_info.append({'size': i, 'count': count, 'unique_count':unique_count, 'correction':correction})

    return groups_info
                


def group_passengers(df_psgr):
    
    grouped_psgr_df = pd.DataFrame()
    
    # immediately build the grouped psgr df with the size = 1 sub df
    
    grouped_psgr_df = pd.concat([grouped_psgr_df, df_psgr[df_psgr['group_size'] == 1]], axis=0)
    
    # two parts to this grouping method
    # 1: use a main party member, use the group size to seek the next members to add
    # 2: iterate through member list to link each member together
    
    # now that we have group info, we can assign group uuid's together
    # again skip to group size 2 (by starting index at 1)
    max_group_size = max(df_psgr['group_size'])
    
    # iterate through each group size in the total passenger dataframe
    for grp_size in range(2, max_group_size+1):
        
        #filter down the passenger list for only same group size passengers
        sub_psgr_df = df_psgr[df_psgr['group_size']==grp_size]
        
        # this list will provide all indices for passengers of this group size to make groups with
        sub_psgr_index_options_list = list(sub_psgr_df.index)
        
        # Iterate through the index list to build groups
        for i in range(0, len(sub_psgr_index_options_list)):
            
            # the first group member will be the sub_index
            sub_index = sub_psgr_index_options_list[i]
            
            # now check to see if this passenger has not already been assigned a group
            if not sub_psgr_df['group'][sub_index]:
            
                # create a list and fill with other passengers with same group size
                all_group_members = []
                all_group_ndx = []
                
                # add in the first passenger pID
                all_group_ndx.append(sub_index)
                all_group_members.append(sub_psgr_df.loc[sub_index, 'pID'])

                # This For Loop builds the list
                for j in range(1, grp_size):
                    next_index = sub_psgr_index_options_list[i+j]
                    all_group_ndx.append(next_index)
                    all_group_members.append(sub_psgr_df.loc[next_index, 'pID'])
                
                # This For Loops pastes the list in the DataFrame to each member
                for ndx in all_group_ndx:
                    sub_psgr_df['group'][ndx] = all_group_members
                
                # update the main grouped passenger df with this group list info                
                grouped_psgr_df = pd.concat([grouped_psgr_df, sub_psgr_df.loc[all_group_ndx, :]], axis=0)
        
            else:
                pass

    return grouped_psgr_df



def preexisting_conditions(age):
    # https://www.cms.gov/CCIIO/Resources/Forms-Reports-and-Other-Resources/preexisting 
    # " 86% of older Americans have preexisting condition"
    # using Figure 1 chart for Americans at Risk by Age
    condition_probability = random.random()
    
    if age < 18 and condition_probability < 0.05:
        return True
    
    elif age >= 18 and age < 25 and condition_probability < 0.09:
        return True
    
    elif age >= 25 and age < 35 and condition_probability < 0.13:
        return True
    
    elif age >= 35 and age < 45 and condition_probability < 0.21:
        return True
    
    elif age >= 45 and age < 55 and condition_probability < 0.32:
        return True
    
    elif age >= 55 and age < 65 and condition_probability < 0.48:
        return True
    
    elif age >= 65 and condition_probability <= 0.86:
        return True
    
    else:
        return False



def probability_alone(age):
    # 2. grouping should look like 

    # 75%  - 1 (is alone = True)
    # 13%  - 2 (is alone = False)
    # 8%   - 3    "         "
    # 3.5% - 4    "         "
    # 0.4% - 5    "         "
    # 0.1% - 6    "         "
    
    alone_prob = random.random()
    
    if age < 18:
        if alone_prob < 0.9:
            return 2
        elif alone_prob < 0.8:
            return 3
        elif alone_prob < 0.7:
            return 4
        else:
            return 5
    else:
    
    
        if alone_prob < 0.6:
            return 1
        elif alone_prob < 0.75:
            return 2
        elif alone_prob < 0.8:
            return 3
        elif alone_prob < 0.9:
            return 4
        elif alone_prob < 0.925:
            return 5
        elif alone_prob < 0.95:
            return 6
        else:
    #         random_add = int(random.random()*10)
    #         random_large_group = 7 + random_add
    #         return random_large_group
            return 7


def set_groups(passenger_list):
    max_group_size = 7
    groups_info = get_correction_counts(passenger_list, max_group_size)
     
    # now correct the details from random generator to realistic groupings
    # default all corrections to group size 1 for simplicity
    
    for i in range(1, max_group_size):
        # starting from one in index here jumps to 'size == 2', 
        g_info = groups_info[i]
        g_size = g_info['size']
        
        num_corrections = g_info['correction']
        n = 0
        
        while n < num_corrections:
            for psgr in passenger_list:
                if psgr['group_size'] == g_size and n < num_corrections:
                    psgr['group_size'] = 1
                    n += 1
    
    return passenger_list




def travel_contact(df):
    for row in df.index:
        group_size = df['group_size'][row]
        if group_size > 1:
            print("Passenger in a group")
            group = df['group'][row]
            for psgr in group:
                print (psgr)
                print(group_size)
    return df



