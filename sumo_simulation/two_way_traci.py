# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 11:23:54 2022

@author: xin
"""


import os, sys
import traci
import numpy as np
import csv


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
# =============================================================================
# change the path based on your configuration
# =============================================================================
sumoBinary = r"/home/simu5g/sumo-1.11.0/bin/sumo" # updating the SUMO path
sumoCmd = [sumoBinary, "-c", "autobahn.sumocfg"]

    

def vehicle_information():
    step = 0
    a = 0
    index = 0
    x_coordinate = np.array([])
    y_coordinate = np.array([])
    
    
    while step < 1000: 
       location_list=[]
       traci.simulationStep()
       for vehicleId in traci.vehicle.getIDList():
           x, y = traci.vehicle.getPosition(vehicleId)           
           x_coordinate = round(x,2)
           y_coordinate = round(y,2)
           location_list.append([vehicleId,x_coordinate,y_coordinate]) # saving three items in each line
           index +=1       
       if 100<step<=500: # sampling time duration
           filename_locations='data/location_for_timestep'+str(step) # each csv-file for each step
           f = open('%s.csv'%filename_locations,'w',newline='')
           writer = csv.writer(f)
           for i in location_list:
               writer.writerow(i)
           f.close()
       
       vehicle_number = len(traci.vehicle.getIDList())
       print('step',step,"Total number of vehicles: " + str(vehicle_number))
       print()
       a += 1             
       step += 1
       index = 0
       x_coordinate = np.array([])
       y_coordinate = np.array([])

def main():    
    traci.start(sumoCmd)
    vehicle_information()
    traci.close()

       
if __name__ == "__main__":
    main()
    

