#!/usr/bin/python

import ui_signature, ui_tracks, ui_bar, ui_menu, ui_creation
import core_project, core_audio
import tkinter
from tkinter import ttk, filedialog, messagebox

class MainMenu(tkinter.Menu):

	def __init__(self, window, barGroup, trackGroup):
		super().__init__(window)
		window.config(menu=self)
		self.window = window
		# File menu
		self.fileMenu = tkinter.Menu(self, tearoff=False)
		self.fileMenu.add_command(label="New Project", 
			accelerator="Ctrl+N", 
			command=self.newProject)
		window.bind_all("<Control-n>", self.newProject)
		self.fileMenu.add_command(label="New Project Creation...", 
			accelerator="Ctrl+G", 
			command=self.generateProject)
		window.bind_all("<Control-g>", self.generateProject)
		self.fileMenu.add_command(label="Open Project", 
			accelerator="Ctrl+O", 
			command=self.openProject)
		window.bind_all("<Control-o>", self.openProject)
		self.fileMenu.add_command(label="Save Project", 
			accelerator="Ctrl+S", 
			command=self.saveProject)
		window.bind_all("<Control-s>", self.saveProject)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label="Exit", command=window.destroy)
		self.add_cascade(label="File", menu=self.fileMenu)
		# Track Menu
		self.trackMenu = ui_menu.TrackMenu(self, trackGroup)
		self.add_cascade(label="Track", menu=self.trackMenu)
		# Bar Menu
		self.barMenu = ui_menu.BarMenu(self, barGroup, trackGroup)
		self.add_cascade(label="Bar", menu=self.barMenu)
		# Part Menu
		self.partMenu = ui_menu.PartMenu(self, barGroup, trackGroup)
		self.add_cascade(label="Part", menu=self.partMenu)
		# Audio menu
		self.audioMenu = tkinter.Menu(self, tearoff=False)
		self.audioMenu.add_command(label="Play", 
			accelerator="Ctrl+R",
			command=self.audioPlay)
		window.bind_all("<Control-r>", self.audioPlay)
		self.audioMenu.add_command(label="Stop",
			accelerator="Ctrl+E",
			command=self.audioStop)
		window.bind_all("<Control-e>", self.audioPlay)
		self.audioMenu.add_separator()
		self.audioMenu.add_command(label="Convert to OGG", 
			command=self.audioConvert)
		self.add_cascade(label="Audio", menu=self.audioMenu)

	###########################################################################
	# File
	###########################################################################

	def newProject(self, event=None):
		self.window.projVar.set("unsaved")
		project = core_project.defaultProject()
		self.window.updateGUI(project)

	def generateProject(self, event=None):
		dialog = ui_creation.SongCreationDialog(self.window)
		if dialog.result:
			self.window.projVar.set("unsaved")
			project = core_project.generateProject(dialog.result)
			self.window.updateGUI(project)

	def openProject(self, event=None):
		filetypes = (
	        ('Project files', '*.proj'),
	        ('All files', '*.*'))
		filename = tkinter.filedialog.askopenfilename(
			title='Open a project file',
	        initialdir='./',
	        filetypes=filetypes)
		if filename and filename != '':
			self.window.projVar.set(filename)
			project = core_project.loadProject(filename)
			self.window.updateGUI(project)

	def saveProject(self, event=None):
		filetypes = (
	        ('Project files', '*.proj'),
	        ('All files', '*.*'))
		filename = tkinter.filedialog.asksaveasfilename(
			title='Selected file name',
	        initialdir='./',
	        filetypes=filetypes)
		if filename and filename != '':
			self.window.projVar.set(filename)
			project = self.window.buildProject()
			core_project.saveProject(project, filename)

	###########################################################################
	# Audio
	###########################################################################

	def audioConvert(self, event=None):
		project = self.window.buildProject()
		core_project.exportMidi(project)
		success = core_audio.generateOgg()
		file = self.window.projVar.get()
		if success:
			tkinter.messagebox.showinfo("Generation Complete", "MIDI %s succesfully converted to OGG." % file)
		else:
			tkinter.messagebox.showinfo("Generation Cancelled", "Conversion of MIDI %s to OGG was cancelled." % file)

	def audioPlay(self, event=None):
		project = self.window.buildProject()
		core_project.exportMidi(project)
		success = core_audio.playMidi()
		if not success:
			tkinter.messagebox.showerror("Error", "Something went wrong.")

	def audioStop(self, event=None):
		core_audio.stopMidi()

	def destroy(self):
		tkinter.Menu.destroy(self)
		core_audio.clear()

class MainWindow(tkinter.Tk):

	def __init__(self):
		super().__init__()
		self.wm_title("Open Melody Raiser")
		self.projVar = tkinter.StringVar()
		self.projVar.trace('w', lambda *x : self.wm_title("Open Melody Raiser - " + self.projVar.get()))
		# Music signature
		self.sigGroup = ui_signature.SignatureGroup(self)
		self.sigGroup.pack(side=tkinter.TOP, padx=5, pady=5)
		# Tracks
		self.trackGroup = ui_tracks.TrackGroup(self, 
			onBarClick=self.onSelectBar, 
			onTrackClick=self.onSelectTrack)
		self.trackGroup.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
		# Bar Composer
		self.barGroup = ui_bar.BarGroup(self,
			onPartClick=self.onSelectPart)
		self.barGroup.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
		# Window menu
		self.menu = MainMenu(self,
			trackGroup = self.trackGroup,
			barGroup = self.barGroup)

	def updateGUI(self, project):
		self.sigGroup.loadSignature(project)
		self.trackGroup.loadTracks(project)
		
	def buildProject(self):
		project = core_project.defaultProject()
		self.sigGroup.saveSignature(project)
		self.trackGroup.saveTracks(project)
		return project

	###########################################################################
	# Callbacks
	###########################################################################

	def onSelectBar(self, label):
		self.barGroup.loadBar(label)
		self.menu.barMenu.onSelect(label != None)

	def onSelectTrack(self, track):
		self.menu.trackMenu.onSelect(track != None)

	def onSelectPart(self, label):
		self.menu.partMenu.onSelect(label != None)

if __name__ == "__main__":
	main = MainWindow()
	main.mainloop()