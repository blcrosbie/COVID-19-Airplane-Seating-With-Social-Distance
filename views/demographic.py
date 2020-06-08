# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

def passenger_statistics(df_passengers):
    # age distribution
    age_range = max(df_passengers['age']) - min(df_passengers['age'])

    # NOTE: children under the age of 2 may sit on laps
    age_plot = plt.hist(list(df_passengers['age']), density=False, bins=age_range)
    plt.xlabel('age')
    plt.ylabel('count') 
    plt.title('Age Distribution')
    plt.show(age_plot)
    
    
    # show group sizes
    max_group_size = max(df_passengers['group_size'])
    group_size_plot = plt.hist(list(df_passengers['group_size']), density=False, bins=max_group_size)
    plt.xlabel('group size')
    # plt.set_xlim([1, max_group_size])
    plt.xticks(list(range(1, max_group_size+1)))
    plt.ylabel('count')
    plt.title('Group Size Distribtion')
    plt.show(group_size_plot)
    
    print("Passenegers with Travel History: {}"          .format(df_passengers[df_passengers['has_travelled'] == True].count()['has_travelled']))
    
    print("Passengers with Preexisting Conditions: {}"          .format(df_passengers[df_passengers['has_preexisting_condition'] == True].                  count()['has_preexisting_condition']))    
    


