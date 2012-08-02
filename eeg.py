#!/usr/bin/env python
# encoding: utf-8
"""
eeg.py

Created by Michael Sobczak on 2012-08-02.
Copyright (c) 2012 Michael Sobczak. All rights reserved.
"""

from socket import *
import json
from threading import Thread, Event
import Queue
import time
from sys import stderr

HOST = '127.0.0.1'
PORT = 13854
ADDR = (HOST, PORT)
headset_conf_dict = {'enableRawOutput':False, 'format':'Json'}
HEADSET_JSON_SEPARATOR = '\r'
NULL_DATA = {'poorSignalLevel':200}

# this is the data that the ThinkGearConnector sends out
brain_parameters = (
		lowAlpha, highAlpha, lowBeta, highBeta, 
		lowGamma, highGamma, delta, theta, 
		poorSignalLevel, meditation, attention) = (
		'lowAlpha', 'highAlpha', 'lowBeta', 'highBeta', 
		'lowGamma', 'highGamma', 'delta', 'theta', 
		'poorSignalLevel', 'meditation', 'attention')
		
# these are the two general categories of brainwave data
parameter_categories = (eSense, eegPower) = ('eSense', 'eegPower')	


def _extract_tuple(data_dict):
	"""Returns a tuple of the values extracted from a message dictionary."""
	return (
		data_dict[eegPower][lowAlpha],
		data_dict[eegPower][highAlpha],
		data_dict[eegPower][lowBeta],
		data_dict[eegPower][highBeta],
		data_dict[eegPower][lowGamma],
		data_dict[eegPower][highGamma],
		data_dict[eegPower][delta],
		data_dict[eegPower][theta],
		data_dict[poorSignalLevel],
		data_dict[eSense][meditation],
		data_dict[eSense][attention])


def _create_and_connect_socket(host, port):
	cs = socket(AF_INET, SOCK_STREAM)
	cs.connect((host, port))
	cs.send(json.dumps(headset_conf_dict))
	return cs


def _event_stream(shutdown_func, host, port):
	soc = _create_and_connect_socket(host,port)
	
	while not shutdown_func():
		temp_json = ''
		cur_char = soc.recv(1)
		while cur_char != HEADSET_JSON_SEPARATOR:
			temp_json += cur_char
			cur_char = soc.recv(1)
		data = None
		try:
			data = json.loads(temp_json)
		except ValueError:
			pass#stderr.write('Error while decoding JSON object, discarding data')
		if data:
			if eSense in data and eegPower in data:
				yield dict(zip(brain_parameters, _extract_tuple(data)))
			else:
				yield data
	cs.close()
	
	
def _processEEGStream(queue, shutdown_flag, connected_flag, host, port):
	eegGen = _event_stream(lambda: shutdown_flag.isSet(), host, port)
	
	next_msg = lambda: eegGen.next()
	
	# loop and discard data until connection is made
	while not connected_flag.isSet():
		msg = next_msg()
		if not msg == NULL_DATA:
			connected_flag.set()
			
	# now getting real data
	for data in eegGen:
		#print 'putting %s in queue' % str(data)
		queue.put(data)
		
	connected_flag.clear()


class MindStream(object):
	
	def __init__(self, host=HOST, port=PORT):
		self.host = host
		self.port = port
		# thread communication stuff
		self.shutdown_flag = Event()
		self.is_connected_flag = Event()
		self.queue = Queue.Queue()
		self.stream_thread = Thread(target=_processEEGStream, args=(self.queue, self.shutdown_flag, self.is_connected_flag, self.host, self.port))
		self.stream_thread.start()
		
	def isConnected(self):
		return self.is_connected_flag.isSet()
		
	def shutdown(self):
		self.shutdown_flag.set()
		
	def getData(self):
		stuff = []
		while not self.queue.empty():
			item = self.queue.get()
			if item:
				stuff.append(item)
		return stuff if len(stuff) > 0 else None
		
	def __del__(self):
		self.shutdown()
		self.stream_thread.join()
		

def runTest():
	ms = MindStream()
	print 'attempting to connect to headset'
	start_connecting_time = time.time()
	while not ms.isConnected():
		print 'connecting...'
		time.sleep(3)
	connect_time = time.time() - start_connecting_time
	print 'connected!'
	print 'connection made in %.2f seconds' % connect_time
	start_time = time.time()
	while time.time() - start_time < 25:
		print 'getting data'
		print ms.getData()
		print 'sleeping for a sec'
		time.sleep(5)
	print 'done'
	
if __name__ == '__main__':
	runTest()
			

