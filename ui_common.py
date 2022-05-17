import tkinter
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

class SelectionFrame(ttk.Frame):

	def __init__(self, top, *args, **kwargs):
		super().__init__(top, *args, **kwargs)
		self._current = -1
		self._items = []

	def _setData(self, data):
		self._clearItems()
		for i, d in enumerate(data):
			item = self._newItem()
			self._items.append(item)
			self._setupItem(item, d, i)

	def _clearItems(self):
		for item in self._items:
			item.destroy()
		self._items = []

	def _repackItems(self):
		for i, item in enumerate(self._items):
			item.index = i
			item.pack(side=tkinter.TOP, fill=tkinter.BOTH)

	def _newItem(self):
		return tkinter.Frame(self, borderwidth=2)

	def _setupItem(self, item, data, index):
		item.index = index
		def onSelect(e):
			e.previous = self._items[self._current] if self._current >= 0 else None
			e.item = self.selectItem(item.index)
			e.index = item.index
			self._onSelect(e)
		item["relief"] = BORDEROFF
		item.bind("<Button-1>", onSelect)
		item.bind("<Button-3>", onSelect)
		item.onSelect = onSelect

	def selectItem(self, index):
		if index == self._current:
			return self._items[index] if index >= 0 else None
		if self._current >= 0:
			self._items[self._current]["relief"] = BORDEROFF
		self._current = index
		if index >= 0:
			self._items[index]["relief"] = BORDERON
			return self._items[index]
		else:
			return None

	def selectedIndex(self):
		return self._current

	def _onSelect(self, event):
		pass

	def insertItem(self, data, index=None):
		index = index or self._current
		self.selectItem(-1)
		item = self._newItem()
		if index == -1:
			index = len(self._items)
			self._items.append(item)
		else:
			index += 1
			self._items.insert(index, item)
		self._setupItem(item, data, index)
		self._repackItems()
		self._items[index].event_generate("<Button-1>")
		return item

	def moveItem(self, pos, index=None):
		index = index or self._current
		aux = index + pos
		if aux >= 0 and aux < len(self._items):
			x, y = self._items[self._current], self._items[aux]
			self._items[self._current], self._items[aux] = y, x
			self._repackItems()
			self._items[index].event_generate("<Button-1>")

	def deleteItem(self, index=None):
		index = index or self._current
		self._items.pop(index).destroy()
		if index >= len(self._items):
			index -= 1
		print(index, self._current)
		self._current = -1
		self._repackItems()
		self._items[index].event_generate("<Button-1>")

	def replaceItem(self, data, index=None):
		index = index or self._current
		self._setupItem(self._items[index], data, index)