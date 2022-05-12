#!/usr/bin/python

import pretty_midi, json, sys
import core_generator as gen
import core_presets as ps

###############################################################################
# Load
###############################################################################

def defaultProject():
	project = ps.project()
	melodyOct = 5 - (project["keysig"][0] // 12)
	melody = [
		ps.arp(0, 7*melodyOct), ps.arp(1, 7*melodyOct), 
		ps.arp(0, 7*melodyOct+4), ps.arp(1, 7*melodyOct+4)
	]
	harmonyOct = 4 - (project["keysig"][0] // 12)
	harmony = [
		ps.triad(0, 7*harmonyOct), ps.triad(0, 7*harmonyOct+2), 
		ps.triad(0, 7*harmonyOct+4), ps.triad(0, 7*harmonyOct+3)
	]
	drums = [ps.drums(0), ps.drums(0), ps.drums(0), ps.drums(1)]
	project["tracks"][0]["pats"] = melody
	project["tracks"][1]["pats"] = harmony
	project["drums"] = drums
	return project

def generateProject(params):
	project = ps.project()
	project["timesig"][0] = params["bpb"]
	project["bpm"] = params["bpm"]
	params["seedmel"] = 0
	params["seedhar"] = 0
	params["bars"] = [int(s) for s in params["bars"].split()]
	gen.song(project, params)
	return project

def loadProject(file):
	f = open(file, "r")
	obj = json.loads(f.read())
	f.close()
	return obj

def loadPreset(file):
	f = open(file, "r")
	obj = json.loads(f.read())
	f.close()
	return obj

###############################################################################
# Write
###############################################################################
	
def exportMidi(project, file = "temp.mid"):
	midi = pretty_midi.PrettyMIDI(initial_tempo = project["bpm"])
	# Header
	keysig = pretty_midi.KeySignature(_getKeyNumber(project["keysig"]), 0)
	midi.key_signature_changes.append(keysig)
	timesig = pretty_midi.TimeSignature(project["timesig"][0], project["timesig"][1], 0)
	midi.time_signature_changes.append(timesig)
	spb = timesig.numerator / project["bpm"] * 60 # seconds per bar
	# Instrument tracks
	for track in project["tracks"]:
		miditrack = pretty_midi.Instrument(program = track["inst"], name = track["name"])
		for i in range(len(track["pats"])):
			pat = track["pats"][i]
			notes = _createBarNotes(pat, _moveKey(project["keysig"], pat["root"]))
			for n in notes:
				n.start = (i + n.start) * spb
				n.end = (i + n.end) * spb
			miditrack.notes += notes
		miditrack.control_changes.append(pretty_midi.ControlChange(7, track["vol"], 0))
		miditrack.control_changes.append(pretty_midi.ControlChange(10, track["pan"], 0))
		miditrack.control_changes.append(pretty_midi.ControlChange(91, track["rev"], 0))
		miditrack.control_changes.append(pretty_midi.ControlChange(93, track["cho"], 0))
		midi.instruments.append(miditrack)
	# Percussion tracks
	drumtrack = pretty_midi.Instrument(program = 0, name = "Drums", is_drum = True)
	drumtrack.control_changes.append(pretty_midi.ControlChange(7, project["vol"], 0))
	drumtrack.control_changes.append(pretty_midi.ControlChange(10, project["pan"], 0))
	drumtrack.control_changes.append(pretty_midi.ControlChange(91, project["rev"], 0))
	drumtrack.control_changes.append(pretty_midi.ControlChange(93, project["cho"], 0))
	for i in range(len(project["drums"])):
		notes = _createBarDrums(project["drums"][i], project["drumset"])
		for n in notes:
			n.start = (i + n.start) * spb
			n.end = (i + n.end) * spb
		drumtrack.notes += notes
	midi.instruments.append(drumtrack)
	midi.write(file)

def saveProject(project, file):
	f = open(file, "w")
	f.write(json.dumps(project))
	f.close()

###############################################################################
# Util
###############################################################################

major_steps = [2, 2, 1, 2, 2, 2, 1]
mode_map = [0, 2, 3, 4, 5, 1, 6]

def _getPitch(keysig, degree):
	step = 0
	for i in range(degree):
		step += major_steps[(keysig[1] + i) % 7]
	return keysig[0] + step

def _getKeyNumber(keysig):
	return keysig[0] % 12 + mode_map[keysig[1]] * 12

def _moveKey(keysig, degree):
	tonic = _getPitch(keysig, degree)
	mode = (keysig[1] + degree) % 7
	return [tonic, mode]

def _createBarNotes(pat, keysig):
	notes = []
	for melody in pat["riff"]:
		for i in range(len(melody["attacks"])):
			if melody["pitches"][i] == -127:
				continue
			pitch = _getPitch(keysig, melody["pitches"][i]) + melody["acc"][i]
			# Time in bars: unit * bar / unit
			start = melody["attacks"][i] / pat["divs"]
			if i < len(melody["attacks"]) - 1:
				end = melody["attacks"][i+1] / pat["divs"]
			else:
				end = 1
			notes.append(pretty_midi.Note(127, pitch, start, end))
	return notes

def _createBarDrums(drums, drumset):
	notes = []
	for layer in drums["attacks"]:
		for i in range(len(layer)):
			if layer[i] == 0:
				continue
			pitch = drumset[layer[i]-1]
			start = i / drums["divs"]
			end = (i+1) / drums["divs"]
			notes.append(pretty_midi.Note(127, pitch, start, end))
	return notes

###############################################################################
# Test
###############################################################################

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		project = defaultProject()
		exportMidi(project, "temp.mid")
		saveProject(project, "defaultProject.proj")
	elif sys.argv[1] == "pretty_midi":
		cello_c_chord = pretty_midi.PrettyMIDI()
		cello_program = pretty_midi.instrument_name_to_program('Cello')
		cello = pretty_midi.Instrument(program=cello_program)
		for note_name in ['C5', 'E5', 'G5']:
		    note_number = pretty_midi.note_name_to_number(note_name)
		    note = pretty_midi.Note(velocity=100, pitch=note_number, start=0, end=.5)
		    cello.notes.append(note)
		cello_c_chord.instruments.append(cello)
		cello_c_chord.write('temp.mid')
	elif sys.argv[1] == "scale":
		keysig = [9, 5] # A minor
		print([_getPitch(keysig, i) for i in range(0, 8)])
		keysig = [0, 0] # C Major
		print([_getPitch(keysig, i) for i in range(0, 8)])
		keysig = [12*2+7, 5] # G2 minor
		keysig2 = _moveKey(keysig, 4) # Get V chord
		print("This should be D3 Phrygian (mode 2): ", keysig2)
		print("Note: ", keysig2[0] % 12)
		print("Octave: ", keysig2[0] // 12)
		keysig2 = _moveKey(keysig, 7)
		print("This should be G3: ", keysig2)
		keysig2 = _moveKey(keysig, 7*3)
		print("This should be G5: ", keysig2)