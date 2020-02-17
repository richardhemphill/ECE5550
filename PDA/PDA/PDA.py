import importlib
from tkinter import *

class PDA(object):
    # Constants
    PDA_TITLE="Auditory Analyzer"           # window title
    WINDOW_GEOMETRY='640x480'               # default size
    WINDOW_PERCENT_SCREEN=0.5
    PROCESSING_MODES={"GPU":1,"CPU":2}

    # Member Variables
    window = Tk()

    # Constructor
    def __init__(self):
        self.importCusignal()
        self.display()

    # Main Run Loop
    def run(self):
        print("Done")

    # Contructs User GUI
    def display(self):
        self.configureWindow()
        self.gpuSwitch()
        self.window.mainloop()

    # Sets window size
    @property
    def windowSize(self):
        # get screen size
        screenWidth=self.window.winfo_screenwidth()
        screenHeight=self.window.winfo_screenheight()

        # set window size to be within screen
        windowWidth=int(screenWidth*self.WINDOW_PERCENT_SCREEN)
        windowHeight=int(screenHeight*self.WINDOW_PERCENT_SCREEN)

        # format to string that for geometry call
        self._windowSize = "{}x{}".format(windowWidth,windowHeight)

        return self._windowSize

    def configureWindow(self):
        self.window.geometry(self.windowSize)
        self.window.resizable(width=True, height=True)
        self.window.title(self.PDA_TITLE)

    def gpuSwitch(self):
        if self._cusignal is None:
            pass                        # can't use cusignal module
        else:
           self.procMode = IntVar(self.window,1) # default to GPU mode
           for (text, mode) in self.PROCESSING_MODES:
                r = Radiobutton(self.window, text=text, 
                                    variable=self.procMode, value=mode, 
                                    indicator = 0, background = "light blue"
                                    ).grid(row=0, column=mode)

    def importCusignal(self):
        self._cusignal = importlib.util.find_spec('cusignal')

if __name__ == '__main__':
    PDA().run()
