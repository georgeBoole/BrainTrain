import random
import time
import pygame
from pygame.locals import *
import collections
from collections import defaultdict as ddict
import os
import pickle

import utils
from eeg import MindStream
from scene_management import Scene, SceneManager, QUIT_SCENE_MANAGER_KEYWORD

# constants
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (107,255,113)
blue = (58,167,255)
magenta = (147,112,219) 
yellow = (255,244,80)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
color_set = (red, green, blue)
text_color = white
background_color = (50,50,50)

SCREEN_SIZE = (WIDTH, HEIGHT) = (1000, 800)
MAIN_VIEW_WIDTH = 1.0
MAIN_VIEW_HEIGHT = 0.9
APP_TITLE = 'Color Trainer'


TRAINING_INTERVAL = 4 # seconds
NUM_ROUNDS = 2
scenes = (CONNECTING, INSTRUCTION) = ('Connecting', 'Instruction')
labels = {red:'Red', green:'Green', blue:'Blue'}
# UI constants
CONNECTING_MESSAGE = 'Connecting to MindWave Headset...'
INSTRUCTION_MESSAGE = 'Once training starts, the window will randomly shift between different colors. When a given color is displayed, think about that color as hard as you can. The training program is separated into rounds, and in each round every color will be displayed once but in random order. Good luck, and stay focused.'
INSTRUCTION_DISPLAY_TIME = 5 # seconds
# persistence constants
CONFIG_OBJECT_FILENAME = 'user_id.p'
DATA_OUTPUT_DIRECTORY = 'output'

def tagData(data, label, starting_time):
	if not data:
		return None
	filtered_data = filter(lambda x: len(x.keys()) > 1, data)
	tagged_data = [ dict( [ ('time', time.time() - starting_time), ('label', label) ] + d.items() ) for d in filtered_data ]
	return tagged_data

SCENE_NAMES = (CONNECTING, INTRODUCTION, TRAINING, ENDING) = ('Connecting', 'Introduction', 'Training', 'Ending')

def _get_color_pool():
	lst = list(color_set)
	random.shuffle(lst)
	return lst
	
def calculate_round_interval(start_time, interval_length):
	elapsed_time = time.time() - start_time
	rnd_dur = interval_length * len(color_set)
	rnd = int( elapsed_time / rnd_dur )
	int_time = elapsed_time - (rnd*rnd_dur)
	interval = int(int_time / interval_length)
	return (rnd, interval)
	

# now try an example
class ConnectingScene(Scene):
	
	def __init__(self, size, mind_stream, application_font):
		self.name=CONNECTING
		self.size = size
		self.font = application_font#super(Scene, self).__init__(CONNECTING, size, application_font)
		self.mind_stream = mind_stream

	def start(self):
		self.is_started=True

	def update(self, events):
		if self.mind_stream.isConnected():
			return INTRODUCTION
			
	def render(self):
		canvas = pygame.Surface(self.size)
		canvas.fill(background_color)
		msgview = self.font.render(CONNECTING_MESSAGE, True, text_color)
		canvas.blit(msgview, utils.center_surface(msgview, canvas))
		return canvas
		
class IntroductionScene(Scene):
	
	def __init__(self, size, application_font):
		self.name=INTRODUCTION
		self.size = size
		self.font = application_font
		self.introduction_start_time = -1
		
	def start(self):
		self.is_started=True
		self.introduction_start_time = time.time()
		
	def update(self, events):
		if time.time() - self.introduction_start_time > INSTRUCTION_DISPLAY_TIME:
			return TRAINING

	def render(self):
		canvas = pygame.Surface(self.size)
		canvas.fill(background_color)
		inst_msg = utils.build_text_surface(INSTRUCTION_MESSAGE, self.size[0] * .90, self.font, text_color, background_color)
		canvas.blit(inst_msg, utils.center_surface(inst_msg, canvas))
		return canvas
		
class TrainingScene(Scene):
	
	def __init__(self, size, app_font, mind_stream, training_data_output_func, config_obj, num_rounds=NUM_ROUNDS, interval_duration=TRAINING_INTERVAL):
		self.name=TRAINING
		self.size = size
		self.font = app_font
		self.mind_stream = mind_stream
		self.rounds = num_rounds
		self.interval_duration = interval_duration
		self.current_interval = 0
		self.training_data = []
		self.data_output = training_data_output_func
		self.config = config_obj
		
	def start(self):
		self.is_started=True
		self.start_time = time.time()
		self.round_duration = len(color_set) * self.interval_duration
		self.pools = ddict(_get_color_pool)
		def color_builder():
			(r, i) = calculate_round_interval(self.start_time, self.interval_duration)
			return self.pools[r].pop()
		self.colors = ddict(lambda: ddict(color_builder))
		# graphics stuff
		self.prog_bar = utils.ProgressBar(self.size[0], self.size[1] / 10.0, 1.0, bg_color=background_color, border_width=5, border_color=(255,69,0))
		
	def update(self, events):
		(r, i) = calculate_round_interval(self.start_time, self.interval_duration)
		
		steps_done = r*len(color_set) + i
		progress = steps_done / float(self.rounds * len(color_set))
		self.prog_bar.set_progress(progress)
		if r >= self.rounds:
			return QUIT_SCENE_MANAGER_KEYWORD
		else:
			train_data = self.mind_stream.getData()
			tagged_data = tagData(train_data, labels[self._color()], time.time())
			self.data_output(tagged_data)
		
	
	def _color(self):
		(r, i) = calculate_round_interval(self.start_time, self.interval_duration)
		return self.colors[r][i]
				
	def render(self):
		canvas = pygame.Surface(self.size)
		canvas.fill(self._color())
		canvas.blit(self.prog_bar.draw(), (0, .9 * self.size[1]))
		return canvas

#self, size, app_font, mind_stream, training_data_output_func, config_obj, num_rounds=NUM_ROUNDS, interval_duration=TRAINING_INTERVAL
def generate_scenes(window_size, font, ms, data_agg_func, user_conf):

	conn = ConnectingScene(window_size, ms, font)

	intro = IntroductionScene(window_size, font)

	train = TrainingScene(window_size, font, ms, data_agg_func, user_conf)

	return (conn, intro, train)
	

def initialize_graphics():
	random.seed()
	pygame.init()
	pygame.font.init()
	screen = pygame.display.set_mode(SCREEN_SIZE)
	pygame.display.set_caption(APP_TITLE)
	font = pygame.font.Font(None, 32)
	return (screen, font)

def configure_trainer():
	isNewUser = False
	if not os.path.exists(CONFIG_OBJECT_FILENAME):
		# get the user
		print 'No existing configuration object found, will create a new one'
		username = raw_input('Please enter a username:')
		cfg_obj = {'name':username, 'id':0}
		pickle.dump(cfg_obj, open(CONFIG_OBJECT_FILENAME, 'wb'))
		isNewUser=True
	return (pickle.load(open(CONFIG_OBJECT_FILENAME, 'rb')), isNewUser)
		
def runTrainer(screen, manager):
	print 'running training program'
	while manager.is_running():
		evts = []
		for event in pygame.event.get():
			#Ends program if the 'x' GUI element is clicked
			if event.type == pygame.QUIT:
				#Ends pygame
				pygame.quit()
				#Quits all active threads
				os._exit(1)
			else:
				evts.append(event)
		manager.update(evts)
		screen.blit(manager.render(), (0,0))
		pygame.display.flip()
	print 'finished running trainer program'

def main():
	# begin connecting asap since it takes a while
	my_mindstream = MindStream()
	# get user configuration
	(user_configuration, isNew) = configure_trainer()
	user_configuration['id'] += 1
	# initialize pygame
	(screen, default_font) = initialize_graphics()
	# init data collection
	training_data = []
	def proc_data(data):
		if not data:
			return
		elif isinstance(data, collections.Iterable):
			training_data.extend(data)
		else:
			training_data.append(data)
	# initialize scenes
	scenes = generate_scenes(SCREEN_SIZE, default_font, my_mindstream, proc_data, user_configuration)
	manager = SceneManager(scenes)
	# run the program
	runTrainer(screen, manager)
	# clean up
	train_start_time = manager.scenes[2].start_time
	(username, sid) = (user_configuration['name'], user_configuration['id'])
	pdump = {'start_time':train_start_time, 'data':training_data, 'user':user_configuration['name'], 'session_number':user_configuration['id']}
	output_filename = os.path.join(os.getcwd(), DATA_OUTPUT_DIRECTORY, '%s_%d.p' % (username, int(sid)))
	pickle.dump(pdump, open(output_filename, 'wb'))
	pickle.dump(user_configuration, open(CONFIG_OBJECT_FILENAME, 'wb'))
	print 'training data dumped to file, exiting program'
	
if __name__ == '__main__':
	main()
	#Ends program once training is finished
	#Quits pygame
	pygame.quit()
	#Quits all active threads
	os._exit(1)
	
	
	
	
	
	
	
