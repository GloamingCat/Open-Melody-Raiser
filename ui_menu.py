import tkinter
from tkinter import ttk

class CommonMenu(tkinter.Menu):

	def __init__(self, window, typeName,
			presets=[], delMsg=None,
			generationDialog=None, presetDialog=None,
			move=True, replace=True):
		super().__init__(window, tearoff=False)
		self.window = window
		self.addMenu = tkinter.Menu(self, tearoff=False)
		self.add_cascade(label="Add "+typeName, menu=self.addMenu)
		self.addMenu.add_command(label="Empty", command=self.onAddNew)
		self.addMenu.add_command(label="Duplicate", command=self.onDuplicate)
		if generationDialog:
			self.addMenu.add_command(label="Generate...", command=self.onGenerateNew)
		if replace:
			replaceMenu = tkinter.Menu(self, tearoff=False)
			self.add_cascade(label="Replace", menu=replaceMenu)
			if presetDialog:
				replaceMenu.add_command(label="Preset...", command=self.onPreset)
			if len(presets) > 0:
				replaceMenu.add_command(label="Preset (file)...", command=self.onPresetFile)
			if generationDialog:
				replaceMenu.add_command(label="Generate...", command=self.onGenerate)
			replaceMenu.add_command(label="Clear", command=self.onClear)
		if move:
			self.add_command(label="Move Up", command=self.onMoveUp)
			self.add_command(label="Move Down", command=self.onMoveDown)
		if delMsg:
			self.add_command(label="Delete "+typeName, command=self.onDelete)
		if len(presets) > 0:
			self.add_separator()
			self.add_command(label="Save preset...", command=self.onSave)
		self._delMsg = delMsg
		self._presets = presets
		self._typeName = typeName
		self._generationDialog = generationDialog
		self._presetDialog = presetDialog
		self.onDeselect()

	def onSelect(self, value=True):
		self._setState("normal" if value else "disabled")

	def onDeselect(self):
		self._setState("disabled")

	def _setState(self, state):
		for n in ["Replace", "Move Up", "Move Down", "Delete "+self._typeName, "Save preset..."]:
			try:
				self.entryconfig(n, state=state)
			except tkinter.TclError:
				pass
		self.addMenu.entryconfig("Duplicate", state=state)

	###########################################################################
	# Insert
	###########################################################################

	def onAddNew(self):
		self.insert(None)

	def onDuplicate(self):
		obj = self.buildSelected()
		self.insert(obj)

	def onGenerateNew(self):
		dialog = self._generationDialog(self.window)
		if dialog.result:
			self.insert(dialog.result)

	###########################################################################
	# Replace
	###########################################################################

	def onPreset(self):
		dialog = self._presetDialog(self.window)
		if dialog and dialog.result:
			self.replace(dialog.result)

	def onPresetFile(self):
		title='Open a %s preset' % (' or '.join(self._presets))
		filetypes = [(t + ' presets', '*.' + t.lower()) for t in self._presets]
		filename = tkinter.filedialog.askopenfilename(
			title=title,
	        initialdir='./presets/',
	        filetypes=filetypes)
		if filename and filename != '':
			obj = core_project.loadPreset(filename)
			self.replace(obj)

	def onGenerate(self):
		dialog = self._generationDialog(self.window)
		if dialog and dialog.result:
			self.replace(dialog.result)

	def onClear(self):
		self.replace(None)

	###########################################################################
	# Move / Delete
	###########################################################################

	def onMoveUp(self):
		self.move(-1)

	def onMoveDown(self):
		self.move(1)

	def onDelete(self):
		result = tkinter.messagebox.askyesno(
			title="Delete "+self._typeName, 
			message=self._delMsg+". You can't undo this action. "+
			"Do you want to continue?")
		if result == tkinter.YES:
			self.delete()

	###########################################################################
	# Save
	###########################################################################

	def onSave(self):
		title='Open a %s preset' % self._presets[0].lower()
		filetypes = [(self._presets[0] + ' preset', '*.' + self._presets[0].lower())]
		filename = tkinter.filedialog.asksaveasfilename(
			title=title,
	        initialdir='./presets/',
	        filetypes=filetypes)
		if filename and filename != '':
			obj = self.buildSelected()
			core_project.savePreset(obj, filename)

	###########################################################################
	# Callbacks
	###########################################################################

	def buildSelected(self):
		print("Build")
		return None

	def insert(self, obj):
		print("Insert " + str(obj))

	def replace(self, obj):
		print("Replace " + str(obj))

	def move(self, i):
		print("Move " + str(i))

	def delete(self):
		print("Delete")

###############################################################################
# Track
###############################################################################

class TrackMenu(CommonMenu):

	def __init__(self, window, trackGroup):
		super().__init__(window, "track",
			delMsg="The entire selected track will be deleted")
		self._trackSelector = trackGroup._trackSelector

	def buildSelected(self):
		return self._trackSelector.getTracks()

	def insert(self, obj):
		self._trackSelector.insertTrack(obj)
		self._trackSelector.repackFrames()

	def replace(self, obj):
		self._trackSelector.replaceTrack(obj)

	def move(self, i):
		self._trackSelector.moveTrack(i)
		self._trackSelector.repackFrames()

	def delete(self):
		self._trackSelector.deleteTrack()
		self._trackSelector.repackFrames()

###############################################################################
# Bar
###############################################################################

class BarMenu(CommonMenu):

	def __init__(self, window, barGroup, trackGroup):
		super().__init__(window, "bar",
			delMsg="All bars in the time stamp of the selected bar will "+
			"be deleted and all tracks will be shortened by 1 bar",
			move=False, presets=["Bar", "Part"])

###############################################################################
# Part
###############################################################################

class PartMenu(CommonMenu):

	def __init__(self, window, barGroup, trackGroup):
		super().__init__(window, "part",
			delMsg="The selected part of the selected bar will be deleted",
			presets=["Part"])