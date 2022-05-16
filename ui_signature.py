import tkinter, ui_common
from tkinter import ttk

class SignatureGroup(tkinter.LabelFrame):

	def __init__(self, top):
		super().__init__(top, text="Signature")
		self.columnconfigure(1, weight=2)
		self.columnconfigure(3, weight=1)
		self.columnconfigure(5, weight=1)
		self.columnconfigure(6, weight=2)
		self.bpmVar = tkinter.StringVar()
		self.timeVar = tkinter.StringVar()
		self.octVar = tkinter.StringVar()
		self.scaleVar = tkinter.StringVar()
		# BPM
		label = tkinter.Label(self, text="BPM:")
		label.grid(column=0, row=0, sticky=tkinter.W, padx=2, pady=5)
		box = ttk.Spinbox(self, from_=1, to=127, width=8, textvariable=self.bpmVar)
		box.grid(column=1, row=0, sticky=tkinter.EW, padx=5, pady=5)
		# Tempo
		label = tkinter.Label(self, text="Tempo:")
		label.grid(column=2, row=0, sticky=tkinter.W, padx=2, pady=5)
		self.timeBox = ttk.Combobox(self, width=8, state='readonly', textvariable=self.timeVar)
		self.timeBox['values'] = ["4/4", "3/4", "2/4", "5/4"]
		self.timeBox.current(0)
		self.timeBox.grid(column=3, row=0, sticky=tkinter.EW, padx=5, pady=5)
		# Scale
		label = tkinter.Label(self, text="Key:")
		label.grid(column=4, row=0, sticky=tkinter.W, padx=2, pady=5)
		self.scaleBox = ttk.Combobox(self, width=5, state='readonly', textvariable=self.scaleVar)
		self.scaleBox['values'] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
		self.scaleBox.current(0)
		self.scaleBox.grid(column=5, row=0, sticky=tkinter.EW, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=9, width=5, textvariable = self.octVar)
		box.grid(column=6, row=0, sticky=tkinter.EW, padx=2, pady=2)
		# Mode
		self.modeButton = ui_common.ToggleButton(self, ["Major", "Minor"], [0, 5])
		self.modeButton.grid(column=7, row=0, sticky=tkinter.EW, padx=5, pady=5)

	def loadSignature(self, project):
		self.bpmVar.set(project["bpm"])
		if project["timesig"][0] == 3:
			self.timeBox.current(1)
		elif project["timesig"][0] == 2:
			self.timeBox.current(2)
		elif project["timesig"][0] == 5:
			self.timeBox.current(3)
		else:
			self.timeBox.current(0)
		self.scaleBox.current(project["keysig"][0] % 12)
		self.octVar.set(int(project["keysig"][0] / 12))
		self.modeButton.setValue(project["keysig"][1])

	def saveSignature(self, project):
		root = int(self.scaleBox.current()) + int(self.octVar.get()) * 12
		mode = self.modeButton.getValue()
		project["keysig"] = [root, mode]
		project["timesig"] = [int(i) for i in self.timeVar.get().split('/')]
		project["bpm"] = int(self.bpmVar.get())

if __name__ == "__main__":
	main = tkinter.Tk()
	frame = SignatureGroup(main)
	frame.pack()
	main.mainloop()