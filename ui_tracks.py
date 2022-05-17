import tkinter, ui_common, core_util
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

class TrackSelector(ui_common.SelectionFrame):

	def __init__(self, top, onTrackClick, onBarClick):
		super().__init__(top)
		self._scrollFrame = ui_common.ScrollableFrame(self)
		self._scrollFrame.pack(fill=tkinter.BOTH, expand=True)
		self._scrollFrame.innerFrame().columnconfigure(4, weight=1)
		self._trackVars = dict()
		self._onBarClick = onBarClick
		self._onTrackClick = onTrackClick

	def _repackItems(self):
		for i, frame in enumerate(self._items):
			frame.index = i
			frame.grid(column=0, row=i, sticky=tkinter.EW)
			bg = "white" if i % 2 == 0 else "lightgrey"
			frame.configure(bg=bg)
			for child in frame.configLabels:
				child.configure(bg=bg)

	def getTracks(self):
		tracks = []
		for i, frame in enumerate(self._items):
			tracks.append(self.buildItem(i))
		return tracks

	def setTracks(self, tracks):
		for k in KEYS:
			self._trackVars[k] = []
		self._trackVars["name"] = []
		self._trackVars["inst"] = []
		self._setData(tracks)
		self._repackItems()

	def _newItem(self): # Override
		return tkinter.Frame(self._scrollFrame.innerFrame(), borderwidth=2)

	def _setupItem(self, frame, track, index): # Override
		super()._setupItem(frame, track, index)
		bg = "white" if index % 2 == 0 else "lightgrey"
		frame["bg"] = bg
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
		frame.configLabels = []
		for k, n, p in zip(KEYS, NAMES, POS):
			var = tkinter.StringVar(value=track[k] if track else 64)
			self._trackVars[k].append(var)
			label = tkinter.Label(frame, text=n + ":", bg=bg)
			label.bind("<Button-1>", frame.onSelect)
			label.bind("<Button-3>", frame.onSelect)
			label.grid(column=p[0], row=p[1], sticky=tkinter.W, padx=2, pady=2)
			box = ttk.Spinbox(frame, from_=1, to=127, width=4, textvariable=var)
			box.grid(column=p[2], row=p[3], sticky=tkinter.EW, padx=2, pady=2)
			frame.configLabels.append(label)
		def onSelectBar(b):
			self._onTrackClick(self.selectItem(frame.index))
			self._onBarClick(b)
		frame.barSelector = BarSelector(frame, track["pats"] if track else [], onSelectBar)
		frame.barSelector.grid(column=6, row=0, padx=2, pady=2, rowspan=3, sticky=tkinter.NSEW)

	def _onSelect(self, e): # Override
		super()._onSelect(e)
		self._onTrackClick(e.item)
		self._onBarClick(None)

	def selectItem(self, index): # Override
		if self._current >= 0 and self._current != index:
			self._items[self._current].barSelector.selectItem(-1)
		return super().selectItem(index)

	def replaceItem(self, obj, index=None): # Override
		index = index or self._current
		if obj:
			self._trackVars["name"][index].set(obj["name"])
			self._trackVars["inst"][index].set(INSTS[int(obj["inst"])])
			for k in KEYS:
				self._trackVars[k][index].set(obj[k])
			self._items[index].barSelector.setPats(obj["pats"])
		else:
			self._trackVars["name"][index].set("New Track")
			self._trackVars["inst"][index].set(INSTS[0])
			for k in KEYS:
				self._trackVars[k][index].set(64)
			self._items[index].barSelector.setPats([])

	def buildItem(self, index=None):
		index = index or self._current
		track = {}
		track["name"] = self._trackVars["name"][index].get()
		track["inst"] = INSTS.index(self._trackVars["inst"][index].get())
		for k in KEYS:
			track[k] = int(self._trackVars[k][index].get())
		track["pats"] = self._items[index].barSelector.getPats()
		return track

###############################################################################
# Bar Labels
###############################################################################

class BarSelector(ui_common.SelectionFrame):

	def __init__(self, top, bars, onClick):
		super().__init__(top)
		self._onClick = onClick
		self.setPats(bars)
		self.rowconfigure(0, weight=1)

	def getPats(self):
		bars = []
		for label in self._items:
			bars.append(label.getPat())
		return bars

	def setPats(self, pats):
		self._setData(pats)
		self._repackItems()

	def _repackItems(self): # Override
		for i, label in enumerate(self._items):
			label.setIndex(i)
			label.grid(column=i, row=0, sticky=tkinter.NSEW, padx=2, pady=2)

	def _newItem(self): # Override
		return BarLabel(self, self)

	def _setupItem(self, label, bar, index): # Overidde
		super()._setupItem(label, bar, index)
		label.setPat(bar)

	def _onSelect(self, e): # Override
		super()._onSelect(e)
		self._onClick(e.item)

	def buildItem(self, index=None):
		return self._items[index].getPat()

class BarLabel(tkinter.Label):

	def __init__(self, top, selector):
		super().__init__(top, width=6, bg="pink")
		self.selector = selector

	def setIndex(self, index):
		self._index = index
		self["text"] = "Bar " + str(index)

	def setPat(self, bar):
		self.rootVar = tkinter.StringVar(value=bar["root"])
		self.divsVar = tkinter.StringVar(value=bar["divs"])
		self.riff = core_util.convertRiffToUI(bar["riff"], bar["divs"])

	def getPat(self):
		bar = {}
		bar["root"] = int(self.rootVar.get())
		bar["divs"] = int(self.divsVar.get())
		bar["riff"] = core_util.convertRiffToProject(self.riff)
		return bar

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