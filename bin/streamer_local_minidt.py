#!/usr/bin/env python3

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This is a producer of Kafka messages, which buffers
#  data from a local minidt dataset. 
#  This scripts also implements a parallel data reader
#  to preload the next file of the dataset.
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 17 jun 2022
#--------------------------------------------------------

import sys
import configparser
from configparser import ExtendedInterpolation

import json
import time
import random
import numpy as np

from kafka import KafkaProducer

from threading import *


# parsing settings
if len(sys.argv) > 1:
    print('-- environment mode, target:', sys.argv[1])
    
    # read config file
    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(sys.argv[1])
    try:
        PRODUCER_RATE = int( config['DATA-STREAM']['DSTR_PRODUCER_RATE'] )
        KAFKA_BOOTSTRAP_SERVER = str( config['KAFKA']['KAFKA_BOOTSTRAP'] ).replace('\'', '')
        TOPIC = str(config['KAFKA']['TOPIC_STR']).replace('\'', '')
        LINGER = int( config['DATA-STREAM']['DSTR_LINGER'] )
        BATCH_SIZE = int( config['DATA-STREAM']['DSTR_BATCHSZ'] )
    except Exception as e:
        print('ERROR: config file error')
        print(e)
        sys.exit(1)
else:
    print('-- standalone mode')
    PRODUCER_RATE = 1100
    KAFKA_BOOTSTRAP_SERVER = 'localhost:9092'
    TOPIC = 'cosmo-stream'
    LINGER = 2000
    BATCH_SIZE = 1024

print('[info] configuration:')
print(f' server {KAFKA_BOOTSTRAP_SERVER} on topic {TOPIC}')
print(f' data rate {PRODUCER_RATE} Hz')
print(f' linger = {LINGER} ms,  batch = {BATCH_SIZE} ')

#########################################################

file_template = "./data/mapd-minidt-stream/data_0000{:02d}.txt"
preload_margin = 500000

class parallel_reader(Thread):
    def __init__(self, fname):
        super(parallel_reader, self).__init__()
        self.fname = fname
    
    def run(self):
        print('> pre-loading', self.fname)
        tic = time.perf_counter()
        
        # store in memory lines of the file (except first)
        with open(self.fname) as f:
            self.records = f.readlines()
            self.records = self.records[1:]
        
        #  alternative: store in numpy arrays (not convenient!)
        #self.records = np.loadtxt(self.fname, skiprows=1, delimiter=',')
        
        self.length = len(self.records)
        toc = time.perf_counter()
        print(' -- buffered', self.length, f'samples in {round(toc-tic,2)}s')
        return 0


# Kafka producer object
producer = KafkaProducer(bootstrap_servers = KAFKA_BOOTSTRAP_SERVER,
                         linger_ms=LINGER, batch_size=BATCH_SIZE*1024)
# check doc at  https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html


# init the data pool
dataset = parallel_reader( file_template.format(0) )
dataset.run()
cdata, clen = dataset.records, dataset.length


# producer
print(f'\nstart producer at rate {PRODUCER_RATE} Hz\n')
idx, current_data = 0, 0
while 1:
    
    tic = time.perf_counter()
    if(idx == clen - preload_margin):
        dataset = parallel_reader( file_template.format(current_data+1) )
        dataset.start()
    
    #print(cdata[idx])  # debug only
    
    ##     if you like the JSON style...
    #msg = {
    #    'HEAD': cdata[idx][0],
    #    'FPGA': cdata[idx][1],
    #    'TDC_CHANNEL': cdata[idx][2],
    #    'ORBIT_CNT': cdata[idx][3],
    #    'BX_COUNTER': cdata[idx][4],
    #    'TDC_MEAS' : cdata[idx][5]
    #}
    #lst = tuple(int(xx) for xx in cdata[idx])
    #producer.send(TOPIC, json.dumps(lst).encode('utf-8'))
    
    producer.send(TOPIC, cdata[idx].strip().encode('utf-8'))
    #producer.flush()  # no if you aggregate into batches!

    idx += 1
    if idx == clen:
        print('swap to new records file')
        cdata, clen = dataset.records, dataset.length
        current_data += 1
        idx = 0
    
    tic_toc = time.perf_counter() - tic
    time.sleep( max(0, 1/PRODUCER_RATE - tic_toc) )