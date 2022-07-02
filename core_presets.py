###############################################################################
# Song
###############################################################################

def song():
	project = dict()
	project["bpm"] = 90
	project["timesig"] = [4, 4]
	project["keysig"] = [12*2+7, 5] # G2 Minor
	project["drumset"] = [35, 40]
	project["tracks"] = [melody(0), harmony(0), drums(0)]
	return project

###############################################################################
# Track
###############################################################################

def emptyTrack(bars=0):
	track = dict()
	track["name"] = "New Track"
	track["inst"] = 0
	track["vol"] = 64
	track["pan"] = 64
	track["rev"] = 64
	track["cho"] = 64
	track["pats"] = []
	for i in range(bars):
		track["pats"].append(emptyBar())
	return track

def harmony(bars=0):
	track = dict()
	track["name"] = "Harmony"
	track["inst"] = 25
	track["vol"] = 80
	track["pan"] = 64
	track["rev"] = 20
	track["cho"] = 20
	track["pats"] = []
	for i in range(bars):
		track["pats"].append(triad(i))
	return track

def melody(bars=0):
	track = dict()
	track["name"] = "Melody"
	track["inst"] = 0
	track["vol"] = 100
	track["pan"] = 64
	track["rev"] = 40
	track["cho"] = 0
	track["pats"] = []
	for i in range(bars):
		track["pats"].append(arp(i))
	return track

def drums(bars=0):
	track = dict()
	track["name"] = "Drums"
	track["inst"] = -1
	track["vol"] = 100
	track["pan"] = 64
	track["rev"] = 0
	track["cho"] = 0
	track["pats"] = []
	for i in range(bars):
		track["pats"].append(drumloop(i))
	return track

###############################################################################
# Bar
###############################################################################

def emptyBar():
	bar = dict()
	bar["root"] = 0
	bar["divs"] = 4
	bar["riff"] = [{"pitches": [], "attacks": [], "acc": []}] * 6
	return bar

def arp(i, root=0):
	melody = dict()
	if i % 2 == 0:
		melody["pitches"] = [0, 2, 4, 3]
	else:
		melody["pitches"] = [3, 4, 2, 0]
	melody["attacks"] = [0, 1, 2, 3]
	melody["acc"] = [0, 0, 0, 0]
	bar = dict()
	bar["root"] = root
	bar["divs"] = 4
	bar["riff"] = [melody] + [{"pitches": [], "attacks": [], "acc": []}] * 5
	return bar

def triad(i, root=0):
	chord1 = dict()
	chord1["pitches"] = [0, 0]
	chord1["attacks"] = [0, 1]
	chord1["acc"] = [0, 0, 0, 0]
	chord2 = dict()
	chord2["pitches"] = [2, 2]
	chord2["attacks"] = [0, 1]
	chord2["acc"] = [0, 0, 0, 0]
	chord3 = dict()
	chord3["pitches"] = [4, 4]
	chord3["attacks"] = [0, 1]
	chord3["acc"] = [0, 0, 0, 0]
	bar = dict()
	bar["root"] = root
	bar["divs"] = 2
	bar["riff"] = [chord1, chord2, chord3] + [{"pitches": [], "attacks": [], "acc": []}] * 3
	return bar

def drumloop(i):
	bar = dict()
	bar["root"] = 0
	bar["divs"] = 4
	loop = dict()
	loop["pitches"] = [0, 1, 0, 1]
	loop["attacks"] = [0, 1, 2, 3]
	loop["acc"] = [0, 0, 0, 0]
	bar["riff"] = [loop] + [{"pitches": [], "attacks": [], "acc": []}] * 5
	return bar