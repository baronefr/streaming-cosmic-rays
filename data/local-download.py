#!/usr/bin/env python3

#########################################################
#    local data downloader from cloud veneto            #
#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#--------------------------------------------------------

import boto3
import json

# load from  credentials.hidden  file: do you have yours?
with open('credentials.hidden', 'r') as f:
    data = f.read()
    hidden = json.loads(data)
print('got the credentials!')

# file list @
# https://cloud-areapd.pd.infn.it:5210/swift/v1/AUTH_d2e941ce4b324467b6b3d467a923a9bc/mapd-minidt-stream/

file_range = 80
file_name_template = 'data_0000{:02d}.txt'

s3_client = boto3.client('s3', endpoint_url='https://cloud-areapd.pd.infn.it:5210',
                         aws_access_key_id = hidden['key_id'],
                         aws_secret_access_key = hidden['key'],
                         verify='/home/baronefr/.ssh/CloudVenetoCAs.pem')

for i in range(file_range+1):
    print('downloading', file_name_template.format(i))
    s3_client.download_file('mapd-minidt-stream', file_name_template.format(i), file_name_template.format(i))
    
print('completed')