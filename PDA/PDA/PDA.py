from time import process_time
import importlib
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

class PDA(object):
    # Constants
    PDA_TITLE="Pitch Determination Algorithm"   # window title
    WINDOW_GEOMETRY='640x480'                   # default size
    WINDOW_PERCENT_SCREEN=0.5                   # use half screen width and half height
    PROCESSING_MODES={"GPU":1,"CPU":2}
    INPUT_SOURCES={"MIC":1,"FILE":2}
    DEFAULT_SOURCE_FILE="Source Sound File"

    # Member Variables


    # Constructor
    def __init__(self):
        self.importCusignal()
        self.display()

    # Main Run Loop
    def run(self):
        print("Done")

    # Contructs User GUI
    def display(self):
        w=Tk()
        self.configureWindow(w)
        self.configureCmdFrm(w)
        self.configurePlotFrm(w)
        self.configurePlotFrm(w)
        self.configureTimerFrm(w)
        w.mainloop()

    # Sets window size
    def windowSize(self,containerWindow):
        # get screen size
        screenWidth=containerWindow.winfo_screenwidth()
        screenHeight=containerWindow.winfo_screenheight()

        # set window size to be within screen
        windowWidth=int(screenWidth*self.WINDOW_PERCENT_SCREEN)
        windowHeight=int(screenHeight*self.WINDOW_PERCENT_SCREEN)

        # format to string that for geometry call
        return "{}x{}".format(windowWidth,windowHeight)

    # http://www.java2s.com/Code/Python/GUI-Tk/Layoutbuttoninarowwithdifferentpadx.htm
    def configureWindow(self, containerWindow):
        containerWindow.geometry(self.windowSize(containerWindow))
        containerWindow.resizable(width=True, height=True)
        containerWindow.title(self.PDA_TITLE)

    def gpuSwitch(self, containerFrame):
        if self._cusignal is None:
            pass                        # can't use cusignal module
        else:
           f=Frame(containerFrame)
           self.procMode = IntVar(containerFrame,1) # default to GPU mode
           for (text, mode) in self.PROCESSING_MODES.items():
                r = Radiobutton(f, text=text, variable=self.procMode,
                    value=mode, indicator=0, background="light blue")
                r.pack(side=LEFT)
           f.pack(side=LEFT, padx=10)

    def srcSwitch(self, containerFrame):
        f=Frame(containerFrame)
        self.srcMode = IntVar(containerFrame,1) # default to MIC mode
        for (text, mode) in self.INPUT_SOURCES.items():
            r = Radiobutton(f, text=text, variable=self.srcMode, 
                value=mode, indicator=0, background="pink")
            r.pack(side=LEFT)
        f.pack(side=LEFT, padx=10)

    def loadFile(self):
        fileName=askopenfilename(title = "Select sound file",
            filetypes = (("Wave files","*.wav"), 
                         ("MP3 files","*.mp3")))
        self.srcFile.set(fileName)
        self.displaySignals()

    def displaySignals(self):
        startTime=process_time()
        messagebox.showinfo("Sound File",self.srcFile.get().strip())
        elapsedTime=process_time()-startTime
        self.processingTime.set(elapsedTime)

    def OnFileEntryClick(self, event):
        value=self.srcFile.get().strip()
        changed = True if self.prevSrcFile != value else False
        if changed:
            self.displaySignals()
        self.prevSrcFile=value

    def fileBrowser(self, containerFrame):
        f=Frame(containerFrame)
        self.srcFile=StringVar()
        self.prevSrcFile=''
        l=Entry(f, textvariable=self.srcFile, justify=LEFT)
        l.bind("<Return>", self.OnFileEntryClick)
        l.pack(side=LEFT, fill=X, expand=YES)
        b=Button(f, text="Browse", command=lambda:self.loadFile())
        b.pack(side=LEFT)
        f.pack(side=LEFT, padx=10, fill=X, expand=YES)

    def configureCmdFrm(self,containerWindow):
        f=Frame(containerWindow)
        self.gpuSwitch(f)
        self.srcSwitch(f)
        self.fileBrowser(f)
        f.pack(anchor=N, fill=X, expand=YES)

    def configurePlotFrm(self, containerWindow):
        pass

    def configureTimerFrm(self, containerWindow):
        f=Frame(containerWindow)
        lUnit=Label(f,text='nanoseconds')
        lUnit.pack(side=RIGHT)
        self.processingTime=StringVar()
        self.processingTime.set('TBD')
        lValue=Label(f,textvariable=self.processingTime)
        lValue.pack(side=RIGHT)
        f.pack(anchor=S, fill=X, expand=YES)

    def importCusignal(self):
        self._cusignal = importlib.util.find_spec('cusignal')

if __name__ == '__main__':
    PDA().run()
