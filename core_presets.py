def project():
	project = dict()
	# Melody track
	track1 = dict()
	track1["name"] = "Melody"
	track1["inst"] = 0
	track1["vol"] = 100
	track1["pan"] = 64
	track1["rev"] = 40
	track1["cho"] = 0
	track1["pats"] = []
	# Harmony track
	track2 = dict()
	track2["name"] = "Harmony"
	track2["inst"] = 25
	track2["vol"] = 80
	track2["pan"] = 64
	track2["rev"] = 20
	track2["cho"] = 20
	track2["pats"] = []
	# Percussion
	project["vol"] = 100
	project["pan"] = 64
	project["rev"] = 0
	project["cho"] = 0
	project["drums"] = []
	project["drumset"] = [35, 40]
	# Signature
	project["bpm"] = 90
	project["timesig"] = [4, 4]
	project["keysig"] = [12*2+7, 5] # G2 Minor
	project["tracks"] = [track1, track2]
	return project

def arp(i, root):
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
	bar["riff"] = [melody]
	return bar

def drums(i):
	bar = dict()
	bar["divs"] = 8
	bar["attacks"] = [[1, 0, 2, 0, 1, 0, 2, 0]]
	return bar

def triad(i, root):
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
	bar["riff"] = [chord1, chord2, chord3]	
	return bar