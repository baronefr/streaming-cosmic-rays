#!/usr/bin/env python3

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This is a producer of FAKE Kafka messages, just
#  to debug the dashboard (ver 0.0)
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 10 jun 2022
#--------------------------------------------------------

from kafka import KafkaProducer

import json
import time
import random
import numpy as np

from threading import *


producer_period = 2
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092',]
TOPIC='cosmo-results'


# Kafka producer object
producer = KafkaProducer(bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS)


# producer
print(f'\nstart FAKE producer at period {producer_period} s\n')

while 1:
    
    tic = time.perf_counter()
    
    # faking numbers
    cleansed_per_chamber = np.random.randint(10, high=30, size=4)
    tot_processed_hits = np.sum(cleansed_per_chamber) + np.random.randint(40, high=100)
    active_tdc_counts = np.random.randint(3, high=10, size=(64,4))
    active_tdc_orbit = np.random.randint(60, high=100, size=(100,4))
    active_tdc_with_scint = np.random.randint(10, high=30, size=(64,4))
    driftimes_ch = np.random.random(size=(100,4))

    fake_data = {
        'tot_hits':     tot_processed_hits.tolist(),
        'cleansed':     cleansed_per_chamber.tolist(),
        'active_tdc':   active_tdc_counts.T.tolist(),
        'active_orbit': active_tdc_orbit.T.tolist(),
        'active_scint': active_tdc_with_scint.T.tolist(),
        'driftimes':    driftimes_ch.T.tolist()
    }
    
    producer.send(TOPIC, json.dumps(fake_data).encode('utf-8'))
    #producer.flush()  # let Kafka manage this (linger & batchsize)
    
    tic_toc = time.perf_counter() - tic
    time.sleep( max(0, producer_period - tic_toc) )