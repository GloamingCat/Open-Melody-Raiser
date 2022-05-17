import random
import core_presets as ps

###############################################################################
# Song
###############################################################################

def project(params):
	project = ps.song()
	project["timesig"][0] = params["bpb"]
	project["bpm"] = params["bpm"]
	params["seedmel"] = 0
	params["seedhar"] = 0
	params["bars"] = [int(s) for s in params["bars"].split()]
	song(project, params)
	return project

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

###############################################################################
# Track
###############################################################################

def track(params, tracks, pos=-1):
	# Placeholder
	return ps.emptyTrack()

def melody(params, tracks, pos=-1):
	# Temporary
	random.seed(params["seedmel"])
	if seq == len(params["bars"]) - 1:
		# Last bar
		return ps.arp(seq, 3)
	else:
		return ps.arp(seq, 0)

progession = [0, 2, 4, 3]
def harmony(params, tracks, pos=-1):
	# Temporary
	random.seed(params["seedhar"])
	return ps.triad(0, progession[seq % 4])

###############################################################################
# Bar
###############################################################################

def bar(params, project, pos=-1):
	# Placeholder
	return ps.emptyBar()