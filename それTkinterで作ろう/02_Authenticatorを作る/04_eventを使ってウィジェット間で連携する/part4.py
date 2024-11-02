import tkinter
from qreader import QReader
from PIL import ImageGrab
import numpy as np


class QrCodeReader:
    def __init__(self, master) -> None:
        self.frame = tkinter.Frame(master)
        self.frame.grid(column=0, row=0)
        
        qr_img = tkinter.PhotoImage(file="./code/02/qrcode.png").subsample(3, 3)

        self.qr_read_button = tkinter.Button(self.frame, command=self.qr_read, image=qr_img)
        self.qr_read_button.image = qr_img
        self.qr_read_button.grid(column=0, row=0, padx=10, pady=10)

    def qr_read(self, event=None):
        clipboard_img = ImageGrab.grabclipboard()
        if clipboard_img:
            pilimg = np.array(clipboard_img, dtype=np.uint8)

            qreader = QReader()

            qrdata = qreader.detect_and_decode(pilimg[..., :3])
            if len(qrdata) > 0:
                global _qrdata
                _qrdata = qrdata[0]
                root.event_generate("<<qrread>>")


class OTPPreviewer:
    def __init__(self, master) -> None:
        self.frame = tkinter.Frame(master)
        self.frame.grid(column=0, row=1, sticky="ew")
        self.frame.grid_columnconfigure(index=0, weight=1)
        self.frame.grid_rowconfigure(index=[0, 1], weight=1)
        self.frame.anchor("center")
        
        scrollbar = tkinter.Scrollbar(self.frame)
        scrollbar.grid(column=1, row=1, sticky="ns")
        self.otp_list = tkinter.StringVar(self.frame)
        self.otp_listbox = tkinter.Listbox(self.frame, listvariable=self.otp_list, width=40, font=("メイリオ", 11),
                                           yscrollcommand=scrollbar.set, activestyle="none")
        scrollbar["command"] = self.otp_listbox.yview
        self.otp_listbox.grid(column=0, row=1, padx=20, pady=10, sticky="ew")        

        root.bind("<<qrread>>", self.add_qrdata)

    def add_qrdata(self, event=None):
        print(_qrdata)


root = tkinter.Tk()
root.geometry("300x500")
root.title("Authenticator")
root.anchor("center")

root.grid_columnconfigure(index=0, weight=1)
root.grid_rowconfigure(index=[0, 1], weight=1)

qrcodereader = QrCodeReader(root)
otppreviwer = OTPPreviewer(root)

_qrdata = ""

root.mainloop()
