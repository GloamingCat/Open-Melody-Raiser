import tkinter, ui_creation
from tkinter import ttk

class CommonMenu(tkinter.Menu):

	def __init__(self, window, typeName,
			presets=[], delMsg=None, receiver=None,
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
		self._receiver = receiver
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
		self._receiver.insertItem(None)

	def onDuplicate(self):
		obj = self._receiver.buildItem()
		self._receiver.insertItem(obj)

	def onGenerateNew(self):
		dialog = self._generationDialog(self.window,
			title="Generate new %s " % self._typeName)
		if dialog.result:
			self._receiver.insertItem(dialog.result)

	###########################################################################
	# Replace
	###########################################################################

	def onPreset(self):
		dialog = self._presetDialog(self.window,
			title="Create %s preset" % self._typeName)
		if dialog and dialog.result:
			self._receiver.replaceItem(dialog.result)

	def onPresetFile(self):
		title='Open a %s preset' % (' or '.join(self._presets))
		filetypes = [(t + ' presets', '*.' + t.lower()) for t in self._presets]
		filename = tkinter.filedialog.askopenfilename(
			title=title,
	        initialdir='./presets/',
	        filetypes=filetypes)
		if filename and filename != '':
			obj = core_project.loadPreset(filename)
			self._receiver.replaceItem(obj)

	def onGenerate(self):
		dialog = self._generationDialog(self.window,
			title="Generate new %s " % self._typeName)
		if dialog and dialog.result:
			self._receiver.replaceItem(dialog.result)

	def onClear(self):
		self._receiver.replaceItem(None)

	###########################################################################
	# Move / Delete
	###########################################################################

	def onMoveUp(self):
		self._receiver.moveItem(-1)

	def onMoveDown(self):
		self._receiver.moveItem(1)

	def onDelete(self):
		result = tkinter.messagebox.askyesno(
			title="Delete "+self._typeName, 
			message=self._delMsg+". You can't undo this action. "+
			"Do you want to continue?")
		if result == tkinter.YES:
			self._receiver.deleteItem()

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
			obj = self._receiver.buildItem()
			core_project.savePreset(obj, filename)

###############################################################################
# Group Menu
###############################################################################

class TrackMenu(CommonMenu):

	def __init__(self, window, trackGroup):
		super().__init__(window, "track", receiver=trackGroup._trackSelector,
			generationDialog=ui_creation.NewTrackDialog,
			delMsg="The entire selected track will be deleted")
		trackGroup._trackSelector._menu = self

class BarMenu(CommonMenu):

	def __init__(self, window, barGroup, trackGroup):
		super().__init__(window, "bar", receiver=barGroup,
			generationDialog=ui_creation.NewBarDialog,
			presetDialog=ui_creation.BarPresetDialog,
			delMsg="All bars in the time stamp of the selected bar will "+
			"be deleted and all tracks will be shortened by 1 bar",
			move=False, presets=["Bar", "Part"])
		trackGroup._trackSelector._barMenu = self

class PartMenu(CommonMenu):

	def __init__(self, window, barGroup):
		super().__init__(window, "part", receiver=barGroup._partSelector,
			presetDialog=ui_creation.PartPresetDialog,
			delMsg="The selected part of the selected bar will be deleted",
			presets=["Part"])
		barGroup._partSelector._menu = self