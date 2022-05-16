import tkinter, core_project
from tkinter import ttk

BORDERON = "solid"
BORDEROFF = "ridge"

###############################################################################
# Widget
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

###############################################################################
# Frame
###############################################################################

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