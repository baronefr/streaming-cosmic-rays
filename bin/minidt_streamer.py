#!/usr/bin/env python3

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 2202 / Barone Nagaro Ninni Valentini
#
#  This is a producer of Kafka messages, which polls data
#  from a local minidt dataset. This scripts implements
#  a parallel data reader to preload the next file of
#  the dataset, to keep the buffer always online.
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 10 jun 2022
#  Open Access licence
#--------------------------------------------------------

from kafka import KafkaProducer

import json
import time
import random
import numpy as np

from threading import *


producer_rate = 1100       # Hz
preload_margin = 500000
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092',]
TOPIC='cosmo-stream'
file_template = "./data/mapd-minidt-stream/data_0000{:02d}.txt"


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
producer = KafkaProducer(bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS, linger_ms=2000, batch_size=1024*1024)  #batch_size
# check doc at  https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html


# init the data pool
dataset = parallel_reader( file_template.format(0) )
dataset.run()
cdata, clen = dataset.records, dataset.length


# producer
print(f'\nstart producer at rate {producer_rate} Hz\n')
idx, current_data = 0, 0
while 1:
    
    tic = time.perf_counter()
    if(idx == clen - preload_margin):
        dataset = parallel_reader( file_template.format(current_data+1) )
        dataset.start()
    
    #print(cdata[idx])  # debug only
    
    ## if you like the JSON style...
    #msg = {
    #    'HEAD': cdata[idx][0],
    #    'FPGA': cdata[idx][1],
    #    'TDC_CHANNEL': cdata[idx][2],
    #    'ORBIT_CNT': cdata[idx][3],
    #    'BX_COUNTER': cdata[idx][4],
    #    'TDC_MEAS' : cdata[idx][5]
    #}
    #lst = tuple(int(xx) for xx in cdata[idx])
    #print(json.dumps(lst))
    #producer.send(TOPIC, json.dumps(lst).encode('utf-8'))
    
    producer.send(TOPIC, cdata[idx].encode('utf-8'))
    #producer.flush()  # no if you aggregate into batches!

    idx += 1
    if idx == clen:
        print('swap to new records file')
        cdata, clen = dataset.records, dataset.length
        current_data += 1
        idx = 0
    
    tic_toc = time.perf_counter() - tic
    time.sleep( max(0, 1/producer_rate - tic_toc) )