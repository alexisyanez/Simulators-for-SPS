# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 00:19:25 2023

@author: CSUST
"""

from Vehicle import Vehicle
import numpy as np
import pandas as pd
from RBG import RBG
from Channel import Channel
from Obstacles import Obstacles
import sys
import time
import argparse
import copy

parser = argparse.ArgumentParser(description=\
                                 '--r: running time,\
                                 \n--td: target distance for beacon message,\
                                 \n--sst: start sampling time,\
                                 \n--itv: transmission interval of beacon messages,\
                                 \n--rcl: RC lower bound,\
                                 \n--rch: RC higher bound,\
                                 \n--cr: fixed candidate ratio (0.1,0.2,0.3,0.4,0.5,0.6),\
                                 \n--mu: NR numerology for SCS (0,1,2 for FR1),\
                                 \n--obs: Inclusion of obstacles in the scenario\
                                 \n--nr: Activate New Radio adding re-evaluation procedure \
                                 \n--ds: density scenario\
                                 \n--sd: Step Duration in ms\
                                 \n--aw: Awarenesness Window in ms')

                                
parser.add_argument('--cr', type=float, default=0.2) #we remove the list L2 for NR as is shown in: https://ieeexplore.ieee.org/document/9579000
parser.add_argument('--r', type=int, default=5000) #6000 #10000) ##original 300000) # este parametro corresponde al tiempo que se desa correr las simulaciones debe ser menor que time_period_all
parser.add_argument('--td', type=float, default=200)
parser.add_argument('--sst', type=int, default=0)
parser.add_argument('--itv', type=int, default=5)
parser.add_argument('--rcl', type=int, default=5)
parser.add_argument('--rch', type=int, default=15)
parser.add_argument('--mu', type=int, default=0)

parser.add_argument('--obs', action='store_true')
parser.add_argument('--no-obs', dest='obs', action='store_false') # Activar o desactivar 

parser.add_argument('--nr', action='store_true')
parser.add_argument('--no-nr', dest='obs', action='store_false')

parser.set_defaults(feature=False)

parser.add_argument('--ds', type=int, default=4)
parser.add_argument('--sd', type=int, default=10)
parser.add_argument('--aw', type=int, default=100)

def genearate_vehicles(num_vehicle, num_slot, vehicle_location, transmit_power, p_resource_keeping,RCrange,target_distance,obs,obstacles,nr):
    vehicle_instance_list = []
    for i in range(num_vehicle):
        vehicle_instance_list.append(Vehicle(i,vehicle_location[i],transmit_power,p_resource_keeping,RCrange,target_distance,obs,obstacles,nr))
    return vehicle_instance_list    
        
def generate_RBGs(num_slot,num_subch):
    RBG_intance_list = []
    for i in range(num_slot):
        RBG_intance_each_slot = []
        for j in range(num_subch):
            RBG_intance_each_slot.append(RBG(i,j))
        RBG_intance_list.append(RBG_intance_each_slot)
    return RBG_intance_list
  
 
def main(time_period,target_distance,start_sampling_time,interval,RC_low,RC_high,RSRP_ratio_beacon,mu,obs,ds,nr,aw,sd):
    # parameter settings
    transmit_power = 200 #this value is in mW units equivalent to 23 dBm
    time_period_all = 30000 #300000 #6000 #300000 #200 #50000 #50000 #10000 #original 300000 Total time in miliseconds considering all dataset
    # it seems this value comes from the total duration over all section data
    # each section from the dataset has 200 steps, and each step has 0.05 s, so each section has 10 seconds. 
    num_subch = 4
    
    RCrange = [RC_low,RC_high]
        
    p_resource_keeping = 0 #0.4
    sensing_window = 1100
    
    sinr_th = 2**(2.1602)-1 # From Table II on the SPS paper should be 2.76 dB
    k0 = 10**(-4.38)
    alpha = 3.68
            
    num_RBs_per_RBG = 10
    SCS = 15*(np.power(2,mu))*(10**3)#np.power(15,mu)*(10**3)

    Time_slot=np.float_power(2,-mu)
    T3=1+np.float_power(2,mu+1)*Time_slot
    rev_counter=0
    
    num_sc_per_RB = 12
    bandwidth_per_RB = SCS * num_sc_per_RB
    bandwidth_per_RBG = bandwidth_per_RB * num_RBs_per_RBG
    noise_perhz_dBm = -174
    noise_perhz_mW = 10**(noise_perhz_dBm/10)
    noise = noise_perhz_mW * (bandwidth_per_RBG)

    pdr_ratio_list=[]
    transmission_condition=[]
    add_loss_ratio_to_beacon_list = []

    ALL_pdr_ratio_list_individual=[[],[]]
    VRU_pdr_ratio_list_individual=[[],[]]
    emp_VAP_ratio_list_individual=[[],[]]

    VRUpdr_ratio_list=[]   # For VRU calculation
    VRUtransmission_condition=[]  # For VRU calculation
    VRUadd_loss_ratio_to_beacon_list = []  # For VRU calculation

    # Initializing buildings in urban scenario
    obstacles = {}
    obstacles_bool = obs
    if obstacles_bool==True:
        obstacles = Obstacles()

    nr_bool = nr
    ds_index = ds

    if nr_bool: RSRP_ratio_beacon = 1

    RSRP_th = -110
    candidate_ratio_list=[0.1,0.2,0.3,0.4,0.5]  

    filename='mh_fixcr_'+'_num_rep'+str(time_period)+'_interval'+str(interval)+\
        '_startpot'+str(start_sampling_time)+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
    '''
    f = open('%s.log'%(filename), 'a')
    sys.stdout = f
    '''
    
    # =============================================================================
    # import road traffic
    # =============================================================================
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    for section_index in range(0,int(time_period_all/1000)): #200)): # Oiriginal 10000
        if ds_index == 2:
            location_file_name = 'traffic_data_ped_v2/type_v2sumo_ped_vehicle_location_sec_' + str(section_index) # From pedestrian manhatan scenario + str(section_index) 
        elif ds_index == 3:
            location_file_name = 'traffic_data_ped_v3/type_v3sumo_ped_vehicle_location_sec_' + str(section_index) # From pedestrian manhatan scenario + str(section_index) 
        elif ds_index == 4:
            location_file_name = 'traffic_data_ped_v4/type_v4sumo_ped_vehicle_location_sec_' + str(section_index) # From pedestrian manhatan scenario + str(section_index) 
        elif ds_index == 5:
            location_file_name = 'traffic_data_ped_v5/type_v5sumo_ped_vehicle_location_sec_' + str(section_index) # From pedestrian manhatan scenario + str(section_index) 
        elif ds_index == 6:            
            location_file_name = 'traffic_data_ped_v6/type_v6sumo_ped_vehicle_location_sec_' + str(section_index) # From pedestrian manhatan scenario + str(section_index) 
       

        #location_file_name = 'sumo_vehicle_location_'+ str(section_index)
        #location_file_name = 'v2manhattan_location_s20_'+ str(section_index)
        #location_file_name = 'sumo_vehicle_location' # + str(section_index)
        #location_file_name = 'type_v4sumo_ped_vehicle_location_sec_' + str(section_index) # From pedestrian manhatan scenario + str(section_index) 
        
        print('section_index',section_index)
        if section_index==0:
            LocationDataAll=np.array(pd.read_csv("C:/Users/adani/OneDrive/Documentos/GitHub/SimulatorSPS/OOP_for_SPS/%s.csv"%(location_file_name),header=None)).tolist()
            #LocationDataAll=np.array(pd.read_csv("/home/ayanez/Simulators-for-SPS/OOP_for_SPS/traffic_data_ped_v2/%s.csv"%(location_file_name),header=None)).tolist()
        else:    
            LocationDataAll=np.vstack((LocationDataAll,np.array(pd.read_csv("C:/Users/adani/OneDrive/Documentos/GitHub/SimulatorSPS/OOP_for_SPS/%s.csv"%(location_file_name),header=None)).tolist()))
            #LocationDataAll=np.vstack((LocationDataAll,np.array(pd.read_csv("/home/ayanez/Simulators-for-SPS/OOP_for_SPS/traffic_data_ped_v2/%s.csv"%(location_file_name),header=None)).tolist()))

    # location_file_name = 'sumo_vehicle_location'
    # LocationDataAll=np.array(pd.read_csv("C:/Users/adani/OneDrive/Documentos/GitHub/SimulatorSPS/OOP_for_SPS/traffic_data/%s.csv"%(location_file_name),header=None)).tolist()
    
    #print('content', LocationDataAll)

    #print('length of content', len(LocationDataAll))

    ObserveVehicles = [[] for i in range(0,time_period)]
    num_vehicle=int(len(LocationDataAll)/time_period_all)
    print('VehicleNum',num_vehicle)
    for i in range(0,time_period):
        ObserveVehicles[i]=LocationDataAll[int(i*num_vehicle):int((i+1)*num_vehicle)]  
    vehicle_location_ini = ObserveVehicles[0]

   #print(ObserveVehicles[1])

    print('time_period',time_period)
    print('start_sampling_time',start_sampling_time)
    print('RSRP_ratio_beacon',RSRP_ratio_beacon)
    print('p_resource_keeping',p_resource_keeping)
    print('sensing_window',sensing_window)
    print('num_vehicle',num_vehicle)
    print('num_subch', num_subch)
    print('interval', interval)
    print('transmit_power',transmit_power)
    print('target_distance',target_distance)
    print('NR numerology',mu)
    print('Obstacles',obstacles_bool)
    print('Density_scenario',ds_index)

    # =============================================================================
    # initialization
    # =============================================================================
    vehicle_list = genearate_vehicles(num_vehicle,time_period,vehicle_location_ini,\
                                      transmit_power,p_resource_keeping,RCrange,target_distance,obstacles_bool,obstacles,nr_bool)
    #print(vehicle_list[0])

    RBG_list = generate_RBGs(time_period,num_subch)
    channel = Channel(num_subch, interval)
    # generate messages
    for i in range(num_vehicle):
        vehicle_list[i].message_list_ini(time_period)
        vehicle_list[i].generate_beacon(interval, 200, time_period)
            
    # =============================================================================
    # run till time_period    
    # =============================================================================
    eval_time = aw/sd    
    for t in range(0,time_period):
        if t%1000==0: print('t=',t)
        for i in range(num_vehicle):
            # update location and sensing_window
            vehicle_list[i].update_location(ObserveVehicles[t][i])
            
            if t==0:
                # initialize resource selection
                vehicle_list[i].initial_RBGs_selection(RBG_list,interval) 
                vehicle_list[i].generate_neighbour_set(vehicle_list)
                
            else:
                vehicle_list[i].update_reselection_counter(t,interval,RCrange)
    
        # update sensing window, selection window and resource selection
        for i in range(num_vehicle):
            #####################
            # Sensing procedure #
            #####################
            
            vehicle_list[i].generate_RBGlist_1100ms(t, RBG_list, sensing_window)
                      
            vehicle_list[i].update_sensing_result(t, vehicle_list, RBG_list, sensing_window)
            ins=0
            if t>0:
            ############################
            # (Re-)Selection procedure #
            ############################
                if vehicle_list[i].message_list[t]!=None:
                    #vehicle_list[i].generate_neighbour_set(vehicle_list) # Removing this line we are not updating in every step the list of neigbhours
                    vehicle_list[i].generate_RBGs_in_selection_window(t,RBG_list,interval)
                   
                    # Here is the selection for the beacon slot
                    vehicle_list[i].RBG_selection_beacon(RSRP_ratio_beacon, RBG_list, t, channel)
                    vehicle_list[i].lastSel_t = t
                    ins=0
            
            #######################
            # Re-evaluation check #
            #######################        
            if t>0 and t<vehicle_list[i].v_RBG.timeslot - T3 and t > vehicle_list[i].lastSel_t and ins==0 and nr_bool:
                
                #vehicle_list[i].generate_RBGlist_1100ms(t, RBG_list, sensing_window)
                #vehicle_list[i].update_sensing_result(t, vehicle_list, RBG_list, sensing_window)
                        
                vehicles_copy=copy.copy(vehicle_list[i].neighbour_list)
                #vehicles_copy.remove(vehicle_list[i])
                timeslot = vehicle_list[i].v_RBG.timeslot
                subchannel = vehicle_list[i].v_RBG.subchannel
                busy=0
                for vehicle in vehicles_copy:
                        #print(vehicle.v_RBG.subchannel,subchannel,vehicle.v_RBG.timeslot,timeslot)
                    if vehicle.v_RBG.subchannel == subchannel and vehicle.v_RBG.timeslot == timeslot:
                            busy=1
                if busy == 1: # if the slot is bussy the vehicle trigger again the re-selection procedure
                    vehicle_list[i].reselection_counter = 0
                    vehicle_list[i].v_RBG.timeslot = 0                    
                    #vehicle_list[i].generate_RBGs_in_selection_window(t,RBG_list,interval)                   
                    # Here is the selection for the beacon slot
                    #vehicle_list[i].RBG_selection_beacon(RSRP_ratio_beacon, RBG_list, t, channel)
                    #vehicle_list[i].lastSel_t = t
                ins=1
            ########################
            # Message transmission #
            ########################           
            if t>0 and t == vehicle_list[i].v_RBG.timeslot:
                # statistic pdr for beacon messages

                #print('vehicle= '+str(i) + ' tiempo= '+str(t))
                vehicle_list[i].statistic_for_reception(vehicle_list,sinr_th,noise,t,start_sampling_time)
            # Here should be the re-evaluation and pre-emption fase        
        if t>start_sampling_time and t%eval_time==0:
            sum_tran = 0
            sum_rec = 0     

            sum_VRUtran = 0 # collecting metrics for VRU 
            sum_VRUrec = 0 #  collecting metrics for VRU
            
            sum_additional_loss_to_beacons = 0

            individual_PDR = []
            VRUindividual_PDR = []
            individual_emp_VAP = []
            for vehicle in vehicle_list:
                vehicle.num_tran_em = 0
                vehicle.num_rec_em = 0

                sum_tran = 0
                sum_rec = 0 
                VRU_rec = 0
                
                sum_tran += vehicle.num_tran
                sum_rec += vehicle.num_rec
                
                

                #sum_VRUtran += vehicle.VRUnum_tran
                #sum_VRUrec += vehicle.VRUnum_rec

                if sum_tran>0: 
                    individual_PDR.append(sum_rec/sum_tran) #np.average(vehicle.transmission_statistic))
                    
                    if vehicle.type == 1:
                        VRUindividual_PDR.append(sum_rec/sum_tran)

                    if vehicle.type == 2:
                        VRU_neig_dup = set(vehicle.VRUreception)
                        VRU_rec = len(VRU_neig_dup)
                        len_VRU_N =len(vehicle.VRUneighbour_list)

                        if len_VRU_N > 0:
                            individual_emp_VAP.append(VRU_rec/len_VRU_N)
                            #print(VRU_rec/len_VRU_N)
                    #print(np.average(vehicle.transmission_statistic))
                
        
                vehicle.num_tran = 0
                vehicle.num_rec = 0
                vehicle.VRUreception = []
                vehicle_list[i].generate_neighbour_set(vehicle_list)


                #vehicle.VRUnum_tran = 0
                #vehicle.VRUnum_rec = 0        
                #vehicle.transmission_statistic = []
                
                
            #add_loss_ratio_to_beacon_list.append(sum_additional_loss_to_beacons/(sum_additional_loss_to_beacons+sum_rec))
            #pdr_ratio_list.append(sum_rec/sum_tran)
            #transmission_condition.append([sum_rec,sum_tran])

            ALL_pdr_ratio_list_individual[0].append(np.average(individual_PDR))
            ALL_pdr_ratio_list_individual[1].append(np.std(individual_PDR))

            VRU_pdr_ratio_list_individual[0].append(np.average(VRUindividual_PDR))
            VRU_pdr_ratio_list_individual[1].append(np.std(VRUindividual_PDR))

            #print(emp_VAP_ratio_list_individual)
        
            emp_VAP_ratio_list_individual[0].append(np.average(individual_emp_VAP))
            emp_VAP_ratio_list_individual[1].append(np.std(individual_emp_VAP))

            #VRUadd_loss_ratio_to_beacon_list.append(sum_additional_loss_to_beacons/(sum_additional_loss_to_beacons+sum_VRUrec))
            #VRUpdr_ratio_list.append(sum_VRUrec/sum_VRUtran)
            #VRUtransmission_condition.append([sum_VRUrec,sum_VRUtran])

            
    
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('time_period',time_period)
    print('start_sampling_time',start_sampling_time)
    print('RSRP_ratio_beacon',RSRP_ratio_beacon)
    print('p_resource_keeping',p_resource_keeping)
    print('sensing_window',sensing_window)
    print('num_vehicle',num_vehicle)
    print('num_subch', num_subch)
    print('interval', interval)
    print('transmit_power',transmit_power)
    print('target_distance',target_distance)
    print('NR_numerology',mu)
    print('transmission_condition',transmission_condition)
    print('Obstacles',obstacles_bool)
    print('Density_scenario',ds_index)
    
    #print('PDR:',pdr_ratio_list)
    #print('Overall PDR:',list(map(sum, zip(*transmission_condition)))[0]/list(map(sum, zip(*transmission_condition)))[1])
    
    #print('Empiric_VAP_transmission_condition',VRUtransmission_condition) # Printing VRU related performance evaluation
    #print('Empiric_VAP_PDR:',VRUpdr_ratio_list)

    #print('Empiric_VAP_PDR:',VRUpdr_ratio_list)

    # CAR PDR Individual
    # VRU PDR Individual
    # Empiric VAP just from CARs

    print('ALL_PDR_avg_std: ',ALL_pdr_ratio_list_individual)
    print('VRU_PDR_avg_std: ',VRU_pdr_ratio_list_individual)
    print('emp_VAP_avg_std: ',emp_VAP_ratio_list_individual)

    #print('*******************')

    print('\n')         

    
if __name__ == '__main__':
    args = parser.parse_args()   # 解析所有的命令行传入变量
    main(args.r,args.td,args.sst,args.itv,args.rcl,args.rch,args.cr,args.mu,args.obs,args.ds,args.nr,args.aw,args.sd)



 
#x = [[0,0,1],[0,0,2],[0,0,1],[0,0,1],[0,0,2],[0,0,1],[0,0,2]]
#result = [i.pop(2) for i in x]
#print(result.count(1))
