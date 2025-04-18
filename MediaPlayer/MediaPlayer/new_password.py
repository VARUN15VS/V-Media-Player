from pathlib import Path
import tkinter as tk
from tkinter import Canvas, Toplevel, messagebox, Button, PhotoImage, Entry
from customtkinter import CTkLabel
from Network import send_request
import sys

# Determine base path based on execution mode
if getattr(sys, 'frozen', False):  # If running as an .exe
    OUTPUT_PATH = Path(sys._MEIPASS)
else:  # Running as a script
    OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH = OUTPUT_PATH / "Media_assets" / "frame0"

def relative_to_assets(path: str) -> str:
    full_path = ASSETS_PATH / path
    return str(full_path)  # Ensure it returns a string

class New_Password_Popup(Toplevel):
    def __init__(self, email="", master=None):
        super().__init__()

        self.mail = email

        self.geometry("475x200")
        self.configure(background='#292828')
        self.overrideredirect(True)

        self.center_window(self.master,475,200)

        r1 = send_request("get_uname", email,)
        if(r1=="-1015101051"):
            messagebox.showerror("ERROR!!!", "Some unexpected error occured.Try Again.")
            self.destroy()
            return
        else:
            print(r1)

        canvas = Canvas(
            self,
            bg = "#292828",
            height = 200,
            width = 475,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        canvas.place(x = 0, y = 0)
        
        canvas.create_text(
            161.0,
            8.0,
            anchor="nw",
            text=r1,
            fill="#FF0000",
            font=("Inter Bold", 28 * -1)
        )
        canvas.create_text(
            25.0,
            75.0,
            anchor="nw",
            text="Enter New Password :",
            fill="#FFFFFF",
            font=("Inter Regular", 20 * -1)
        )
        canvas.create_text(
            12.0,
            121.0,
            anchor="nw",
            text="Confirm New Password :",
            fill="#FFFFFF",
            font=("Inter Regular", 20 * -1)
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            350.0,
            88.5,
            image=entry_image_1
        )
        self.entry_1 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_1.place(
            x=260.0,
            y=75.0,
            width=196.0,
            height=28.0
        )
        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            350.0,
            132.5,
            image=entry_image_1
        )
        self.entry_2 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_2.place(
            x=260.0,
            y=119.0,
            width=196.0,
            height=28.0
        )

        close_button_image = PhotoImage(
            file=relative_to_assets("close_button.png"))
        close1 = Button(
            canvas,
            background='#292828',
            image=close_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.destroy(),
            relief="flat"
        )
        close1.place(x=445, y=4, width=25, height=25)
        submit_button_image = PhotoImage(
            file=relative_to_assets("submit.png"))
        submit_button = Button(
            canvas,
            background='#292828',
            image=submit_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.submit(),
            relief="flat"
        )
        submit_button.place(x=155, y=165, width=165, height=25)

        self.grab_set()
        self.mainloop()

    def submit(self):
        e1=self.entry_1.get()
        e2=self.entry_2.get()
        if e1=="" or e2=="":
            messagebox.showerror("Empty!!!", "Please fill all the fields.")
        elif e1==e2:
            m = self.mail
            response = send_request("change_password",m,e1,)
            if response == "0":
                messagebox.showinfo("Successfull","Password changed Successfully.")
            else:
                messagebox.showerror("ERROR!!!", "Some unexpected error occured. Try Again!!!")
            self.destroy()
        else:
            messagebox.showerror("Not matched!!!", "Please enter same password in both fields.")

    def center_window(self, master, width, height):
        """Centers the Toplevel window on the screen."""
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")

