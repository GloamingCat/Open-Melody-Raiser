import tkinter, math, ui_widgets
import pretty_midi.utilities as util
import pretty_midi.constants as midi
from tkinter import ttk, simpledialog

class SignatureFrame(tkinter.LabelFrame):

	singleton = None

	def __init__(self, top):
		super().__init__(top, text="Signature")
		SignatureFrame.singleton = self
		self.columnconfigure(1, weight=2)
		self.columnconfigure(3, weight=1)
		self.columnconfigure(5, weight=1)
		self.columnconfigure(6, weight=2)
		self.bpmVar = tkinter.StringVar()
		self.timeVar = tkinter.StringVar()
		self.octVar = tkinter.StringVar()
		self.scaleVar = tkinter.StringVar()
		# BPM
		label = tkinter.Label(self, text="BPM:")
		label.grid(column=0, row=0, sticky=tkinter.W, padx=2, pady=5)
		box = ttk.Spinbox(self, from_=1, to=127, width=8, textvariable=self.bpmVar)
		box.grid(column=1, row=0, sticky=tkinter.EW, padx=5, pady=5)
		# Tempo
		label = tkinter.Label(self, text="Tempo:")
		label.grid(column=2, row=0, sticky=tkinter.W, padx=2, pady=5)
		self.timeBox = ttk.Combobox(self, width=8, state='readonly', textvariable=self.timeVar)
		self.timeBox['values'] = ["4/4", "3/4", "2/4", "5/4"]
		self.timeBox.current(0)
		self.timeBox.grid(column=3, row=0, sticky=tkinter.EW, padx=5, pady=5)
		# Scale
		label = tkinter.Label(self, text="Key:")
		label.grid(column=4, row=0, sticky=tkinter.W, padx=2, pady=5)
		self.scaleBox = ttk.Combobox(self, width=5, state='readonly', textvariable=self.scaleVar)
		self.scaleBox['values'] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
		self.scaleBox.current(0)
		self.scaleBox.grid(column=5, row=0, sticky=tkinter.EW, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=9, width=5, textvariable = self.octVar)
		box.grid(column=6, row=0, sticky=tkinter.EW, padx=2, pady=2)
		# Mode
		self.modeButton = ui_widgets.ToggleButton(self, ["Major", "Minor"], [0, 5])
		self.modeButton.grid(column=7, row=0, sticky=tkinter.EW, padx=5, pady=5)

	def loadSignature(self, project):
		self.bpmVar.set(project["bpm"])
		if project["timesig"][0] == 3:
			self.timeBox.current(1)
		elif project["timesig"][0] == 2:
			self.timeBox.current(2)
		elif project["timesig"][0] == 5:
			self.timeBox.current(3)
		else:
			self.timeBox.current(0)
		self.scaleBox.current(project["keysig"][0] % 12)
		self.octVar.set(int(project["keysig"][0] / 12))
		self.modeButton.setValue(project["keysig"][1])

	def saveSignature(self, project):
		root = int(self.scaleBox.current()) + int(self.octVar.get()) * 12
		mode = self.modeButton.getValue()
		project["keysig"] = [root, mode]
		project["timesig"] = [int(i) for i in self.timeVar.get().split('/')]
		project["bpm"] = int(self.bpmVar.get())

class TrackFrame(tkinter.LabelFrame):

	KEYS = ["vol", "rev", "pan", "cho"]
	NAMES = ["Vol", "Rvrb", "Pan", "Chor"]
	POS = [(2, 0, 3, 0), (4, 0, 5, 0), (2, 1, 3, 1), (4, 1, 5, 1)]
	INSTS = [str(i) + ": " + midi.INSTRUMENT_MAP[i] for i in range(len(midi.INSTRUMENT_MAP))]

	singleton = None

	def __init__(self, top):
		super().__init__(top, text="Tracks")
		TrackFrame.singleton = self
		self._scrollFrame = ui_widgets.ScrollableFrame(self)
		self._scrollFrame.pack(fill=tkinter.BOTH, expand=True)
		self._trackVars = dict()
		self._trackFrames = []
		self._selectedTrack = -1

	def loadTracks(self, project):
		for k in TrackFrame.KEYS:
			self._trackVars[k] = []
		self._trackVars["name"] = []
		self._trackVars["inst"] = []
		for frame in self._trackFrames:
			frame.destroy()
		self._trackFrames = []
		self._barSelectors = []
		self._selectedTrack = -1
		self._scrollFrame.innerFrame().columnconfigure(4, weight=1)
		for track in project["tracks"]:
			self.insertTrack(track)
		self._scrollFrame.pack()

	def insertTrack(self, track):
		nameVar = tkinter.StringVar(value=track["name"])
		instVar = tkinter.StringVar(value=TrackFrame.INSTS[track["inst"]])
		self._trackVars["name"].append(nameVar)
		self._trackVars["inst"].append(instVar)
		index = len(self._trackFrames)
		bg = "white" if index % 2 == 0 else "lightgrey"
		def select(*x):
			self.selectTrack(index)
		frame = tkinter.Frame(self._scrollFrame.innerFrame(), borderwidth=2, bg=bg)
		frame["relief"] = ui_widgets.BORDEROFF
		frame.bind("<Button-1>", select)
		# Name
		entry = tkinter.Entry(frame, textvariable=nameVar)
		entry.grid(column=0, row=index*3, sticky="ew", padx=5, pady=5)
		# Play Mode button
		button = ui_widgets.ToggleButton(frame, [" On ", "Mute", "Solo"])
		button.grid(column=1, row=index*3, sticky=tkinter.EW, padx=2, pady=5)
		# Instrument
		box = ttk.Combobox(frame, width=8, state='readonly', textvariable=instVar, value=instVar.get())
		box["values"] = TrackFrame.INSTS
		box.grid(column=0, row=index*3+1, columnspan=2, sticky=tkinter.EW, padx=5, pady=5)
		# Properties
		for k, n, p in zip(TrackFrame.KEYS, TrackFrame.NAMES, TrackFrame.POS):
			var = tkinter.StringVar(value=track[k])
			self._trackVars[k].append(var)
			label = tkinter.Label(frame, text=n + ":", bg=bg)
			label.bind("<Button-1>", select)
			label.grid(column=p[0], row=p[1]+index*3, sticky=tkinter.W, padx=2, pady=2)
			box = ttk.Spinbox(frame, from_=1, to=127, width=4, textvariable=var)
			box.grid(column=p[2], row=p[3]+index*3, sticky=tkinter.EW, padx=2, pady=2)
		# Bar list
		barFrame = ui_widgets.BarSelector(frame, index, track["pats"], self.selectBarLabel)
		barFrame.grid(column=6, row=index*3, padx=2, pady=2, rowspan=3, sticky=tkinter.NSEW)
		frame.pack(fill=tkinter.BOTH)
		self._trackFrames.append(frame)
		self._barSelectors.append(barFrame)

	def selectBarLabel(self, barLabel):
		self.selectTrack(barLabel.trackIndex())
		BarFrame.singleton.loadBar(barLabel)

	def selectTrack(self, index):
		if index == self._selectedTrack:
			return
		if self._selectedTrack >= 0:
			self._trackFrames[self._selectedTrack]["relief"] = ui_widgets.BORDEROFF
			self._barSelectors[self._selectedTrack].selectBar(-1)
		self._selectedTrack = index
		if index >= 0:
			self._trackFrames[index]["relief"] = ui_widgets.BORDERON

	def saveTracks(self, project):
		tracks = []
		for i, selector in enumerate(self._barSelectors):
			track = {}
			track["name"] = self._trackVars["name"][i].get()
			track["inst"] = TrackFrame.INSTS.index(self._trackVars["inst"][i].get())
			for k in TrackFrame.KEYS:
				track[k] = int(self._trackVars[k][i].get())
			track["pats"] = selector.buildBars()
			tracks.append(track)
		project["tracks"] = tracks

class BarFrame(tkinter.LabelFrame):

	singleton = None

	def __init__(self, top):
		super().__init__(top, text="Bar Composer")
		BarFrame.singleton = self
		self.columnconfigure(5, weight=1)
		self.rowconfigure(1, weight=1)
		# Root
		label = tkinter.Label(self, text="Root:")
		label.grid(column=0, row=0, padx=2, pady=2)
		self._rootBox = ttk.Spinbox(self, from_=1, to=90, width=4)
		self._rootBox.grid(column=1, row=0, padx=2, pady=2)
		# Divisions
		label = tkinter.Label(self, text="Divs:")
		label.grid(column=2, row=0, padx=2, pady=2)
		self._divsLabel = tkinter.Label(self, width=4)
		self._divsLabel.grid(column=3, row=0, padx=2, pady=2)
		# Riff editor
		self._scrollFrame = ui_widgets.ScrollableFrame(self)
		self._scrollFrame.grid(column=0, row=1, columnspan=6, sticky=tkinter.NSEW)
		tkinter.Label(self).grid(column=5, row=0)
		self.partSelector = ui_widgets.PartSelector(self._scrollFrame.innerFrame())
		self.partSelector.pack(expand=True, fill='both')

	def loadBar(self, barLabel):
		self._divsLabel.configure(textvariable=barLabel.divsVar)
		self._divsLabel["text"] = barLabel.divsVar.get()
		self._rootBox.configure(textvariable=barLabel.rootVar)
		self._rootBox["value"] = barLabel.rootVar.get()
		self.partSelector.setRiff(barLabel.riff)