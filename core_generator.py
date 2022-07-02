import random
import core_presets as ps

###############################################################################
# Song
###############################################################################

# Generates a full song according to given parameters.
def song(params):
	project = ps.song()
	project["timesig"][0] = params["bpb"]
	project["bpm"] = params["bpm"]
	if type(params["sections"]) is str:
		params["sections"] = [int(s) for s in params["sections"].split()]
	elif type(params["sections"]) is int:
		params["sections"] = [params["sections"]]
	tracks = []
	tracks.append(track(params, tracks, "har", harmonyNode, ps.harmony))
	tracks.append(track(params, tracks, "mel", melodyNode, ps.melody))
	tracks.append(track(params, tracks, "drm", drumNode, ps.drums))
	project["tracks"] = [tracks[1], tracks[0], tracks[2]]
	return project

###############################################################################
# Track
###############################################################################

def track(params, tracks, suffix, newNode, newTrack):
	if ("seed" + suffix) in params:
		random.seed(params["seed" + suffix])
	t = newTrack()
	nodes = dict()
	previous = None
	for i in params["sections"]:
		node = None
		if i in nodes:
			node = nodes[i]
		else:
			node = newNode(params, previous)
			nodes[i] = node
		t["pats"] += node
		previous = node
	return t

def melodyNode(params, previous):
	progession = [0, 0, 0, 3]
	# TODO: use previous
	return [ps.arp(i, progession[i]) for i in range(4)] 

def harmonyNode(params, previous):
	progession = [0, 2, 4, 3]
	# TODO: use previous
	return [ps.triad(0, progession[i]) for i in range(4)]

def drumNode(params, previous):
	return [ps.drumloop(0) for i in range(4)]

###############################################################################
# Bar
###############################################################################

def bar(params, project, pos=-1):
	empty = ps.emptyBar()
	for t in projects["tracks"]:
		if pos == -1:
			pos = len(t["pats"]) - 1
		if pos >= 0 and pos < len(t["pats"]):
			previous = t["pats"][pos]
		else:
			previous = empty
		# TODO: new bar from previous
		t["pats"].append(previous)
