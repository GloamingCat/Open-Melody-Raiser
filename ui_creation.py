import tkinter
from tkinter import ttk, simpledialog

class BarCreationFrame(tkinter.LabelFrame):

	def __init__(self, top, params, suffix=""):
		super().__init__(top)
		if suffix == "har":
			self["text"] = "Harmony"
		elif suffix == "mel":
			self["text"] = "Melody"
		params["oct"+suffix] = tkinter.StringVar(value=4 if suffix == "har" else 5)
		params["range"+suffix] = tkinter.StringVar(value=7 if suffix == "har" else 14)
		params["npb"+suffix] = tkinter.StringVar(value=2 if suffix == "har" else 4)
		params["arp"+suffix] = tkinter.StringVar(value=0 if suffix == "har" else 100)
		params["mod"+suffix] = tkinter.StringVar(value=0)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		# Octave
		label = tkinter.Label(self, text="Octave")
		label.grid(column=0, row=0, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=9, width=4, textvariable = params["oct"+suffix])
		box.grid(column=1, row=0, sticky=tkinter.EW, padx=5, pady=5)
		# Range
		label = tkinter.Label(self, text="Range")
		label.grid(column=0, row=1, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=30, width=4, textvariable = params["range"+suffix])
		box.grid(column=1, row=1, sticky=tkinter.EW, padx=5, pady=5)
		# Modulation
		label = tkinter.Label(self, text="Modulation %")
		label.grid(column=0, row=2, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=100, width=4, textvariable = params["mod"+suffix])
		box.grid(column=1, row=2, sticky=tkinter.EW, padx=5, pady=5)
		# Notes/Bar
		label = tkinter.Label(self, text="Notes per Bar")
		label.grid(column=0, row=3, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=256, width=4, textvariable = params["npb"+suffix])
		box.grid(column=1, row=3, sticky=tkinter.EW, padx=5, pady=5)
		# Riff
		label = tkinter.Label(self, text="Apeggiation %")
		label.grid(column=0, row=4, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(self, from_=1, to=16, width=4, textvariable = params["arp"+suffix])
		box.grid(column=1, row=4, sticky=tkinter.EW, padx=5, pady=5)

class SongCreationDialog(tkinter.simpledialog.Dialog):

	def __init__(self, top):
		self.result = None
		self._params = dict()
		super().__init__(top, title="Create Song")
		
	def body(self, frame):
		# Structure/rhythm params
		self._params["bars"] = tkinter.StringVar(value="1 1 2")
		self._params["bpb"] = tkinter.StringVar(value=4)
		self._params["bpm"] = tkinter.StringVar(value=60)
		structFrame = tkinter.LabelFrame(frame, text="General")
		structFrame.columnconfigure(0, weight=1)
		structFrame.columnconfigure(1, weight=1)
		structFrame.columnconfigure(2, weight=1)
		structFrame.columnconfigure(3, weight=1)
		# Beats per minute
		label = tkinter.Label(structFrame, text="Beats per Minute")
		label.grid(column=0, row=0, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(structFrame, from_=2, to=16, width=4, textvariable = self._params["bpm"])
		box.grid(column=1, row=0, sticky=tkinter.EW, padx=5, pady=5)
		# Beats per bar
		label = tkinter.Label(structFrame, text="Beats per Bar")
		label.grid(column=2, row=0, sticky=tkinter.W, padx=5, pady=5)
		box = ttk.Spinbox(structFrame, from_=2, to=16, width=4, textvariable = self._params["bpb"])
		box.grid(column=3, row=0, columnspan=2, sticky=tkinter.EW, padx=5, pady=5)
		# Pattern
		label = tkinter.Label(structFrame, text="Bar Sequence Pattern")
		label.grid(column=0, row=1, sticky=tkinter.W, padx=5, pady=5)
		box = tkinter.Entry(structFrame, textvariable = self._params["bars"])
		box.grid(column=1, row=1, columnspan=2, sticky=tkinter.EW, padx=5, pady=5)
		structFrame.pack(side=tkinter.TOP, expand=True)
		# Melody
		melodyFrame = BarCreationFrame(frame, self._params, "mel")
		melodyFrame.pack(side=tkinter.LEFT, expand=True)
		# Harmony
		harmonyFrame = BarCreationFrame(frame, self._params, "har")
		harmonyFrame.pack(side=tkinter.RIGHT, expand=True)
		return frame

	def buttonbox(self):
		button = tkinter.Button(self, text='Generate', command=self.confirm)
		button.pack(side=tkinter.LEFT, padx=5, pady=5)
		button = tkinter.Button(self, text='Cancel', command=self.destroy)
		button.pack(side=tkinter.LEFT, padx=5, pady=5)
		self.bind("<Return>", lambda event: self.confirm())
		self.bind("<Escape>", lambda event: self.destroy())

	def confirm(self):
		self.result = {}
		for k, var in self._params.items():
			if var.get().isnumeric():
				self.result[k] = int(var.get())
			else:
				self.result[k] = var.get()
		self.destroy()

class PresetDialog(tkinter.simpledialog.Dialog):

	def __init__(self, top, typeName):
		self.result = None
		self._params = dict()
		self._typeName = typeName
		super().__init__(top, title="Create %s preset"%typeName)
		
	def body(self, frame):
		return frame

	def buttonbox(self):
		button = tkinter.Button(self, text='Generate', command=self.confirm)
		button.pack(side=tkinter.LEFT, padx=5, pady=5)
		button = tkinter.Button(self, text='Cancel', command=self.destroy)
		button.pack(side=tkinter.LEFT, padx=5, pady=5)
		self.bind("<Return>", lambda event: self.confirm())
		self.bind("<Escape>", lambda event: self.destroy())

	def confirm(self):
		self.result = {}
		for k, var in self._params.items():
			if var.get().isnumeric():
				self.result[k] = int(var.get())
			else:
				self.result[k] = var.get()
		self.destroy()

class GenerationDialog(tkinter.simpledialog.Dialog):

	def __init__(self, top, typeName):
		self.result = None
		self._params = dict()
		self._typeName = typeName
		super().__init__(top, title="Generate %s"%typeName)
		
	def body(self, frame):
		return frame

	def buttonbox(self):
		button = tkinter.Button(self, text='Generate', command=self.confirm)
		button.pack(side=tkinter.LEFT, padx=5, pady=5)
		button = tkinter.Button(self, text='Cancel', command=self.destroy)
		button.pack(side=tkinter.LEFT, padx=5, pady=5)
		self.bind("<Return>", lambda event: self.confirm())
		self.bind("<Escape>", lambda event: self.destroy())

	def confirm(self):
		self.result = {}
		for k, var in self._params.items():
			if var.get().isnumeric():
				self.result[k] = int(var.get())
			else:
				self.result[k] = var.get()
		self.destroy()