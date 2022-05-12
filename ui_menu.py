import tkinter, core_audio, core_project, ui_dialog
from tkinter import filedialog, messagebox

class Menu(tkinter.Menu):

	def __init__(self, window, frame):
		super().__init__(window)
		window.config(menu=self)
		self.window = window
		self.frame = frame
		# File menu
		fileMenu = tkinter.Menu(self, tearoff=False)
		fileMenu.add_command(label="New Project", 
			accelerator="Ctrl+N", 
			command=self.newProject)
		window.bind_all("<Control-n>", self.newProject)
		fileMenu.add_command(label="New Project Creation...", 
			accelerator="Ctrl+G", 
			command=self.generateProject)
		window.bind_all("<Control-g>", self.generateProject)
		fileMenu.add_command(label="Open Project", 
			accelerator="Ctrl+O", 
			command=self.openProject)
		window.bind_all("<Control-o>", self.openProject)
		fileMenu.add_command(label="Save Project", 
			accelerator="Ctrl+S", 
			command=self.saveProject)
		window.bind_all("<Control-s>", self.saveProject)
		fileMenu.add_command(label="Exit", command=window.destroy)
		self.add_cascade(label="File", menu=fileMenu)
		# Track menu
		self.trackMenu = PopMenu(self, "track",
			"The entire track will be deleted",
			op=False, save=False)
		self.add_cascade(label="Track", menu=self.trackMenu)
		# Bar menu
		self.barMenu = PopMenu(self, "bar",
			"All bars in this time stamp will be deleted"+
			"and all tracks will be shortened by 1 bar",
			move=False)
		self.add_cascade(label="Bar", menu=self.barMenu)
		# Audio menu
		audioMenu = tkinter.Menu(self, tearoff=False)
		audioMenu.add_command(label="Play", 
			accelerator="Ctrl+R",
			command=self.audioPlay)
		window.bind_all("<Control-r>", self.audioPlay)
		audioMenu.add_command(label="Stop",
			accelerator="Ctrl+E",
			command=self.audioStop)
		window.bind_all("<Control-e>", self.audioPlay)
		audioMenu.add_command(label="Convert to OGG", 
			command=self.audioConvert)
		self.add_cascade(label="Audio", menu=audioMenu)

	def setSubFrames(self, trackFrame, barFrame):
		self.trackMenu.receiver = trackFrame
		self.barMenu.receiver = barFrame
		trackFrame.composer = barFrame

	###########################################################################
	# File
	###########################################################################

	def newProject(self, event=None):
		self.frame.projVar.set("unsaved")
		project = core_project.defaultProject()
		self.frame.updateGUI(project)

	def generateProject(self, event=None):
		dialog = ui_dialog.SongCreationDialog(self.window)
		if dialog.result:
			self.frame.projVar.set("unsaved")
			project = core_project.generateProject(dialog.result)
			self.frame.updateGUI(project)

	def openProject(self, event=None):
		filetypes = (
	        ('Project files', '*.proj'),
	        ('All files', '*.*'))
		filename = tkinter.filedialog.askopenfilename(
			title='Open a project file',
	        initialdir='./',
	        filetypes=filetypes)
		if filename and filename != '':
			self.frame.projVar.set(filename)
			project = core_project.loadProject(filename)
			self.frame.updateGUI(project)

	def saveProject(self, event=None):
		filetypes = (
	        ('Project files', '*.proj'))
		filename = tkinter.filedialog.asksaveasfilename(
			title='Selected file name',
	        initialdir='./',
	        filetypes=filetypes)
		if filename and filename != '':
			self.frame.projVar.set(filename)
			project = self.frame.buildProject()
			core_project.saveProject(project)

	###########################################################################
	# Audio
	###########################################################################

	def audioConvert(self, event=None):
		project = self.frame.buildProject()
		core_project.exportMidi(project)
		success = core_audio.generateOgg()
		file = self.frame.projVar.get()
		if success:
			tkinter.messagebox.showinfo("Generation Complete", "MIDI %s succesfully converted to OGG." % file)
		else:
			tkinter.messagebox.showinfo("Generation Cancelled", "Conversion of MIDI %s to OGG was cancelled." % file)

	def audioPlay(self, event=None):
		project = self.frame.buildProject()
		core_project.exportMidi(project)
		success = core_audio.playMidi()
		if not success:
			tkinter.messagebox.showerror("Error", "Something went wrong.")

	def audioStop(self, event=None):
		core_audio.stopMidi()

	def destroy(self):
		tkinter.Menu.destroy(self)
		core_audio.clear()

###############################################################################
# Pop-up
###############################################################################

class PopMenu(tkinter.Menu):

	def __init__(self, top, typeName, delMsg, move=True, op=True, save=True):
		super().__init__(top, tearoff=False)
		self.window = top.window
		self.receiver=None
		addMenu = tkinter.Menu(self, tearoff=False)
		self.add_cascade(label="Add "+typeName, menu=addMenu)
		addMenu.add_command(label="Empty", command=self.onAddNew)
		addMenu.add_command(label="Duplicate", command=self.onDuplicate)
		addMenu.add_command(label="Generate", command=self.onGenerateNew)
		replaceMenu = tkinter.Menu(self, tearoff=False)
		self.add_cascade(label="Replace", menu=replaceMenu)
		replaceMenu.add_command(label="Preset...", command=self.onPreset)
		replaceMenu.add_command(label="Preset (file)...", command=self.onPresetFile)
		replaceMenu.add_command(label="Generate...", command=self.onGenerate)
		replaceMenu.add_command(label="Clear", command=self.onClear)
		if move:
			self.add_command(label="Move Up", command=self.onMoveUp)
			self.add_command(label="Move Down", command=self.onMoveDown)
		self.add_command(label="Delete "+typeName, command=self.onDelete)
		if save:
			self.add_command(label="Save preset...", command=self.onSave)
		self.typeName = typeName
		self.delMsg = delMsg

	###########################################################################
	# Insert / Delete
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