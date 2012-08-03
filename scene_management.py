#!/usr/bin/env python
# encoding: utf-8
"""
scene_management.py

Created by Michael Sobczak on 2012-08-02.
Copyright (c) 2012 Michael Sobczak. All rights reserved.
"""

import abc

QUIT_SCENE_MANAGER_KEYWORD = 'Quit'

class Scene(object):
	__metaclass__ = abc.ABCMeta
	
	def __init__(self, name, size, default_font):
		self.name = name
		self.size = size
		self.font = default_font
	
	
	def start(self):
		""" perform any necessary initialization in here to avoid update slowdown """
		self.is_started = True

	def isStarted(self):
		return self.is_started

	@abc.abstractmethod
	def update(self, events):
		""" update the state of the scene given new stuff and return the name of the next scene or None to avoid transitioning """
		return

	@abc.abstractmethod	
	def render(self):
		""" return a surface with this scene rendered on it """
		return


class SceneManager(object):
	
	def __init__(self, scenes):
		self.scenes = scenes
		self.current_scene = scenes[0] if scenes and len(scenes) > 0 else None
		self.trans_map = dict([ (x.name, x) for x in scenes])
		self.next_scene = None
		self.is_shutdown = False
		#print 'new scene manager initializing with initial scene %s' % self.current_scene.name
		
	def update(self, events):
		newSceneName = self.current_scene.update(events)
		if newSceneName:
			#print 'NEW SCENE NAME: %s' % newSceneName
			if newSceneName == QUIT_SCENE_MANAGER_KEYWORD:
				self.is_shutdown = True
				return
			self.next_scene = self.trans_map[newSceneName] if newSceneName in self.trans_map else None
			#print 'NEW SCENE IS: %s' % self.next_scene.name
			if not self.next_scene:
				print 'Scene transition attempted but scene named %s not found' % newSceneName
		
	def render(self):
		scene_surface = self.current_scene.render()
		if self.next_scene:
			#print 'NEXT SCENE SPECIFIED!!'
			self.current_scene = self.next_scene
			#print 'CURRENT SCENE IS NOW %S'
			self.current_scene.start()
			self.next_scene = None
		return scene_surface
	
	def is_running(self):
		return not self.is_shutdown

		
	
		
