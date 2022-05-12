#!/usr/bin/python

import random
import core_presets as ps # Temporary

def melody(seq, params, har, previous=None):
	# Temporary
	random.seed(params["seedmel"])
	if seq == len(params["bars"]) - 1:
		# Last bar
		return ps.arp(seq, 3)
	else:
		return ps.arp(seq, 0)

progession = [0, 2, 4, 3]
def harmony(seq, params, previous=None):
	# Temporary
	random.seed(params["seedhar"])
	return ps.triad(0, progession[seq % 4])

def song(project, params):
	har = [harmony(0, params)]
	mel = [melody(0, params, har[0])]
	for i in range(1, len(params["bars"])):
		har.append(harmony(i, params, har[i-1]))
		mel.append(melody(i, params, har[0], mel[i-1]))
	drums = [ps.drums(0)] * len(params["bars"])
	project["tracks"][0]["pats"] = mel
	project["tracks"][1]["pats"] = har
	project["drums"] = drums
	return project