#!/usr/bin/python

import ui_signature, ui_tracks, ui_bar
import core_project, core_audio
import tkinter
from tkinter import ttk, filedialog, messagebox

class MainMenu(tkinter.Menu):

	def __init__(self, window):
		super().__init__(window)
		window.config(menu=self)
		self.window = window
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

	###########################################################################
	# File
	###########################################################################

	def newProject(self, event=None):
		self.window.projVar.set("unsaved")
		project = core_project.defaultProject()
		self.window.updateGUI(project)

	def generateProject(self, event=None):
		dialog = ui_dialog.SongCreationDialog(self.window)
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
		# Window menu
		self.menu = MainMenu(self)
		# Music signature
		self.sigFrame = ui_signature.SignatureFrame(self)
		self.sigFrame.pack(side=tkinter.TOP, padx=5, pady=5)
		# Tracks
		self.trackFrame = ui_tracks.TrackFrame(self, onSelectBar=self.onSelectBar)
		self.trackFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
		# Bar Composer
		self.barFrame = ui_bar.BarFrame(self)
		self.barFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)

	def updateGUI(self, project):
		self.sigFrame.loadSignature(project)
		self.trackFrame.loadTracks(project)
		
	def buildProject(self):
		project = core_project.defaultProject()
		self.sigFrame.saveSignature(project)
		self.trackFrame.saveTracks(project)
		return project

	###########################################################################
	# Callbacks
	###########################################################################

	def onSelectBar(self, label):
		self.barFrame.loadBar(label)

if __name__ == "__main__":
	main = MainWindow()
	main.mainloop()