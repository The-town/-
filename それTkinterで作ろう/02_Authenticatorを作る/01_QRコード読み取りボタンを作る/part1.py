import tkinter


class QrCodeReader:
    def __init__(self, master) -> None:
        self.frame = tkinter.Frame(master)
        self.frame.grid(column=0, row=0)
        
        qr_img = tkinter.PhotoImage(file="./code/02/qrcode.png").subsample(3, 3)

        self.qr_read_button = tkinter.Button(self.frame, command=self.qr_read, image=qr_img)
        self.qr_read_button.image = qr_img
        self.qr_read_button.grid(column=0, row=0, padx=10, pady=10)

    def qr_read(self):
        pass


root = tkinter.Tk()
root.geometry("300x500")
root.title("Authenticator")
root.anchor("center")
qrcodereader = QrCodeReader(root)

root.mainloop()
