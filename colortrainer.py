import random
import time
import pygame
from pygame.locals import *
import collections
import os
import pickle

import utils
from eeg import MindStream


	

# constants
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
color_set = (red, green, blue)
text_color = (0,191,255)
background_color = (50,50,50)

SCREEN_SIZE = (WIDTH, HEIGHT) = (1000, 800)
MAIN_VIEW_WIDTH = 1.0
MAIN_VIEW_HEIGHT = 0.9
APP_TITLE = 'Color Trainer'


TRAINING_INTERVAL = 5 # seconds
NUM_ROUNDS = 3
scenes = (CONNECTING, INSTRUCTION) = ('Connecting', 'Instruction')
labels = {red:'Red', green:'Green', blue:'Blue'}
# UI constants
CONNECTING_MESSAGE = 'Connecting to MindWave Headset...'
INSTRUCTION_MESSAGE = 'Once training starts, the window will randomly shift between different colors. When a given color is displayed, think about that color as hard as you can. The training program is separated into rounds, and in each round every color will be displayed once but in random order. Good luck, and stay focused.'
INSTRUCTION_DISPLAY_TIME = 10 # seconds
# persistence constants
CONFIG_OBJECT_FILENAME = 'user_id.p'
DATA_OUTPUT_DIRECTORY = 'output'
# configuration
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
	inst_msg = utils.build_text_surface(INSTRUCTION_MESSAGE, WIDTH * .90, font, text_color, background_color)
	screen.blit(inst_msg, utils.center_surface(inst_msg, screen))
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
train_prog_bar = utils.ProgressBar(WIDTH, HEIGHT / 10.0, NUM_ROUNDS * len(color_set), bg_color=background_color, border_width=5, border_color=(255,69,0))
int_color = None
for interval in xrange(NUM_ROUNDS * len(color_set)):
	if len(cur_color_set) < 1:
		cur_color_set = list(color_set)
		random.shuffle(cur_color_set)
		while int_color and cur_color_set[len(cur_color_set)-1] == int_color:
			random.shuffle(cur_color_set)
	int_color = cur_color_set.pop()
	int_start = time.time()
	while time.time() - int_start <= TRAINING_INTERVAL:
		# render the color
		ex_rect = pygame.Rect(0, 0, WIDTH * MAIN_VIEW_WIDTH, HEIGHT * MAIN_VIEW_HEIGHT)
		pygame.draw.rect(screen, int_color, ex_rect)
		screen.blit(train_prog_bar.draw(), (0,ex_rect.height))
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
	train_prog_bar.report_progress(1.0)
			
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