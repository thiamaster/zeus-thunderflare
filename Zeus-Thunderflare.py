#!/usr/bin/python

import glob
import os.path
from google.cloud import storage
from google.cloud.gapic.videointelligence.v1beta1 import enums
from google.cloud.gapic.videointelligence.v1beta1 import (
	video_intelligence_service_client)
from os import listdir
from os.path import isfile, join
import argparse
import sys
import time

def convertMillis(millis):
	seconds=(millis/1000)%60
	minutes=(millis/(1000*60))%60
	hours=(millis/(1000*60*60))%24
	return [hours, minutes, seconds]


filePath = '/home/gpca/Desktop/Zeus/Cloudspot'
flarePath = '/home/gpca/Desktop/Zeus/Thunderflare'
projectId = 'causal-fort-176621'
bucketName = 'zeus_thunderflare'

video_client = (video_intelligence_service_client.
	VideoIntelligenceServiceClient())
features = [enums.Feature.LABEL_DETECTION]



#files = [f for f in listdir(filePath) if isfile(join(filePath, f))]
videoList = glob.glob(filePath+"/*.mp4")


client = storage.Client()
bucket = client.get_bucket(bucketName)

for video in videoList:
	blob = bucket.blob(os.path.basename(video))
	videoFile = open(video)
	print('\n Enviando arquivo '+os.path.basename(video)+' ...');
	blob.upload_from_file(videoFile)
	operation = video_client.annotate_video("gs://"+bucketName+"/"+os.path.basename(video), features)
	print('\n Aguarde! Processando video '+os.path.basename(video)+' ...')
	while not operation.done():
		sys.stdout.write('.')
		sys.stdout.flush()
		time.sleep(20)
	print('\n Pronto!')
	results = operation.result().annotation_results[0]
	responseFile = open(flarePath+"/"+os.path.basename(video)+".txt", 'w+');
	for label in results.label_annotations:
		
		responseFile.write('\n Label: {}'.format(label.description))
		responseFile.write('\n Quando: \n')
		for l, location in enumerate(label.locations):
			responseFile.write('\t{}: {} ate {} \n'.format(
				l,
				location.segment.start_time_offset,
				location.segment.end_time_offset))
	responseFile.close()

