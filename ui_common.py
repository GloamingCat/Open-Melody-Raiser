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

###############################################################################
# Menu
###############################################################################

class EditMenu(tkinter.Menu):

	def __init__(self, window, typeName, receiver=None, 
			delMsg=None, move=True, op=True, save=True, replace=True,
			generate=True):
		super().__init__(window, tearoff=False)
		self.window = window
		self.receiver = receiver
		addMenu = tkinter.Menu(self, tearoff=False)
		self.add_cascade(label="Add "+typeName, menu=addMenu)
		addMenu.add_command(label="Empty", command=self.onAddNew)
		addMenu.add_command(label="Duplicate", command=self.onDuplicate)
		if generate:
			addMenu.add_command(label="Generate...", command=self.onGenerateNew)
		if replace:
			replaceMenu = tkinter.Menu(self, tearoff=False)
			self.add_cascade(label="Replace", menu=replaceMenu)
			replaceMenu.add_command(label="Preset...", command=self.onPreset)
			replaceMenu.add_command(label="Preset (file)...", command=self.onPresetFile)
			if generate:
				replaceMenu.add_command(label="Generate...", command=self.onGenerate)
			replaceMenu.add_command(label="Clear", command=self.onClear)
		if move:
			self.add_command(label="Move Up", command=self.onMoveUp)
			self.add_command(label="Move Down", command=self.onMoveDown)
		if delMsg:
			self.add_command(label="Delete "+typeName, command=self.onDelete)
		if save:
			self.add_command(label="Save preset...", command=self.onSave)
		self.typeName = typeName
		self.delMsg = delMsg

	###########################################################################
	# Insert
	###########################################################################

	def onAddNew(self):
		self.receiver.insert(None)

	def onDuplicate(self):
		obj = self.receiver.buildSelected()
		self.receiver.insert(obj)

	def onGenerateNew(self):
		dialog = self.receiver.openGenerateDialog(self.window)
		if dialog.result:
			obj = self.receiver.generateNew(dialog.result)
			self.receiver.insert(obj)

	###########################################################################
	# Replace
	###########################################################################

	def onPreset(self):
		if receiver.barPresets:
			# obj = ui_dialog.BarPresetDialog(self.window)
			obj = {}
		else:
			# obj = ui_dialog.PartPresetDialog(self.window)
			obj = {}
		self.receiver.replace(obj)

	def onPresetFile(self):
		title='Open a part preset'
		filetypes = [('Part presets', '*.part')]
		if receiver.barPresets:
			filetypes.append(('Bar presets', '*.bar'))
			title = title.replace('part', 'part or bar')
		filename = tkinter.filedialog.askopenfilename(
			title=title,
	        initialdir='./presets/',
	        filetypes=filetypes)
		if filename and filename != '':
			obj = core_project.loadPreset(filename)
			self.receiver.replace(obj)

	def onGenerate(self):
		dialog = self.receiver.openGenerateDialog(self.window)
		if dialog.result:
			obj = self.receiver.replace(dialog.result)

	def onClear(self):
		self.receiver.replace(None)

	###########################################################################
	# Move / Delete
	###########################################################################

	def onMoveUp(self):
		self.receiver.moveUp()

	def onMoveDown(self):
		self.receiver.moveDown()

	def onDelete(self):
		result = tkinter.messagebox.askyesno(
			title="Delete "+self.typeName, 
			message=self.delMsg+". You can't undo this action. "+
			"Do you want to continue?")
		if result == tkinter.YES:
			self.receiver.delete()

	###########################################################################
	# Save
	###########################################################################

	def onSave(self):
		title='Open a part preset'
		filetypes = [('Part presets', '*.part')]
		if receiver.barPresets:
			filetypes.append(('Bar presets', '*.bar'))
			title = title.replace('part', 'part or bar')
		filename = tkinter.filedialog.asksaveasfilename(
			title=title,
	        initialdir='./presets/',
	        filetypes=filetypes)
		if filename and filename != '':
			obj = core_project.loadPreset(filename)
			self.receiver.replace(obj)