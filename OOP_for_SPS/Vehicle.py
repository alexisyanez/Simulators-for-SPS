# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 18:36:52 2023

@author: CSUST
"""

import math
import numpy as np
from message import Beacon
import copy
import random
from list_process import transfer_2Dlist_to_1Dlist
from RBG import RGBs_set
from Obstacles import Obstacles



# =============================================================================
#     v_RBG is the observed suhchannel, 
#     the function "sense_single_RBG" is to get the sum power received by the object vehicle.
#     if the observed slot is used by object vehicle, return "False"
# =============================================================================


class Vehicle():
    
    def __init__(self, index, location, power, p_resource_keeping,RCrange,target_distance,obstacles_bool,obstacles,nr,cl,min_cl,max_cl,msd_cl,cluster,max_dis_cl):
        self.index = index
        self.type = location[3]
        #print(self.type) just to dbug the type
        self.location = location
        self.speed = location[4]
        self.angle = location[5]
        self.v_RBG = None
        self.v_em_RBGs_set = []
        self.v_em_RBGs_multiple = []
        self.choose_RBGs_multiple = []
        self.message_list = None
        self.power = power
        self.sensepower_1100ms = {}
        self.sensingpower_current_slot = {}
        self.RBGlist_1100ms = []
        self.RBGlist_tillnow = []
        self.RBGlist_in_slot = []
        self.prepower_in_selection_window = {}
        self.best_RBG_list_beacon = []
        self.neighbour_list = []
        self.Rxneighbour_list = [] #[number of succesfully received, number of failed received]
        self.VRUneighbour_list = []  #adding the list of neighbout for VRU
        self.VRUreception = []  # To check message reception 
        self.transmission_statistic = []
        self.VRUtransmission_statistic = [] # Collecting the statistic for VRU neigbohrs
        self.target_distance = target_distance
        self.reselection_counter = random.randint(RCrange[0], RCrange[1])
        self.RBGs_in_selection_window = []
        self.num_tran = 0
        self.num_rec = 0
        self.VRUnum_tran = 0 # Special metrics for VRU
        self.VRUnum_rec = 0 # Special metrics for VRU
        self.p_resource_keeping = p_resource_keeping
        self.RSRP_th = -110.35564074964655
        self.max_upper_bound = 0
        self.n_sample = 0        
        self.RSRPth_selected=[]
        self.RSRPth_index_selected = []
        self.candidate_ratio_selected = []
        self.candidate_ratio_index_selected = []
        self.features_list = []
        self.features_decision_mapping = {}
        self.k=0
        self.candidate_chosen_list = []
        self.bm_reception_record = {}
        self.v_RBG_last_one=None
        self.obstacles_bool=obstacles_bool
        self.obstacles=obstacles # Getting obstacles from main class
        self.lastSel_t=float('inf')
        self.nr_bool = nr
        self.cl_bool = cl
        self.cl_role = 0 # 0-> VRU Active-Standalone o VRU-ACTIVE-CLUSTER-LEADER , 1 -> VRU-PASSIVE
        self.cl_id = 0 # Cluster ID
        self.my_cluster = [] # member in the cluster
        self.min_cl_member = min_cl # Maximum number of members
        self.max_cl_member = max_cl # Minimum number of members 
        self.max_speed_dif = msd_cl
        self.max_dsitance_cl = max_dis_cl
        self.all_clusters = cluster
  

        
        
    def initial_statistic_pdr_multi_dis(self,distance_list):
        for i in distance_list:
            self.statistic_pdr_multi_dis[i]=0
            self.statistic_all_packet_multi_dis[i]=0
        
        
    def initial_RBGs_selection(self,RBG_list,interval):
        self.v_RBG = random.choice(transfer_2Dlist_to_1Dlist(RBG_list[:interval]))

    def initial_RBGs_selection_em(self,RBG_list):
        #self.v_em_RBG = RGBs_set(0,[0,1])
        self.v_em_RBGs_set = [RBG_list[0][0],RBG_list[0][1]]
        self.v_em_RBGs_multiple = [RGBs_set(0,[0,1])]
        self.choose_RBGs_multiple=[[RBG_list[0][0],RBG_list[0][1]]]
        
    def generate_RBGlist_in_slot(self,current_time, RBG_list):
        self.RBGlist_in_slot = RBG_list[current_time]
    
    def update_reselection_counter(self,current_time,interval,RCrange):
        if current_time % (int(interval)) == 0:
            self.reselection_counter -= 1
            if self.reselection_counter < 0:
                self.reselection_counter = random.randint(RCrange[0],RCrange[1])
    
    def generate_RBGlist_1100ms(self,current_time, RBG_list, sensing_window):
        if current_time>=sensing_window:
            self.RBGlist_1100ms = RBG_list[current_time-sensing_window:current_time]
        else:
            self.RBGlist_1100ms = RBG_list[:current_time]
    


    def generate_RBGs_in_selection_window(self,current_time,RBG_list,window_size):
        self.RBGs_in_selection_window = transfer_2Dlist_to_1Dlist(RBG_list[current_time:current_time+window_size])

        
    def update_power(self,newpower):
        self.power = newpower
        
    def update_location(self,newlocation):
        self.location = newlocation
        
    def update_RBG(self,newv_RBG):
        self.v_RBG = newv_RBG
    
    def message_list_ini(self,time_period):
        self.message_list = [None]*time_period
        
    def generate_beacon(self,interval,mdelay,time_period):
        for i in range(0,int(time_period/interval)):
            if int(i*interval) >= time_period:
                break
            mID=str(self.index)+'-'+ str(self.type) +'-'+str(i)
            ## print('The ID and type for the beacon is: '+mID)
            self.message_list[int(i*interval)] = Beacon(0, mdelay, int(i*interval), None, interval,mID)


    def genearate_vehicles(num_vehicle, num_slot, vehicle_location, transmit_power):
        vehicle_instance_list = []
        for i in range(num_vehicle):
            vehicle_instance_list.append(Vehicle(i,vehicle_location[i],transmit_power))
        return vehicle_instance_list    


    def distance(self,v2):
        v1_location = self.location
        v2_location = v2.location
        distance = math.sqrt(math.pow((v2_location[0] - v1_location[0]), 2) + math.pow((v2_location[1] - v1_location[1]), 2))
        return distance
    
    def receive_power(self,vehicle):        
        k0 = 10**(-4.38)
        if self.distance(vehicle) != 0:
            # Substract losses from obstacles in the receive power
            if self.obstacles_bool==True:
                obs_loss = self.obstacles.getObsaclesLossess(self.location,vehicle.location)
                Total_loss_dB = np.log10(k0*vehicle.power*self.distance(vehicle)**(-3.68))*10 - obs_loss
                Total_loss_mw = 10**(Total_loss_dB/10)
                if Total_loss_mw>=0: 
                    return Total_loss_mw
                else: 
                    return 0
            else:   
                return k0*vehicle.power*self.distance(vehicle)**(-3.68)
        else:
            #if self.obstacles_bool==True:
            #    obs_loss = self.obstacles.getObsaclesLossess(self.location,vehicle.location)
            #    return k0*vehicle.power*0.1**(-3.68) - obs_loss
            #else:   
            return k0*vehicle.power*0.1**(-3.68)
            
    
    # check if the slot can be measured by the object vehicle, due to the half duplex
    def observation_boolean(self, v_RBG):
        timeslot = v_RBG.timeslot
        if self.cl_role==0:
            if timeslot == self.v_RBG.timeslot:
                return False
            else:
                return True
        else: return False

    def sense_single_RBG(self, v_RBG, vehicles):
        sum_power = 0
        vehicles_copy=copy.copy(vehicles)
        vehicles_copy.remove(self)
        timeslot = v_RBG.timeslot
        subchannel = v_RBG.subchannel
        if self.observation_boolean(v_RBG) == True:
            for vehicle in vehicles_copy:
                #print(vehicle.v_RBG.subchannel,subchannel,vehicle.v_RBG.timeslot,timeslot)
                if vehicle.cl_role==0:
                    try:
                        if vehicle.v_RBG.subchannel == subchannel and vehicle.v_RBG.timeslot == timeslot: # and vehicle.cl_role==0:
                            sum_power += self.receive_power(vehicle)
                    except AttributeError:
                        print("-Waring: vehicle.v_RBG is None")
                        #print("-vehicle is: ",vehicle.type)
        else:
            sum_power = float("inf")
        return sum_power
 
        
    def sensing_single_slot(self, time, vehicles, RBG_list):
        self.sensingpower_current_slot = {}
        self.generate_RBGlist_in_slot(time, RBG_list)
        for RB in self.RBGlist_in_slot:
             self.sensingpower_current_slot[RB]=self.sense_single_RBG(RB, vehicles)

    def remove_outofdate_sensing(self,current_time, RBG_list, sensing_window):
        outofdate_RBGs = RBG_list[current_time-sensing_window-1]
        if current_time>sensing_window:
            for RB in outofdate_RBGs:
                self.sensepower_1100ms.pop(RB)
                
            
    def add_uptodate_sensing(self,current_time, vehicles, RBG_list):
        self.sensing_single_slot(current_time-1, vehicles, RBG_list)
        self.sensepower_1100ms.update(self.sensingpower_current_slot)
    
    def update_sensing_result(self, current_time, vehicles, RBG_list, sensing_window):
        self.remove_outofdate_sensing(current_time, RBG_list,sensing_window)
        self.add_uptodate_sensing(current_time, vehicles, RBG_list)     
                
    def evaluate_average_power(self,observed_RBG, channel):
        ####################### Important #########################################
        ## As shown in https://ieeexplore.ieee.org/document/9579000, there are no more average evaluation over 5G-NR
        ###########################################################################
        sum_power_list = []
        RBGlist_1100ms_temp=transfer_2Dlist_to_1Dlist(self.RBGlist_1100ms)
        for RB in RBGlist_1100ms_temp:
            if self.nr_bool:
                if RB.subchannel == observed_RBG.subchannel: # and (observed_RBG.timeslot - RB.timeslot)%(channel.interval) == 0:  
                    sum_power_list.append(self.sensepower_1100ms[RB])
            else:
                if RB.subchannel == observed_RBG.subchannel and (observed_RBG.timeslot - RB.timeslot)%(channel.interval) == 0:  
                    sum_power_list.append(self.sensepower_1100ms[RB])
        if self.nr_bool:
            self.prepower_in_selection_window[observed_RBG] = sum_power_list[0] # np.average(sum_power_list)
        else:
            self.prepower_in_selection_window[observed_RBG] = np.average(sum_power_list)

    def evaluate_power_in_selection_window(self, channel):
        self.prepower_in_selection_window={}
        for RB in self.RBGs_in_selection_window:
            self.evaluate_average_power(RB, channel)
                    
    def find_accessible_RBGs_for_beacon(self, RSRP_ratio_beacon):
        temp = copy.copy(self.prepower_in_selection_window)
        self.best_RBG_list_beacon = []
        num_picked_RBGs = int(RSRP_ratio_beacon * len(temp))
        
        for i in range(num_picked_RBGs):
            min_power_RBG = min(temp.items(), key=lambda x: x[1])[0]
            self.best_RBG_list_beacon.append(min_power_RBG)
            temp.pop(min_power_RBG)
            
    def RBG_selection_beacon(self, RSRP_ratio_beacon, RBG_list, current_time, channel):
        #observed_RBG_in_selection_window = RBG_list[current_time:current_time+channel.interval]
        self.v_RBG_last_one = self.v_RBG # for reward calculation in em generation, in case new rbg is selected but not yet statistic
        p = random.random()
        if p>self.p_resource_keeping and self.reselection_counter == 0:
            self.evaluate_power_in_selection_window(channel)
            self.find_accessible_RBGs_for_beacon(RSRP_ratio_beacon)
            self.v_RBG = random.choice(self.best_RBG_list_beacon)
            #print(self.v_RBG)
        else:
            self.v_RBG = RBG_list[self.v_RBG.timeslot+channel.interval][self.v_RBG.subchannel]
    
    def generate_neighbour_set(self,vehicles,t):
        self.neighbour_list = []
        self.VRUneighbour_list = []
        self.Rxneighbour_list = []
        #self.VRUreception = []
        vehicles_copy = copy.copy(vehicles)
        vehicles_copy.remove(self)

        for vehicle in vehicles_copy:
            if self.distance(vehicle)<=self.target_distance:
                self.neighbour_list.append(vehicle)
                self.Rxneighbour_list.append([0,0])
                if vehicle.type == 1: # and self.type == 2:  #Type 1 corresponds to VRU, type 2 to Cars
                    self.VRUneighbour_list.append(vehicle)
                    #self.VRUreception.append(0)
        
        # Chequing if there are a leader in the VRU neigbhour and if it's cluster not exceed the maximum member
        if self.cl_bool:
            #print("Ive pass the first conditional, so clustering is acctivated")
            if not self.my_cluster: # Checkeando que no tenga asignado un cluster
                #print("Ive pass the second conditional, so I dont have a cluster assigned")
                if self.type == 1: # Checking the user is VRU
                    #print("Ive pass third conditional, so Im a VRU")
                    alone_VRUs = []
                    #print('the length of the neighbout list is:'+str(len(self.VRUneighbour_list)))
                    for VRU in self.VRUneighbour_list:
                        if VRU.cl_role == 0 and len(VRU.my_cluster) < self.max_cl_member and VRU.my_cluster and (self.vel_diff(VRU.speed,VRU.angle) <= self.max_speed_dif) and self.distance(VRU)<=self.max_dsitance_cl: # Looking for a leader with a cluster created
                            #print("I found a cluster so Im joining it")
                            VRU.my_cluster.append(self) #joining a cluster 
                            self.cl_role=1
                            self.cl_id=VRU.cl_id
                        if  VRU.cl_role == 0 and not VRU.my_cluster: # Looking for active stand-alone VRU
                            #print("I found neigbors alone")
                            alone_VRUs.append(VRU)
                    if len(alone_VRUs) > self.min_cl_member: # Creating a cluster
                        self.cl_role=0
                        self.id=self.all_clusters.getClusterID(t)
                        #print("I passed the fourth conditional so im geting cearting a cluster and getting an ID")
                        self.my_cluster=alone_VRUs
                        for cl_member in alone_VRUs:
                            cl_member.cl_role=1 #changing the role for the cluster members                  
            else:
                for CM in self.my_cluster:
                    if CM.cl_role == 0 and self.cl_role==1:
                        if self.distance(CM)>self.max_dsitance_cl or (self.vel_diff(CM.speed,CM.angle) > self.max_speed_dif): # Leaving cluster if im out of range or exceed the speed diference
                            #print("Im leaving the cluster beacuse Im far away to the CH")
                            for CM2 in self.my_cluster:
                                CM2.my_cluster.remove(self) #removing from all cluster lists
                            self.cl_role=0
                            print("leaving cluster and changing role to active stand-alone")

                if 0 < len(self.my_cluster) < self.min_cl_member and self.cl_role == 0: #Deleting a Cluster if is a Leader
                    #print("since I am the CH im deleting the cluster because we dont have enough memebers")
                    self.all_clusters.deleteClusterID(self.cl_id,t)

                    for CM in self.my_cluster:
                        CM.my_cluster = []
                        CM.cl_id = 0
                        CM.cl_role= 0
                    
                    self.my_cluster = []
                    self.cl_id = 0
                    print("Deleting cluster being a Leader")

    def sum_interference_power(self,receive_vehicle,vehicles):
        sum_interference = 0
        vehicles_copy=copy.copy(vehicles)
        vehicles_copy.remove(self)
        vehicles_copy.remove(receive_vehicle)

        if receive_vehicle.cl_role==0:
            try:
                if self.v_RBG.timeslot == receive_vehicle.v_RBG.timeslot:
                    sum_interference = float("inf")
                else:
                    for vehicle in vehicles_copy:
                        if vehicle.cl_role==0:
                            try:
                                if vehicle.v_RBG.timeslot == self.v_RBG.timeslot and vehicle.v_RBG.subchannel == self.v_RBG.subchannel: # and vehicle.cl_role==0: #only considering leader as transmitter
                                    sum_interference += receive_vehicle.receive_power(vehicle)
                            except AttributeError:
                                print("-In Interference Power Warning: vehicle.v_RBG is None")
                                #print("-In Interference Power vehicle is: ",vehicle.type)
            except AttributeError:
                print("-In Interference Power Warning: received vehicle.v_RBG is None")
                                #print("-In Interference Power vehicle is: ",vehicle.type)
        return sum_interference

    
    def sum_interference_power_em(self,receive_vehicle,vehicles,RB):
        sum_interference = 0
        vehicles_copy=copy.copy(vehicles)
        vehicles_copy.remove(self)
        vehicles_copy.remove(receive_vehicle)
        
        # check half-duplex errors
        if RB.timeslot == receive_vehicle.v_RBG.timeslot:
            sum_interference = float("inf")
            return sum_interference
        # if no half-duplex errors, accumulate the interference power
        for vehicle in vehicles_copy:                
            if vehicle.v_RBG.timeslot == RB.timeslot and vehicle.v_RBG.subchannel == RB.subchannel and vehicle.cl_role==0: #only considering leader as transmitter
                sum_interference += receive_vehicle.receive_power(vehicle)                    
        return sum_interference    

    def sinr_calculate(self,receive_vehicle,vehicles,noise):
        useful_power = receive_vehicle.receive_power(self)
        interference_power = self.sum_interference_power(receive_vehicle,vehicles)
        sinr = useful_power/(interference_power+noise)
        return sinr
 
    def check_message_reception(self,receive_vehicle,vehicles,sinr_th,noise):
        sinr = self.sinr_calculate(receive_vehicle,vehicles,noise)
        if sinr >= sinr_th:
            reception = True
        else:
            reception = False
        return reception

        
    def statistic_for_reception(self,vehicles,sinr_th,noise,current_time,start_sampling_time):
        reception = 0     
        num_packet = len(self.neighbour_list)
        if current_time>start_sampling_time:
            self.num_tran += len(self.neighbour_list)
        #print('t=',current_time,self.index,'neighbour_list',self.neighbour_list)
        for vehicle in self.neighbour_list:
            
            # shorten vehicle.bm_reception_record
            len_record = len(vehicle.bm_reception_record)
            popkeys = list(vehicle.bm_reception_record.keys())[:min(len_record-400,0)]
            [vehicle.bm_reception_record.pop(k) for k in popkeys]    

            if self.check_message_reception(vehicle,vehicles,sinr_th,noise) == True:
                reception += 1
                vehicle.bm_reception_record[str([self.index,self.v_RBG.timeslot])]=1
                
                if current_time>start_sampling_time:
                    self.num_rec += 1
                    self.Rxneighbour_list[self.neighbour_list.index(vehicle)][0]=self.Rxneighbour_list[self.neighbour_list.index(vehicle)][0]+1 # Incrementing succefull receptión for each vehicle
                    if self.type == 1 and vehicle.type == 2: #Type=1 is a VRU and Type=2 is a Car
                        if self in vehicle.VRUneighbour_list and self not in vehicle.VRUreception:
                            vehicle.VRUreception.append(self.index)
                            # adding the cluster info to the reception from vehicles
                            if len(self.my_cluster) > 1:
                                for cm in self.my_cluster:
                                    if cm in vehicle.VRUneighbour_list and cm not in vehicle.VRUreception:
                                        vehicle.VRUreception.append(cm.index)


                        #if self in VRU_List:
                        #    VRU_index = VRU_List.index(self)
                        #    vehicle.VRUreception[VRU_index]=1
                    #print("VRU index: ",self.index)
                    #print("VRU List: ",vehicle.VRUneighbour_list)
                    #print("VRU recception List: ",vehicle.VRUreception)


            else:
                vehicle.bm_reception_record[str([self.index,self.v_RBG.timeslot])]=0
                self.Rxneighbour_list[self.neighbour_list.index(vehicle)][1]=self.Rxneighbour_list[self.neighbour_list.index(vehicle)][1]+1 # Incrementing failed receptión for each vehicle

        if num_packet==0:
            self.transmission_statistic.append(None)
        else:
            self.transmission_statistic.append(reception/num_packet)

    def vel_diff(self, speed_head, angle_head): #calculate_velocity_difference_percentage(
        # Convert angles from degrees to radians
        angle_head_rad = math.radians(angle_head)
        angle_follower_rad = math.radians(self.angle)
        
        # Convert polar coordinates to Cartesian coordinates
        v1x = speed_head * math.cos(angle_head_rad)
        v1y = speed_head * math.sin(angle_head_rad)
        v2x = self.speed * math.cos(angle_follower_rad)
        v2y = self.speed * math.sin(angle_follower_rad)
        
        # Calculate the relative velocity components
        vrx = v1x - v2x
        vry = v1y - v2y
        
        # Calculate the magnitude of the relative velocity
        relative_speed = math.sqrt(vrx**2 + vry**2)
        
        # Calculate the percentage difference relative to the cluster head's speed
        percentage_difference = (relative_speed / speed_head) * 100
        
        return percentage_difference
        #repeat the process for VRU neighbours

"""         reception = 0     
        num_packet = len(self.VRUneighbour_list)
        if current_time>start_sampling_time:
            self.VRUnum_tran += len(self.VRUneighbour_list)
        #print('t=',current_time,self.index,'neighbour_list',self.neighbour_list)
            
        for vehicle in self.VRUneighbour_list:
            # shorten vehicle.bm_reception_record
            len_record = len(vehicle.bm_reception_record)
            popkeys = list(vehicle.bm_reception_record.keys())[:min(len_record-400,0)]
            [vehicle.bm_reception_record.pop(k) for k in popkeys]    

            if self.check_message_reception(vehicle,vehicles,sinr_th,noise) == True:
                reception += 1
                vehicle.bm_reception_record[str([self.index,self.v_RBG.timeslot])]=1
                
                if current_time>start_sampling_time:
                    self.VRUnum_rec += 1

                # This is the Empiric VAP
                if self.type == 1 and vehicle.type == 2:
                    VRU_List = vehicle.VRUneighbour_list
                    if self in VRU_List:
                        VRU_index = VRU_List.index(self)
                        vehicle.VRUreception[VRU_index]=1
                    #print("VRU index: ",self.index)
                    #print("VRU List: ",vehicle.VRUneighbour_list)
                    #print("VRU recception List: ",vehicle.VRUreception)
            else:
                vehicle.bm_reception_record[str([self.index,self.v_RBG.timeslot])]=0
        if num_packet==0:
            self.VRUtransmission_statistic.append(None)
        else:
            self.VRUtransmission_statistic.append(reception/num_packet)
        
 """
