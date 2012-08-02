import random
import time
import pygame
from pygame.locals import *
from eeg import MindStream
import collections
import os
import pickle

# constants
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
color_set = (red, green, blue)
text_color = (0, 191, 255)
background_color = (0,0,0)

SCREEN_SIZE = (WIDTH, HEIGHT) = (800, 800)
APP_TITLE = 'Color Trainer'


TRAINING_INTERVAL = 5 # seconds
NUM_ROUNDS = 3
scenes = (CONNECTING, INSTRUCTION) = ('Connecting', 'Instruction')
labels = {red:'Red', green:'Green', blue:'Blue'}
# UI constants
CONNECTING_MESSAGE = 'Connecting to MindWave Headset...'
INSTRUCTION_MESSAGE = 'Think about each color as hard as you can while it\'s displayed on screen'
INSTRUCTION_DISPLAY_TIME = 4 # seconds
# persistence constants
CONFIG_OBJECT_FILENAME = 'user_id.p'
DATA_OUTPUT_DIRECTORY = 'output'
# pygame initialization
random.seed()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
background = pygame.Surface(SCREEN_SIZE)

pygame.display.set_caption(APP_TITLE)
font = pygame.font.Font(None, 32)

mindstream = MindStream()


def render_background():
	background.fill(background_color)
	screen.blit(background, (0,0))


def connecting_update(strt_time):
	msgview = font.render(CONNECTING_MESSAGE, True, text_color)
	screen.blit(msgview, (WIDTH/3.0, HEIGHT/2.1))
	return INSTRUCTION if mindstream.isConnected() else None
	
def instruction_update(strt_time):
	inst_msg = font.render(INSTRUCTION_MESSAGE, True, text_color)
	screen.blit(inst_msg, (WIDTH/7.0, HEIGHT/2.1))
	return 'TRAINING' if time.time() - strt_time > INSTRUCTION_DISPLAY_TIME else None
	
def training_update():
	pass
	
def end_update():
	pass

def tagData(data, label, starting_time):
	if not data:
		return None
	filtered_data = filter(lambda x: len(x.keys()) > 1, data)
	tagged_data = [ dict( [ ('time', time.time() - starting_time), ('label', label) ] + d.items() ) for d in filtered_data ]
	return tagged_data


scene_dict = {
	CONNECTING:connecting_update,
	INSTRUCTION:instruction_update }

# get the config object
print 'performing configuration'
isNewUser = False
if not os.path.exists(CONFIG_OBJECT_FILENAME):
	# get the user
	print 'No existing configuration object found, will create a new one'
	username = raw_input('Please enter a username:')
	cfg_obj = {'name':username, 'id':0}
	pickle.dump(cfg_obj, open(CONFIG_OBJECT_FILENAME, 'wb'))
	isNewUser=True

config_object = pickle.load(open(CONFIG_OBJECT_FILENAME, 'rb'))
print 'configuration loaded, starting program\n'
if isNewUser:
	print 'Hello %s. Welcome to the %s App' % (config_object['name'], APP_TITLE)
else:
	print 'Welcome back %s for session #%d' % (config_object['name'], int(config_object['id'])+1)

print 'initializing training program'
current_scene = CONNECTING
start = time.time()
current_scene_start_time = start
while True:
	render_background()
	next_scene = scene_dict[current_scene](current_scene_start_time)
	pygame.display.flip()
	if next_scene:
		if next_scene == 'TRAINING':
			break
		else:
			current_scene = next_scene
			current_scene_start_time = time.time()

print 'initialization completed'
# now in training mode
training_data = []
print 'starting training'
training_start_time = time.time()
cur_color_set = []
for interval in xrange(NUM_ROUNDS * len(color_set)):
	if len(cur_color_set) < 1:
		cur_color_set = list(color_set)
		random.shuffle(cur_color_set)
	int_color = cur_color_set.pop()
	int_start = time.time()
	while time.time() - int_start <= TRAINING_INTERVAL:
		# render the color
		screen.fill(int_color)
		pygame.display.flip()
		# collect the data
		data = mindstream.getData()
		# tag and store it
		taggedData = tagData(data, labels[int_color], training_start_time)
		if taggedData:
			if isinstance(taggedData, collections.Iterable):
				training_data.extend(taggedData)
			else:
				training_data.append(taggedData)
			
pygame.quit()
print 'training completed, building output'

# build the output dict
output_dict = {'start_time':training_start_time, 'user':config_object['name'], 'session_number':config_object['id'], 'data':training_data}
# check output directory
dir_path = os.path.join(os.getcwd(), DATA_OUTPUT_DIRECTORY)
if not os.path.isdir(dir_path):
	print 'output directory not found, creating it now\n\tpath: %s' % dir_path
	os.mkdir(dir_path)
	
# now dump stuff to output
config_object['id'] += 1
output_filename = os.path.join(os.getcwd(), dir_path, '%s_%d.p' % (config_object['name'], int(config_object['id'])))
pickle.dump(output_dict, open(output_filename, 'wb'))
# dump new config object
pickle.dump(config_object, open(CONFIG_OBJECT_FILENAME, 'wb'))
print 'Done storing output, program finished'