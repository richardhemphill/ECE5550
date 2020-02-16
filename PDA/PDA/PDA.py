from tkinter import *

class PDA(object):
    # Constants
    PDA_TITLE="Auditory Analyzer"
    WINDOW_GEOMETRY='640x480'

    # Member Variables
    window = Tk()

    # Constructor
    def __init__(self):
        self.display()

    # Main Run Loop
    def run(self):
        print("Done")

    # Contructs User GUI
    def display(self):
        lbl = Label(self.window, text="Hello")
        lbl.grid(column=0, row=0)
        btn = Button(self.window, text="Click Me")
        btn.grid(column=1, row=0)
        self.window.geometry(self.WINDOW_GEOMETRY)
        self.window.title(self.PDA_TITLE)
        self.window.mainloop()

if __name__ == '__main__':
    PDA().run()
