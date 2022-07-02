import pretty_midi

###############################################################################
# Key
###############################################################################

major_steps = [2, 2, 1, 2, 2, 2, 1]
mode_map = [0, 2, 3, 4, 5, 1, 6]

def getPitch(keysig, degree):
	step = 0
	for i in range(degree):
		step += major_steps[(keysig[1] + i) % 7]
	return keysig[0] + step

def getKeyNumber(keysig):
	return keysig[0] % 12 + mode_map[keysig[1]] * 12

def moveKey(keysig, degree):
	tonic = getPitch(keysig, degree)
	mode = (keysig[1] + degree) % 7
	return [tonic, mode]

###############################################################################
# MIDI Convertion
###############################################################################

def createBarNotes(pat, keysig=None, pitchMap=None):
	notes = []
	for melody in pat["riff"]:
		for i in range(len(melody["attacks"])):
			if melody["pitches"][i] == -127:
				continue
			pitch = melody["acc"][i]
			if keysig:
				pitch += getPitch(keysig, melody["pitches"][i])
			else:
				pitch += melody["pitches"][i]
			if pitchMap:
				pitch = pitchMap[pitch]
			# Time in bars: unit * bar / unit
			start = melody["attacks"][i] / pat["divs"]
			if i < len(melody["attacks"]) - 1:
				end = melody["attacks"][i+1] / pat["divs"]
			else:
				end = 1
			notes.append(pretty_midi.Note(127, pitch, start, end))
	return notes

###############################################################################
# Format Convertion
###############################################################################

def convertRiffToProject(parts):
	riff = []
	for part in parts:
		t, p, a = [], [], []
		for i, note in enumerate(part):
			if note["mode"] == 1:
				t.append(i)
				p.append(note["pitch"])
				a.append(note["acc"])
			elif note["mode"] == 2:
				t.append(i)
				p.append(-127)
				a.append(0)
		riff.append({"attacks": t, "pitches": p, "acc": a})
	return riff

def convertRiffToUI(riff, divs):
	parts = []
	for part in riff:
		notes = []
		for j in range(divs):
			notes.append({"pitch": 0, "acc": 0, "mode": 0})
		for (t, p, a) in zip(part["attacks"], part["pitches"], part["acc"]):
			if p == -127:
				notes[t]["mode"] = 2
			else:
				notes[t]["mode"] = 1
				notes[t]["pitch"] = p
				notes[t]["acc"] = a
		parts.append(notes)
	return parts

###############################################################################
# Test
###############################################################################

if __name__ == '__main__':
	keysig = [9, 5] # A minor
	print([getPitch(keysig, i) for i in range(0, 8)])
	keysig = [0, 0] # C Major
	print([getPitch(keysig, i) for i in range(0, 8)])
	keysig = [12*2+7, 5] # G2 minor
	keysig2 = moveKey(keysig, 4) # Get V chord
	print("This should be D3 Phrygian (mode 2): ", keysig2)
	print("Note: ", keysig2[0] % 12)
	print("Octave: ", keysig2[0] // 12)
	keysig2 = moveKey(keysig, 7)
	print("This should be G3: ", keysig2)
	keysig2 = moveKey(keysig, 7*3)
	print("This should be G5: ", keysig2)