import tkinter, ui_common
from tkinter import ttk

class BarGroup(tkinter.LabelFrame):

	def __init__(self, window, onPartClick=None):
		super().__init__(window, text="Bar Composer")
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
		self._scrollFrame = ui_common.ScrollableFrame(self)
		self._scrollFrame.grid(column=0, row=1, columnspan=6, sticky=tkinter.NSEW)
		tkinter.Label(self).grid(column=5, row=0)
		self._partSelector = PartSelector(self._scrollFrame.innerFrame(), onPartClick)
		self._partSelector.pack(expand=True, fill='both')

	def loadBar(self, barLabel):
		if barLabel:
			self._divsLabel.configure(textvariable=barLabel.divsVar)
			self._rootBox.configure(textvariable=barLabel.rootVar)
			self._partSelector.setRiff(barLabel.riff)
		else:
			var = tkinter.StringVar(value="")
			self._divsLabel.configure(textvariable=var)
			self._rootBox.configure(textvariable=var)
			self._partSelector.setRiff([])

class PartSelector(ui_common.SelectionFrame):

	def __init__(self, top, onPartClick):
		super().__init__(top)
		self._onClick = onPartClick

	def setRiff(self, riff):
		self._setData(riff)
		self._repackItems()

	def _setupItem(self, frame, notes, index): # Override
		super()._setupItem(frame, notes, index)
		label = tkinter.Label(frame, width=5)
		label.pack(side=tkinter.LEFT)
		label.bind("<Button-1>", frame.onSelect)
		label.bind("<Button-3>", frame.onSelect)
		frame.noteLabels = []
		for j, note in enumerate(notes):
			label = NoteLabel(frame, note, frame.onSelect)
			label["bg"] = "white" if index % 2 == 0 else "lightgrey"
			label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=2, pady=2)
			frame.noteLabels.append(label)
		frame.pack(side=tkinter.TOP)

	def replaceItem(self, obj, index=None): # Override
		index = index or self._current
		frame = self._items[index]
		for note, label in zip(notes, frame.noteLabels):
			label.setNote(note["pitch"], note["acc"], note["mode"])

	def _onSelect(self, e):
		self._onClick(e.item)

class NoteLabel(tkinter.Label):

	def __init__(self, top, note, onClick):
		super().__init__(top, width=3, borderwidth=1, relief="solid", padx=3, pady=3)
		self._note = note
		if note["mode"] == 0:
			self["text"] = "   "
		elif note["mode"] == 1:
			self["text"] = self._noteText()
		else:
			self["text"] = " - "
		self.bind("<Button-1>", lambda e: (self._step(1), onClick(e)))
		self.bind("<Button-3>", lambda e: (self._step(-1), onClick(e)))
		self.bind("<Shift-Button-1>", lambda *x: self._accStep(1))
		self.bind("<Shift-Button-3>", lambda *x: self._accStep(-1))
		self.bind("<Alt-Button-1>", lambda *x: self.erase())
		self.bind("<Alt-Button-3>", lambda *x: self.silence())

	def setNote(self, p, a, m=1):
		self._note["pitch"] = p
		self._note["acc"] = a
		self._note["mode"] = m
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

###############################################################################
# Quick Test
###############################################################################

if __name__ == "__main__":
	main = tkinter.Tk()
	main.menu = tkinter.Menu(main)
	main.config(menu=main.menu)
	frame = BarGroup(main)
	frame.pack()
	main.mainloop()