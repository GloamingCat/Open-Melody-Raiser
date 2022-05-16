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
			self._divsLabel["text"] = barLabel.divsVar.get()
			self._rootBox.configure(textvariable=barLabel.rootVar)
			self._rootBox["value"] = barLabel.rootVar.get()
			self._partSelector.setRiff(barLabel.riff)
		else:
			self._divsLabel.configure(textvariable=None)
			self._divsLabel["text"] = ""
			self._rootBox.configure(textvariable=None)
			self._rootBox["value"] = ""
			self._partSelector.setRiff([])

class PartSelector(tkinter.Frame):

	def __init__(self, top, onPartClick):
		super().__init__(top)
		self._selectedPart = -1
		self._partFrames = []
		self._onClick = onPartClick

	def setRiff(self, riff):
		for part in self._partFrames:
			part.destroy()
		self._partFrames = []
		for i, part in enumerate(riff):
			self.insertPart(i, part)

	def insertPart(self, i, notes):
		def select(e):
			self.selectPart(i)
		frame = tkinter.Frame(self, borderwidth=2, relief=ui_common.BORDEROFF)
		frame.bind("<Button-1>", select)
		frame.bind("<Button-3>", select)
		label = tkinter.Label(frame, width=5)
		label.pack(side=tkinter.LEFT)
		label.bind("<Button-1>", select)
		label.bind("<Button-3>", select)
		for j, note in enumerate(notes):
			label = NoteLabel(frame, self, note, i)
			label["bg"] = "white" if i % 2 == 0 else "lightgrey"
			label.pack(side=tkinter.LEFT, padx=2, pady=2)
		self._partFrames.append(frame)
		frame.pack(side=tkinter.TOP)

	def selectPart(self, index):
		if self._selectedPart >= 0:
			self._partFrames[self._selectedPart]["relief"] = ui_common.BORDEROFF
		self._selectedPart = index
		if index >= 0:
			self._partFrames[index]["relief"] = ui_common.BORDERON

	def isSelected(self, index):
		return self._selectedPart == index

class NoteLabel(tkinter.Label):

	def __init__(self, top, frame, note, i):
		super().__init__(top, width=3, borderwidth=1, relief="solid", padx=3, pady=3)
		self._note = note
		if note["mode"] == 0:
			self["text"] = "   "
		elif note["mode"] == 1:
			self["text"] = self._noteText()
		else:
			self["text"] = " - "
		self.bind("<Button-1>", lambda *x: (self._step(1), frame.selectPart(i)))
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