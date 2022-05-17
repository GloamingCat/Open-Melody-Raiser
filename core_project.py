import pretty_midi, json, sys
import core_presets as ps
import core_util as util

###############################################################################
# Load
###############################################################################

def defaultProject():
	project = ps.song()
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
		for i, pat in enumerate(track["pats"]):
			notes = util.createBarNotes(pat, _moveKey(project["keysig"], pat["root"]))
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
		notes = util.createBarDrums(project["drums"][i], project["drumset"])
		for n in notes:
			n.start = (i + n.start) * spb
			n.end = (i + n.end) * spb
		drumtrack.notes += notes
	midi.instruments.append(drumtrack)
	midi.write(file)

def savePreset(preset, file):
	f = open(file, "w")
	f.write(json.dumps(preset))
	f.close()

def saveProject(project, file):
	savePreset(project, file)

###############################################################################
# Modify
###############################################################################

def addTrack(project, minBarCount=0):
	barCount = project["tracks"][0]["pats"] if len(project["tracks"]) > 0 else 0
	if barCount > minBarCount:
		# Extend current tracks
		addBars(project, barCount - minBarCount)
		# Add track
		project["tracks"].append(ps.emptyTrack(barCount))
	else:
		project["tracks"].append(ps.emptyTrack(minBarCount))

def addBars(project, barCount=0):
	for track in project["tracks"]:
		tracks["pats"] += [ps.emptyBar() for i in range(barCount)]

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