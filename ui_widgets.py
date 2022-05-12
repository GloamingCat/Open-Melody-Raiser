import tkinter, math
from tkinter import ttk

BORDERON = "solid"
BORDEROFF = "ridge"

###############################################################################
# Common
###############################################################################

class ToggleButton(tkinter.Button):

	def __init__(self, top, names=["ON", "OFF"], values=None):
		w = max([len(name) for name in names])
		super().__init__(top, text=names[0], width=w, command=self.toggle)
		self._names = names
		if values:
			self._values = values
		else:
			self._values = range(len(names))
		self._index = 0

	def toggle(self):
		self.setIndex((self._index + 1) % len(self._values))		

	def getValue(self):
		return self._values[self._index]

	def setValue(self, value):
		self.setIndex(self._values.index(value))

	def setIndex(self, index):
		self._index = index
		self["text"] = self._names[self._index]

class ScrollableFrame(ttk.Frame):

	def __init__(self, container, scroll="both", *args, **kwargs):
		super().__init__(container, *args, **kwargs)
		self._canvas = tkinter.Canvas(self)
		self._innerFrame = ttk.Frame(self._canvas)
		self._innerFrame.bind("<Configure>", self._configInnerFrame)
		self._canvas.create_window((0, 0), window=self._innerFrame, anchor=tkinter.NW)
		scroll = scroll.lower()
		if scroll == 'y':
			self._addScrollbarY()
		elif scroll == 'x':
			self._addScrollbarX()
		else:
			self._addScrollbarY()
			self._addScrollbarX()
		self._canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

	def innerFrame(self):
		return self._innerFrame

	def _configInnerFrame(self, *v):
		self._canvas.configure(scrollregion=self._canvas.bbox("all"))

	def _addScrollbarX(self):
		scrollbar = ttk.Scrollbar(self, orient="horizontal",
			command=self._canvas.xview)
		scrollbar.pack(side="bottom", fill="x")
		self._canvas.configure(xscrollcommand=scrollbar.set)

	def _addScrollbarY(self):
		scrollbar = ttk.Scrollbar(self, orient="vertical",
			command=self._canvas.yview)
		scrollbar.pack(side="right", fill="y")
		self._canvas.configure(yscrollcommand=scrollbar.set)

###############################################################################
# Track Frame
###############################################################################

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
		super().__init__(top, text="Bar " + str(index), width=6, bg="pink", relief=BORDEROFF)
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
		self["relief"] = BORDERON

	def deselect(self):
		self["relief"] = BORDEROFF

	def trackIndex(self):
		return self._trackIndex

###############################################################################
# Bar Frame
###############################################################################

class NoteLabel(tkinter.Label):

	def __init__(self, top, note):
		super().__init__(top, width=3, borderwidth=1, relief="solid", padx=3, pady=3)
		self._note = note
		if note["mode"] == 0:
			self["text"] = "   "
		elif note["mode"] == 1:
			self["text"] = self._noteText()
		else:
			self["text"] = " - "
		self.bind("<Button-1>", lambda *x: self._step(1))
		self.bind("<Button-3>", lambda *x: self._step(-1))
		self.bind("<Shift-Button-1>", lambda *x: self._accStep(1))
		self.bind("<Shift-Button-3>", lambda *x: self._accStep(-1))
		self.bind("<Alt-Button-1>", lambda *x: self.erase())
		self.bind("<Alt-Button-3>", lambda *x: self.silence())

	def setNote(self, p, a):
		self._note["pitch"] = p
		self._note["acc"] = a
		self._note["mode"] = 1
		self["text"] = self._noteText()

	def erase(self):
		self["text"] = "   "
		self._note["mode"] = 0

	def silence(self):
		self["text"] = " - "
		self._note["mode"] = 2

	def _step(self, i):
		if self._note["mode"] == 1:
			pitch = self._note["pitch"] + i
			if pitch < 0:
				self.silence()
				return
			elif pitch <= 90:
				self._note["pitch"] = pitch
		else:
			self._note["mode"] = 1
		self["text"] = self._noteText()

	def _accStep(self, i):
		if self._note["mode"] == 1:
			self._note["acc"] = max(-2, min(self.acc + i, 2))
		else:
			self._note["mode"] = 1
		self["text"] = self._noteText()

	def _noteText(self):
		s = str(self._note["pitch"] + 1)
		a = self._note["acc"]
		if a < 0:
			s += 'b' * (-a)
		elif a > 0:
			s += '#' * a
		self["text"] = s