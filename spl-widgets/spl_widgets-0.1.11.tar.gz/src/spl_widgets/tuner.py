from tkinter import *
from tkinter import filedialog, ttk
from .misc_util import *
from .tune_freq import tune_cols

def main():

    root=Tk()
    root.title("CTSF's SWX Tuner")
    root.geometry("415x270+50+50")
    root.resizable(False, False)

    intervalVar = StringVar()
    fileVar = StringVar()
    scaleVar = StringVar(value="C Major Scale")

    showVar = IntVar()
    showScalesVar = IntVar()
    noteVars = [IntVar() for _ in range(len(notes))]
    tuneFreqsVar = IntVar(value=1)

    cb_values = [f"{n} Major Scale" for n in notes]
    cb_values_ext = [f"{notes[i]} {n}" for n in default_scales.keys() for i in range(len(notes))]

    def limitIntervalLen(*args):
        interval_in = intervalVar.get()
        if len(interval_in)>2 or (len(interval_in) >0 and not interval_in[-1].isdigit()):
            intervalVar.set(interval_in[:-1])

    intervalVar.trace('w',limitIntervalLen)

    def disableScaleTuning():
        scaleCombobox.configure(state="disabled")
        advScaleCheckbox.configure(state="disabled")

    def disableNoteTuning():
        for noteCheckbox in noteButtons:
            noteCheckbox.configure(state="disabled")

    def enableScaleTuning():
        scaleCombobox.configure(state="readonly")
        advScaleCheckbox.configure(state="normal")

    def enableNoteTuning():
        for noteCheckbox in noteButtons:
            noteCheckbox.configure(state="normal")

    def showsel():

        if showVar.get():
            disableScaleTuning()
            enableNoteTuning()
        else:
            disableNoteTuning()
            enableScaleTuning()

    def getFile():
        file =  filedialog.askopenfilename(
            title="Select File to Tune",
            filetypes=[("SWX Files","*.swx")]
            )
        
        fileName.config(text=f'File: {file[file.rfind("/")+1:]}')
        fileVar.set(file) 

    def changeScalesShown():
        showAdditional = showScalesVar.get()
        if showAdditional: scaleCombobox.config(values=cb_values_ext)
        else:
            scaleCombobox.config(values=cb_values)
            if scaleVar.get() not in cb_values: scaleVar.set("C Major Scale")

    def changeTuneFreqs():
        tuneFreqs = tuneFreqsVar.get()
        if tuneFreqs: 
            for n in selectorButtons: n.configure(state="normal")
            if showVar.get(): enableNoteTuning()
            else: enableScaleTuning()
        else:
            for n in selectorButtons: n.configure(state="disabled")
            disableNoteTuning(); disableScaleTuning()

    def tuneWithData():
        filepath = fileVar.get()
        interval = int(intervalVar.get())
        tune_freqs = tuneFreqsVar.get()

        tuneType = showVar.get()        # 0: scale, 1: notes
        if tuneType == 0:
            scale_note, scale_type = scaleVar.get().split(' ',maxsplit=1)
            scale = construct_default_scale(notes.index(scale_note)+1, scale_type)
        else:
            scale = [i+1 for i in range(len(noteButtons)) if noteVars[i].get()]

        can_proceed = (filepath and interval and (scale or not tune_freqs))
        if can_proceed: tune_cols(filepath, interval, scale, bool(tune_freqs))

    optionsFrame = Frame(root, borderwidth=10); optionsFrame.pack(side='left', anchor=N)
    tuningFrame = Frame(root, pady=5); tuningFrame.pack(side='right', anchor=N)


    # File Input
    fileFrame = Frame(optionsFrame, borderwidth=5)
    fileFrame.pack(side='top', anchor=W)

    fileLabel = Label(fileFrame, text="Select File to Tune:")
    fileLabel.pack(side='top', anchor=W)

    fileInput = Button(fileFrame, text="Browse Files...", command=getFile)
    fileInput.pack(side='left')

    fileName = Label(fileFrame)
    fileName.pack(side='right')


    # Interval Input
    intervalFrame = Frame(optionsFrame, borderwidth=3)
    intervalFrame.pack(side='top', anchor=W)

    intervalInputLabel = Label(intervalFrame, text="Tuning interval (x10ms): ")
    intervalInputLabel.pack(side='left',anchor=W)

    intervalInput = Entry(intervalFrame, width=2, textvariable=intervalVar)
    intervalInput.pack(side='right',anchor=S)


    # Submit Button
    submitButton = Button(optionsFrame, text="Tune File", command=tuneWithData, borderwidth=5)
    submitButton.pack(side='bottom',anchor=W)

    # Selector Radios
    selectorFrame = Frame(optionsFrame, borderwidth=3)
    selectorFrame.pack(side='top', anchor=W)

    tuneFreqsCheckbox = Checkbutton(selectorFrame, text="Tune Frequencies", variable=tuneFreqsVar, onvalue=1, offvalue=0, command=changeTuneFreqs)
    tuneFreqsCheckbox.pack(anchor=W, side='top')

    selectorLabel = Label(selectorFrame, text="Tune File By: ")
    selectorLabel.pack(anchor=W)

    selectorButtons = [Radiobutton(selectorFrame,text=n, variable=showVar, command=showsel, value=i) for i,n in enumerate(["Scale", "Notes"])]
    for n in selectorButtons: n.pack(anchor=W)

    # Scale radio combobox
    scaleRadioFrame = Frame(tuningFrame, borderwidth=10)
    scaleRadioFrame.pack(anchor=N)

    scaleRadioLabel = Label(scaleRadioFrame, text="Select scale to tune to: ")
    scaleRadioLabel.pack(anchor=W)

    scaleCombobox = ttk.Combobox(scaleRadioFrame, textvariable = scaleVar, values=cb_values, state = "readonly")
    scaleCombobox.pack(anchor=W)

    advScaleCheckbox = Checkbutton(scaleRadioFrame, command=changeScalesShown, text="Show additional scales",onvalue=1,offvalue=0, variable=showScalesVar)
    advScaleCheckbox.pack(anchor=W)

    # Note checkbuttons
    noteButtonsFrame = Frame(tuningFrame, padx=10); noteButtonsFrame.pack(anchor=SW)
    bottomNotesFrame=Frame(noteButtonsFrame); bottomNotesFrame.pack(side='bottom')

    leftSideFrame = Frame(bottomNotesFrame, borderwidth=3, padx=10); leftSideFrame.pack(side='left', anchor=W)
    rightSideFrame = Frame(bottomNotesFrame, borderwidth=3,padx=10); rightSideFrame.pack(side='right', anchor=W)

    noteButtonsLabel = Label(noteButtonsFrame, text="Select note(s) to tune to: ")
    noteButtonsLabel.pack(anchor=N)

    noteButtons = [Checkbutton([leftSideFrame,rightSideFrame][i>5], text=n, variable=noteVars[i], onvalue=1, offvalue=0, state="disabled") for i,n in enumerate(notes)]
    for n in noteButtons: n.pack(anchor=W)

    root.mainloop()

if __name__ == "__main__": main()
