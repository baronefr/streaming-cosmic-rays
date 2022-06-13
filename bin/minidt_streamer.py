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


producer_rate = 10         # Hz
preload_margin = 500000
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092',]
TOPIC='cosmo-stream'
file_template = "./data/mapd-minidt-stream/data_0000{:02d}.txt"
# rewind ?


class parallel_reader(Thread):
    def __init__(self, fname):
        super(parallel_reader, self).__init__()
        self.fname = fname
    
    def run(self):
        print('> pre-loading', self.fname)
        tic = time.perf_counter()
        self.records = np.loadtxt(self.fname, skiprows=1, delimiter=',')
        self.length = len(self.records)
        toc = time.perf_counter()
        print(' -- buffered', self.length, f'samples in {round(toc-tic,2)}s')
        return 0


# Kafka producer object
producer = KafkaProducer(bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS)

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
    
    print(np.sum(cdata[idx]))
    #msg = {
    #    'name': random.choice(first_names),
    #    'surname': random.choice(last_names),
    #    'amount': '{:.2f}'.format(random.random()*1000),
    #    'delta_t': '{:.2f}'.format(random.random()*10),
    #    'flag': random.choices([0,1], weights=[0.8, 0.2])[0]
    #}
    #producer.send(TOPIC, json.dumps(msg).encode('utf-8'))
    #producer.flush()

    idx += 1
    if idx == clen:
        print('swap to new records file')
        cdata, clen = dataset.records, dataset.length
        current_data += 1
        idx = 0
    
    tic_toc = time.perf_counter() - tic
    time.sleep( max(0, 1/producer_rate - tic_toc) )