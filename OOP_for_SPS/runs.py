import multiprocessing 
import json
import SPS_test
import numpy as np
import tqdm

def wrapper(args):
    # Función auxiliar para llamar a SPS_test.main con los argumentos
    return SPS_test.main(*args)

if __name__ == "__main__":

    time_period = 5200    
    start_sampling_time = 200
    interval = 50
    RC_low = 5
    RC_high = 15
    RSRP_ratio_beacon = 0.2      
    ds = 4
    sd = 1
    td = np.arange(25, 525, 25)
    obs_list = [False, True]
    aw_list = [10, 50, 100, 200, 500]
    nr_list = [False, True]  
    mu_list = [0,1,2]

    param_list = []
    

    for target_distance in td:
        for obs in obs_list:
            for aw in aw_list:
                for nr in nr_list:
                    if nr:
                        #for mu in mu_list:
                        param = [time_period,target_distance,start_sampling_time,interval,RC_low,RC_high,RSRP_ratio_beacon,mu_list[0],obs,ds,nr,aw,sd]
                        param_list.append(param)
                    #else:
                    #    param = [time_period,target_distance,start_sampling_time,interval,RC_low,RC_high,RSRP_ratio_beacon,mu_list[0],obs,ds,nr,aw,sd]
                    #    param_list.append(param)

    #for conf in param:
    
    # Número máximo de procesos (8 para usar 8 CPU)
    num_procesos = 8

    # Crear un grupo de procesos
    with multiprocessing.Pool(processes=num_procesos) as pool:
        #resultados = pool.map(wrapper,param_list)
        resultados = list(tqdm.tqdm(pool.imap_unordered(wrapper,param_list), total=len(param_list)))

    # Ahora 'resultados' contiene los 90 resultados generados en paralelo
    # Puedes procesarlos o combinarlos según lo que necesites

    # Por ejemplo, imprimir los primeros 10 resultados
    print(resultados[:10])

    # Combinar los resultados en un solo diccionario
    diccionario_final = {}
    for resultado in resultados:
        diccionario_final.update(resultado)

    # Exportar como archivo JSON
    with open("Final_results_group1.json", "w") as archivo:
        json.dump(diccionario_final, archivo, indent=4)

    print("Archivo 'Final_results_group1.json' creado exitosamente.")
