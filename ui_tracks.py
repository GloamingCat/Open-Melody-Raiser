import tkinter, ui_common
import pretty_midi.constants as midi
from tkinter import ttk

KEYS = ["vol", "rev", "pan", "cho"]
NAMES = ["Vol", "Rvrb", "Pan", "Chor"]
POS = [(2, 0, 3, 0), (4, 0, 5, 0), (2, 1, 3, 1), (4, 1, 5, 1)]
INSTS = [str(i) + ": " + midi.INSTRUMENT_MAP[i] for i in range(len(midi.INSTRUMENT_MAP))]

class TrackGroup(tkinter.LabelFrame):

	def __init__(self, window, onTrackClick=None, onBarClick=None):
		super().__init__(window, text="Tracks")
		# Track selector
		self._trackSelector = TrackSelector(self, onTrackClick, onBarClick)
		self._trackSelector.pack(expand=True, fill=tkinter.BOTH)

	def loadTracks(self, project):
		self._trackSelector.setTracks(project["tracks"])

	def saveTracks(self, project):
		project["tracks"] = self._trackSelector.getTracks()

class TrackSelector(tkinter.Frame):

	def __init__(self, top, onTrackClick, onBarClick):
		super().__init__(top)
		self._scrollFrame = ui_common.ScrollableFrame(self)
		self._scrollFrame.pack(fill=tkinter.BOTH, expand=True)
		self._trackVars = dict()
		self._trackFrames = []
		self._selectedTrack = -1
		self._onBarClick = onBarClick
		self._onTrackClick = onTrackClick

	def getTracks(self):
		tracks = []
		for i, frame in enumerate(self._trackFrames):
			track = {}
			track["name"] = self._trackVars["name"][i].get()
			track["inst"] = INSTS.index(self._trackVars["inst"][i].get())
			for k in KEYS:
				track[k] = int(self._trackVars[k][i].get())
			track["pats"] = frame.barSelector.buildBars()
			tracks.append(track)
		return tracks

	def setTracks(self, tracks):
		for k in KEYS:
			self._trackVars[k] = []
		self._trackVars["name"] = []
		self._trackVars["inst"] = []
		for frame in self._trackFrames:
			frame.destroy()
		self._trackFrames = []
		self._selectedTrack = -1
		self._scrollFrame.innerFrame().columnconfigure(4, weight=1)
		for track in tracks:
			self.insertTrack(track)
		self.repackFrames()

	def insertTrack(self, track):
		index = len(self._trackFrames)
		bg = "white" if index % 2 == 0 else "lightgrey"
		frame = tkinter.Frame(self._scrollFrame.innerFrame(), borderwidth=2, bg=bg)
		frame.index = index
		def selectTrack(e):
			self._onTrackClick(self.selectTrack(frame.index))
			self._onBarClick(None)
		frame["relief"] = ui_common.BORDEROFF
		frame.bind("<Button-1>", selectTrack)
		frame.bind("<Button-3>", selectTrack)
		# Variables
		nameVar = tkinter.StringVar(value=track["name"] if track else "New Track")
		instVar = tkinter.StringVar(value=INSTS[track["inst"]] if track else INSTS[0])
		self._trackVars["name"].append(nameVar)
		self._trackVars["inst"].append(instVar)
		# Name
		entry = tkinter.Entry(frame, textvariable=nameVar)
		entry.grid(column=0, row=0, sticky="ew", padx=5, pady=5)
		# Play Mode button
		button = ui_common.ToggleButton(frame, [" On ", "Mute", "Solo"])
		button.grid(column=1, row=0, sticky=tkinter.EW, padx=2, pady=5)
		# Instrument
		box = ttk.Combobox(frame, width=8, state='readonly', textvariable=instVar, value=instVar.get())
		box["values"] = INSTS
		box.grid(column=0, row=1, columnspan=2, sticky=tkinter.EW, padx=5, pady=5)
		# Properties
		for k, n, p in zip(KEYS, NAMES, POS):
			var = tkinter.StringVar(value=track[k] if track else 64)
			self._trackVars[k].append(var)
			label = tkinter.Label(frame, text=n + ":", bg=bg)
			label.bind("<Button-1>", selectTrack)
			label.bind("<Button-3>", selectTrack)
			label.grid(column=p[0], row=p[1], sticky=tkinter.W, padx=2, pady=2)
			box = ttk.Spinbox(frame, from_=1, to=127, width=4, textvariable=var)
			box.grid(column=p[2], row=p[3], sticky=tkinter.EW, padx=2, pady=2)
		# Bar list
		def selectBar(b):
			self._onTrackClick(self.selectTrack(b.trackIndex()))
			self._onBarClick(b)
		frame.barSelector = BarSelector(frame, track["pats"] if track else [], selectBar)
		frame.barSelector.grid(column=6, row=0, padx=2, pady=2, rowspan=3, sticky=tkinter.NSEW)
		if self._selectedTrack >= 0:
			self._trackFrames.insert(self._selectedTrack, frame)
			self.selectTrack(self._selectedTrack + 1)
		else:
			self._trackFrames.append(frame)
		return frame

	def replaceTrack(self, obj):
		self._trackVars["name"][self._selectedTrack].set(obj["name"])
		self._trackVars["inst"][self._selectedTrack].set(INSTS[int(obj["inst"])])
		for k in KEYS:
			self._trackVars[k][self._selectedTrack].set(obj[k])
		self._trackFrames[self._selectedTrack].barSelector.setBars(obj["pats"])

	def moveTrack(self, i):
		aux = self._selectedTrack + i
		if aux >= 0 and aux < len(self._trackFrames):
			x, y = self._trackFrames[self._selectedTrack], self._trackFrames[aux]
			self._trackFrames[self._selectedTrack], self._trackFrames[aux] = y, x
			self._onTrackClick(self.selectTrack(aux))
			self._onBarClick(None)

	def deleteTrack(self):
		self._trackFrames.pop(self._selectedTrack).destroy()
		if self._selectedTrack < len(self._trackFrames):
			i = self._selectedTrack
		else:
			i = self._selectedTrack - 1
		self._selectedTrack = -1
		self._onTrackClick(self.selectTrack(i))
		self._onBarClick(None)

	def repackFrames(self):
		for i, frame in enumerate(self._trackFrames):
			frame.index = i
			frame.pack(fill=tkinter.BOTH)

	def selectTrack(self, index):
		if index == self._selectedTrack:
			return self._trackFrames[index] if index >= 0 else None
		if self._selectedTrack >= 0:
			frame = self._trackFrames[self._selectedTrack]
			frame["relief"] = ui_common.BORDEROFF
			frame.barSelector.selectBar(-1)
		self._selectedTrack = index
		if index >= 0:
			self._trackFrames[index]["relief"] = ui_common.BORDERON
			return self._trackFrames[index]
		else:
			return None

class BarSelector(tkinter.Frame):

	def __init__(self, trackFrame, bars, onClick):
		super().__init__(trackFrame)
		self._trackFrame = trackFrame
		self._selectedBar = -1
		self._labels = []
		self._onClick = onClick
		for i, bar in enumerate(bars):
			self.insertBar(bar, i)

	def setBars(self, bars):
		for bar, label in zip(bars, self._labels):
			label.setBar(bar)

	def insertBar(self, bar, index):
		label = BarLabel(self, bar, index, self._trackFrame)
		label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=2, pady=2)
		label.bind("<Button-1>", lambda *x : self._onClick(self.selectBar(index)))
		self._labels.append(label)

	def selectBar(self, index):
		if index == self._selectedBar:
			return self._labels[index] if index >= 0 else None
		if self._selectedBar >= 0:
			self._labels[self._selectedBar].deselect()
		self._selectedBar = index
		if index >= 0:
			self._labels[index].select()
		return self._labels[index]

	def buildBars(self):
		bars = []
		for label in self._labels:
			bars.append(label.buildPat())
		return bars

class BarLabel(tkinter.Label):

	def __init__(self, top, bar, index, trackFrame):
		super().__init__(top, text="Bar " + str(index), width=6, bg="pink", relief=ui_common.BORDEROFF)
		self._index = index
		self._trackFrame = trackFrame
		self.rootVar = tkinter.StringVar(value=bar["root"])
		self.divsVar = tkinter.StringVar(value=bar["divs"])
		self.setRiff(bar["riff"], bar["divs"])

	def setPat(self, bar):
		self.rootVar = tkinter.StringVar(value=bar["root"])
		self.divsVar = tkinter.StringVar(value=bar["divs"])
		self.setRiff(bar["riff"], bar["divs"])

	def setRiff(self, riff, divs):
		self.riff = []
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
			self.riff.append(notes)

	def buildPat(self):
		bar = {}
		bar["root"] = int(self.rootVar.get())
		bar["divs"] = int(self.divsVar.get())
		bar["riff"] = []
		for part in self.riff:
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
			bar["riff"].append({"attacks": t, "pitches": p, "acc": a})
		return bar

	def select(self):
		self["relief"] = ui_common.BORDERON

	def deselect(self):
		self["relief"] = ui_common.BORDEROFF

	def trackIndex(self):
		return self._trackFrame.index

###############################################################################
# Quick Test
###############################################################################

if __name__ == "__main__":
	main = tkinter.Tk()
	main.menu = tkinter.Menu(main)
	main.config(menu=main.menu)
	frame = TrackGroup(main, lambda t: print("Track click"), lambda b: print("Bar click"))
	project = {"tracks": []}
	frame.loadTracks(project)
	frame.pack()
	main.mainloop()