#!./venv/bin/python

from Tkinter import *
from ttk import Progressbar

from ui.annotate import Annotate
from ui.references import References
from ui.select_type import DTType
from ui.single_object_detection import SingleDetection
from ui.single_object_tracking import SingleTracking
from ui.steps import Steps
from ui.upload import Upload


class App(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.progress_bar = None
        self.prog_win = None

        self.working_folder = None

        self.main_container = Frame(
            self,
            highlightbackground="black",
            highlightcolor="black",
            highlightthickness=1
        )
        self.frames = {}

        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        for F in (Steps, DTType, Upload, Annotate, SingleDetection, SingleTracking, References):
            frame = F(self.main_container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Steps)

    def show_frame(self, frame):
        self.frames[frame].tkraise()
        self.frames[frame].event_generate("<<ShowFrame>>")

    def show_progress(self, start):
        if start:
            self.prog_win = Toplevel(self.main_container, padx=8, pady=8)
            self.prog_win.transient(self)
            self.prog_win.title('Working...')
            self.prog_win.resizable(0, 0)
            self.progress_bar = Progressbar(self.prog_win,
                                            orient=HORIZONTAL,
                                            mode='indeterminate',
                                            length=250,
                                            takefocus=True)
            self.progress_bar.grid()
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.prog_win.destroy()


if __name__ == '__main__':
    app = App()
    app.title("Deep Learning For Object Detection And Tracking For UAV")
    app.geometry("1280x720")
    app.mainloop()
