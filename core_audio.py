#!/usr/bin/python

import subprocess, os

fspath = "fluidsynth/bin/fluidsynth.exe"
playingProcess = None

###############################################################################
# Player
###############################################################################

def playMidi(file="temp", timeout=-1):
	global playingProcess
	cmd = fspath + " Microsoft_GS.sf2 %s.mid" % file
	if playingProcess:
		playingProcess.kill()
	playingProcess = subprocess.Popen(cmd)
	print('Running in process', playingProcess.pid)
	if timeout > 0:
		try:
			print("Waiting...")
			playingProcess.wait(timeout=timeout)
			print("MIDI played entirely.")
			return True
		except:
			playingProcess.kill()
			print("MIDI played partially.")
			return False
	else:
		return True

def stopMidi():
	if playingProcess:
		playingProcess.kill()
		return True
	return False

def clear():
	global playingProcess
	if playingProcess:
		playingProcess.kill()

###############################################################################
# Converter
###############################################################################

def generateOgg(infile="temp", outfile="temp"):
	cmd = fspath + " -nli -r 48000 -o synth.cpu-cores=2 -T oga -F %s.ogg Microsoft_GS.sf2 %s.mid" % (outfile, infile)
	process = subprocess.Popen(cmd)
	try:
		print('Running in process', process.pid)
		process.wait()
		return True
	except subprocess.TimeoutExpired:
		print('Timed out - killing', process.pid)
		process.kill()
		return False

###############################################################################
# Test
###############################################################################

if __name__ == "__main__":
	if os.path.exists("temp.mid"):
		if generateOgg():
			print("temp.ogg generated.")
		playMidi(timeout=3)
	else:
		print("Test project first to generate temp.mid file.")