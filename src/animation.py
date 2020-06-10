# -*- coding: utf-8 -*-

import os, sys

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from matplotlib import colors


LOCAL_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_DIR = os.path.dirname(LOCAL_SRC_DIR)
LOCAL_BASE_DIR = os.path.dirname(LOCAL_REPO_DIR)

LOCAL_RESULTS_DIR = os.path.join(LOCAL_REPO_DIR, "results")
fn = os.path.join(LOCAL_RESULTS_DIR, "Airbus_380/run_003.csv")

passenger_df = pd.read_csv(fn)
passenger_df = passenger_df.drop(['Unnamed: 0'], axis=1)



#Define discrete color map  (blue for empty, gold for passenger)
cmap = colors.ListedColormap(["darkslateblue", 'gold'])
bounds=[-1,0,300]
norm = colors.BoundaryNorm(bounds, cmap.N)

img_list = ac.img_list

for i in range(2):
    img_list.append(img_list[-1])

im=[]

#Create figure and add subplot
fig=plt.figure(figsize=(8,13))
ax=fig.add_subplot(111)
ax.set_xlabel("Rear",fontsize=20)
ax.set_title("Passenger entry here",fontsize=20)


#Use imshow on the images and create a nice looking plot
for i in range(len(img_list)):
    image=ax.imshow(img_list[i],animated=True,cmap=cmap,norm=norm)
    ax.set_xticks(sci.arange(-0.5,7.5,1))
    ax.set_yticks(sci.arange(-0.5,23.5,1))
    ax.grid(color="k",linestyle="-",linewidth=2.5)  
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    im.append([image])
    
    
#Play and store the animation
mov=anim.ArtistAnimation(fig,im,interval=180)
mov.save("Airplane_Boarding_{0}.mp4".format(method))