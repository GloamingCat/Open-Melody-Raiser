#!/usr/bin/python

import tkinter, ui_groups, ui_menu, core_project
from tkinter import ttk

class MainFrame(tkinter.Frame):

	def __init__(self, top):
		tkinter.Frame.__init__(self, top)
		self.projVar = tkinter.StringVar()
		self.projVar.trace('w', lambda *x : top.wm_title("MIDI Composer - " + self.projVar.get()))
		# Music signature
		self.sigFrame = ui_groups.SignatureFrame(self)
		self.sigFrame.pack(side=tkinter.TOP, padx=5, pady=5)
		# Tracks
		self.trackFrame = ui_groups.TrackFrame(self)
		self.trackFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
		# Bar Composer
		self.barFrame = ui_groups.BarFrame(self)
		self.barFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
		# Window menu
		menu = ui_menu.Menu(top, self)
		menu.setSubFrames(self.trackFrame, self.barFrame)

	def updateGUI(self, project):
		self.sigFrame.loadSignature(project)
		self.trackFrame.loadTracks(project)
		
	def buildProject(self):
		project = core_project.defaultProject()
		self.sigFrame.saveSignature(project)
		self.trackFrame.saveTracks(project)
		return project

if __name__ == "__main__":
	tk = tkinter.Tk()
	tk.wm_title("MIDI Composer")
	main = MainFrame(tk)
	main.pack(fill=tkinter.BOTH, expand=True)
	tk.mainloop()