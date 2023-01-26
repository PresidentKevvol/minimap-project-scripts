import numpy as np
import redis
import json

rds = None

def setup_redis_client(redis_host, redis_pw, port=6379):
    global rds
    rds = redis.Redis(host=redis_host, port=port, db=0, password=redis_pw)

def get_all_beacon_readings():
    global rds
    
    # get all the stored beacon names
    beacons_names = rds.sscan('BeaconNames', count=rds.scard('BeaconNames'))[1]
    beacons_names = [b.decode("utf-8") for b in beacons_names]
    
    # read/collect all the beacon's readings to this program
    all_current_readings = {}
    for name in beacons_names:
        all_current_readings[name] = [json.loads(j) for j in rds.lrange('BeaconRecord-' + name, 0, 99)]
    
    return all_current_readings

def extract_readings_stats(all_current_readings, missing_fill=-101):
    # extract all BSSID's from all data
    all_bssids = {}
    for name in all_current_readings:
        beacon_readings = all_current_readings[name]
        # for each reading data point
        for datapt in beacon_readings:
            for ap in datapt['Points']:
                # record all the existing BSSID and store in hashmap
                if ap['BSSID'] not in all_bssids:
                    all_bssids[ap['BSSID']] = ap['SSID']
    
    # take the keys list and from it establish the ordering of the aps
    # for use in the matrices and vecotrs
    matrix_indices = list(all_bssids.keys())
    
    covariant_matrices = {}
    mean_vectors = {}

    # generate the covariant matrices and mean vectors for the mahalanobis distance
    for name in all_current_readings:
        beacon_readings = all_current_readings[name]
        # the table to contain the data
        data_tableu = np.zeros((len(matrix_indices), len(beacon_readings))) + missing_fill
    
        for i in range(len(beacon_readings)):
            datapt = beacon_readings[i]
            for ap in datapt['Points']:
                ind = matrix_indices.index(ap['BSSID'])
                data_tableu[ind, i] = ap['RSSI']
        # remember bias = True in covariance!
        # otherwise the function divides by N-1 instead of N
        cov = np.cov(data_tableu, bias=True)
        # mean vector of the readings
        mean = np.mean(data_tableu, axis=1)
        covariant_matrices[name] = cov
        mean_vectors[name] = mean
        
    return covariant_matrices, mean_vectors