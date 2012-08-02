#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Michael Sobczak on 2012-08-02.
Copyright (c) 2012 Michael Sobczak. All rights reserved.
"""

import pygame
from pygame.locals import *
import ConfigParser as cp
from collections import defaultdict

white=(255,255,255)
black=(0,0,0)
# returns the drawing coordinates to use if you want to draw the 
# inner surface in the center of the outer surface
def center_surface(inner_surface, outer_surface):
	os = outer_surface
	ns = inner_surface
	(ow, oh) = os.get_size()
	(nw, nh) = ns.get_size()
	return ( (ow - nw)/2.0, (oh - nh)/2.0)

def build_text_surface(text_string, max_width, font, color=white, bg_color=black):
	sz = font.size
	w = lambda t: sz(t)[0]
	h = lambda t: sz(t)[1]
	text_lines = []
	temp_line = ''
	for letter in text_string:
		if w(temp_line + letter) <= max_width:
			temp_line += letter
		else:
			text_lines.append(temp_line)
			temp_line = letter
	if len(temp_line) > 0:
		text_lines.append(temp_line)
	h_sep = max([h(x) for x in text_lines])
	text_surface = pygame.Surface((max_width, h_sep * len(text_lines)))
	text_surface.fill(bg_color)
	for (idx, line) in enumerate(text_lines):
		line_surface = font.render(line, True, color)
		text_surface.blit(line_surface, (0, h_sep * idx))
	return text_surface
	
def load_config(filename):
	cfg = cp.ConfigParser()
	cfg.read(filename)
	cfg_dict = defaultdict(defaultdict(str))
	for sec in cfg.sections():
		for opt in cfg.options(sec):
			cfg_dict[sec][opt] = cfg.get(sec, opt)
	return cfg_dict
			
	
class ProgressBar(object):
	
	def __init__(self, width, height, upper_bound=100.0, fill_color=(238,118,0), bg_color=(0,0,0), border_color=(105,105,105), border_width=0):
		self.w = width
		self.h = height
		self.max = float(upper_bound)
		self.color = fill_color
		self.bg = bg_color
		self.load = 0
		self.border_width = border_width
		self.border_color = border_color
		
	def draw(self):
		progress = self.load / float(self.max)
		bar_width = progress * self.w
		canvas = pygame.Surface((self.w, self.h))
		canvas.fill(self.bg)
		bar_rect = pygame.Rect(0,0, bar_width, self.h)
		pygame.draw.rect(canvas, self.color, bar_rect)
		if self.border_width > 0:
			pygame.draw.rect(canvas, self.border_color, bar_rect, self.border_width)
		return canvas
		
	def report_progress(self, progress_change):
		self.load += progress_change
