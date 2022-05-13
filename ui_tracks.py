import tkinter, ui_common
import pretty_midi.constants as midi
from tkinter import ttk

class TrackFrame(tkinter.LabelFrame):

	def __init__(self, window, onSelectBar=None):
		super().__init__(window, text="Tracks")
		self._trackSelector = TrackSelector(self, onSelectBar)
		self._trackSelector.pack(expand=True, fill=tkinter.BOTH)
		menu = ui_common.EditMenu(window, "track",
			delMsg="The entire selected track will be deleted",
			receiver=self, op=False, save=False)
		window.menu.add_cascade(label="Track", menu=menu)

	def loadTracks(self, project):
		self._trackSelector.setTracks(project["tracks"])

	def saveTracks(self, project):
		project["tracks"] = self._trackSelector.getTracks()

KEYS = ["vol", "rev", "pan", "cho"]
NAMES = ["Vol", "Rvrb", "Pan", "Chor"]
POS = [(2, 0, 3, 0), (4, 0, 5, 0), (2, 1, 3, 1), (4, 1, 5, 1)]
INSTS = [str(i) + ": " + midi.INSTRUMENT_MAP[i] for i in range(len(midi.INSTRUMENT_MAP))]

class TrackSelector(tkinter.Frame):

	def __init__(self, top, onSelectBar=None):
		super().__init__(top)
		self._scrollFrame = ui_common.ScrollableFrame(self)
		self._scrollFrame.pack(fill=tkinter.BOTH, expand=True)
		self._trackVars = dict()
		self._trackFrames = []
		self._selectedTrack = -1
		self._onSelectBar = onSelectBar

	def getTracks(self):
		tracks = []
		for i, selector in enumerate(self._barSelectors):
			track = {}
			track["name"] = self._trackVars["name"][i].get()
			track["inst"] = INSTS.index(self._trackVars["inst"][i].get())
			for k in KEYS:
				track[k] = int(self._trackVars[k][i].get())
			track["pats"] = selector.buildBars()
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
		self._barSelectors = []
		self._selectedTrack = -1
		self._scrollFrame.innerFrame().columnconfigure(4, weight=1)
		for track in tracks:
			frame = self.insertTrack(track)
			frame.pack(fill=tkinter.BOTH)

	def insertTrack(self, track):
		nameVar = tkinter.StringVar(value=track["name"])
		instVar = tkinter.StringVar(value=INSTS[track["inst"]])
		self._trackVars["name"].append(nameVar)
		self._trackVars["inst"].append(instVar)
		index = len(self._trackFrames)
		bg = "white" if index % 2 == 0 else "lightgrey"
		def select(*x):
			self.selectTrack(index)
		frame = tkinter.Frame(self._scrollFrame.innerFrame(), borderwidth=2, bg=bg)
		frame["relief"] = ui_common.BORDEROFF
		frame.bind("<Button-1>", select)
		# Name
		entry = tkinter.Entry(frame, textvariable=nameVar)
		entry.grid(column=0, row=index*3, sticky="ew", padx=5, pady=5)
		# Play Mode button
		button = ui_common.ToggleButton(frame, [" On ", "Mute", "Solo"])
		button.grid(column=1, row=index*3, sticky=tkinter.EW, padx=2, pady=5)
		# Instrument
		box = ttk.Combobox(frame, width=8, state='readonly', textvariable=instVar, value=instVar.get())
		box["values"] = INSTS
		box.grid(column=0, row=index*3+1, columnspan=2, sticky=tkinter.EW, padx=5, pady=5)
		# Properties
		for k, n, p in zip(KEYS, NAMES, POS):
			var = tkinter.StringVar(value=track[k])
			self._trackVars[k].append(var)
			label = tkinter.Label(frame, text=n + ":", bg=bg)
			label.bind("<Button-1>", select)
			label.grid(column=p[0], row=p[1]+index*3, sticky=tkinter.W, padx=2, pady=2)
			box = ttk.Spinbox(frame, from_=1, to=127, width=4, textvariable=var)
			box.grid(column=p[2], row=p[3]+index*3, sticky=tkinter.EW, padx=2, pady=2)
		# Bar list
		barFrame = BarSelector(frame, index, track["pats"], self.selectBarLabel)
		barFrame.grid(column=6, row=index*3, padx=2, pady=2, rowspan=3, sticky=tkinter.NSEW)
		self._trackFrames.append(frame)
		self._barSelectors.append(barFrame)
		return frame

	def selectBarLabel(self, barLabel):
		self.selectTrack(barLabel.trackIndex())
		if self._onSelectBar:
			self._onSelectBar(barLabel)

	def selectTrack(self, index):
		if index == self._selectedTrack:
			return
		if self._selectedTrack >= 0:
			self._trackFrames[self._selectedTrack]["relief"] = ui_common.BORDEROFF
			self._barSelectors[self._selectedTrack].selectBar(-1)
		self._selectedTrack = index
		if index >= 0:
			self._trackFrames[index]["relief"] = ui_common.BORDERON

class BarSelector(tkinter.Frame):

	def __init__(self, top, index, bars, onClick):
		super().__init__(top)
		self._trackIndex = index
		self._selectedBar = -1
		self._labels = []
		self._onClick = onClick
		for i in range(len(bars)):
			self.addBar(bars[i], i)

	def addBar(self, bar, index):
		label = BarLabel(self, bar, index, self._trackIndex)
		label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=2, pady=2)
		label.bind("<Button-1>", lambda *x : self._onClick(self.selectBar(index)))
		self._labels.append(label)

	def selectBar(self, index):
		if index == self._selectedBar:
			return self._labels[index]
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

	def __init__(self, top, bar, index, trackIndex):
		super().__init__(top, text="Bar " + str(index), width=6, bg="pink", relief=ui_common.BORDEROFF)
		self._index = index
		self._trackIndex = trackIndex
		self.rootVar = tkinter.StringVar(value=bar["root"])
		self.divsVar = tkinter.StringVar(value=bar["divs"])
		self.riff = []
		for part in bar["riff"]:
			notes = []
			for j in range(bar["divs"]):
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
		return self._trackIndex

###############################################################################
# Quick Test
###############################################################################

if __name__ == "__main__":
	main = tkinter.Tk()
	main.menu = tkinter.Menu(main)
	main.config(menu=main.menu)
	frame = TrackFrame(main)
	frame.pack()
	main.mainloop()