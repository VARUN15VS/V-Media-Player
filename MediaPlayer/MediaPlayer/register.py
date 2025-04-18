from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Toplevel, messagebox
from customtkinter import CTkLabel
from Network import send_request
import re
import sys

remaining_time = 0
verified = False
check = False

# Determine base path based on execution mode
if getattr(sys, 'frozen', False):  # If running as an .exe
    OUTPUT_PATH = Path(sys._MEIPASS)
else:  # Running as a script
    OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH = OUTPUT_PATH / "register_assets" / "frame0"

def relative_to_assets(path: str) -> str:
    full_path = ASSETS_PATH / path
    return str(full_path)  # Ensure it returns a string

def center_window_sub(self, master, width, height):
        """Centers the Toplevel window on the screen."""
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")

class Register(Toplevel):
    def __init__(window, img, master=None):
        super().__init__()
        window.geometry("510x444")
        window.configure(bg = "#292828")
        window.overrideredirect(True)

        window.center_window(window.master,510,444)

        canvas = Canvas(
            window,
            bg = "#292828",
            height = 444,
            width = 510,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(
            430.0,
            163.0,
            image=image_image_1
        )

        canvas.create_text(
            18.0,
            107.0,
            anchor="nw",
            text="FIRST NAME",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            18.0,
            149.0,
            anchor="nw",
            text="LAST NAME",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            18.0,
            191.0,
            anchor="nw",
            text="PHONE NO",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            18.0,
            233.0,
            anchor="nw",
            text="PASSWORD",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            18.0,
            275.0,
            anchor="nw",
            text="E-MAIL",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            18.0,
            317.0,
            anchor="nw",
            text="OTP",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            241.0,
            117.0,
            image=entry_image_1
        )
        window.entry_1 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_1.place(
            x=143.0,
            y=102.0,
            width=196.0,
            height=28.0
        )

        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            241.0,
            159.0,
            image=entry_image_2
        )
        window.entry_2 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_2.place(
            x=143.0,
            y=144.0,
            width=196.0,
            height=28.0
        )

        entry_image_3 = PhotoImage(
            file=relative_to_assets("entry_3.png"))
        entry_bg_3 = canvas.create_image(
            241.0,
            201.0,
            image=entry_image_3
        )
        window.entry_3 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_3.place(
            x=143.0,
            y=186.0,
            width=196.0,
            height=28.0
        )

        entry_image_4 = PhotoImage(
            file=relative_to_assets("entry_4.png"))
        entry_bg_4 = canvas.create_image(
            241.0,
            243.0,
            image=entry_image_4
        )
        window.entry_4 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_4.place(
            x=143.0,
            y=228.0,
            width=196.0,
            height=28.0
        )

        entry_image_5 = PhotoImage(
            file=relative_to_assets("entry_5.png"))
        entry_bg_5 = canvas.create_image(
            241.0,
            285.0,
            image=entry_image_5
        )
        window.entry_5 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_5.place(
            x=143.0,
            y=270.0,
            width=196.0,
            height=28.0
        )

        entry_image_6 = PhotoImage(
            file=relative_to_assets("entry_6.png"))
        entry_bg_6 = canvas.create_image(
            241.0,
            327.0,
            image=entry_image_6
        )
        window.entry_6 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_6.place(
            x=143.0,
            y=312.0,
            width=196.0,
            height=28.0
        )

        canvas.create_rectangle(
            53.0,
            66.0,
            456.0049743652344,
            67.0,
            fill="#FFFFFF",
            outline="")

        canvas.create_text(
            81.0,
            15.0,
            anchor="nw",
            text="CREATE ACCOUNT!",
            fill="#FF0000",
            font=("Inter Bold", 36 * -1)
        )

        window.label = CTkLabel(canvas, text="00:00", bg_color='#292828', fg_color='#292828', font=("Inter Bold", 16))
        window.label.place(x=330.0, y=190.0)

        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = Button(
            canvas,
            image=button_image_1,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda event=None: window.next(),
            relief="flat"
        )
        button_1.place(
            x=115.0,
            y=373.0,
            width=280.0,
            height=44.0
        )

        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        window.button_2 = Button(
            canvas,
            image=button_image_2,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.verify(),
            relief="flat"
        )
        window.button_2.place(
            x=364.0,
            y=273.0,
            width=133.0,
            height=30.0
        )

        button_image_3 = PhotoImage(
            file=relative_to_assets("button_3.png"))
        window.button_3 = Button(
            canvas,
            image=button_image_3,
            state='disabled',
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.verification(),
            relief="flat"
        )
        window.button_3.place(
            x=364.0,
            y=312.0,
            width=133.0,
            height=30.0
        )

        close_3 = Button(canvas, image=img, background='#292828', borderwidth=0, highlightthickness=0, command=lambda: window.close(), relief="flat")
        close_3.place(x=455.0, y=10.0, width=46.0, height=48.0)

        window.entry_5.bind('<KeyPress>', lambda event: window.on_keypress_email())

        window.grab_set()
        window.resizable(False, False)
        window.mainloop()

    def verification(window):
        global verified
        e5 = window.entry_5.get()
        e5 = e5.lower()
        e6 = window.entry_6.get()
        if e6 == "":
            messagebox.showerror("No OTP Found!!!", "Please enter an OTP.")
        else:
            response = send_request("email_otp_verification", e5, e6)
            if response == '0':
                messagebox.showinfo("Verification Successfull!", "OTP Verified Successfully.")
                verified = True
            elif response == '1':
                messagebox.showerror("Wrong OTP!!!", "OTP doesn't match. TRY AGAIN!")
            else:
                messagebox.showerror("Failed!!!", "Failed due to unexpected error. TRY AGAIN!")

    def on_keypress_email(window, event=None):
        global verified
        verified = False

    def close(window):
        window.destroy()

    def username(window, fname, lname, email, phoneno, password, event=None):
        # Create a new popup window
        window.uname_popup = Toplevel(window.master)
        window.uname_popup.geometry("517x166")  # Corrected window geometry call
        window.uname_popup.configure(bg="#292828")
        window.uname_popup.overrideredirect(True)

        center_window_sub(window.uname_popup, window.master,517,166)

        canvas = Canvas(
            window.uname_popup,
            bg="#292828",
            height=166,
            width=517,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        canvas.create_text(
            28.0,
            19.0,
            anchor="nw",
            text="CREATE USERNAME",
            fill="#FF0000",
            font=("Inter Bold", 24 * -1)
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("e1.png"))
        entry_bg_1 = canvas.create_image(
            171.0,
            74.0,
            image=entry_image_1
        )

        # The 'Entry' should be placed inside 'uname_popup' not 'window.uname_popup'
        window.e1 = Entry(
            window.uname_popup,  # Corrected the reference to the popup window
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.e1.place(
            x=38.0,
            y=59.0,
            width=266.0,
            height=28.0
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("b1.png"))
        b1 = Button(
            window.uname_popup,
            image=button_image_1,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.uname_popup.destroy(),
            relief="flat"
        )
        b1.place(
            x=34.0,
            y=116.0,
            width=209.0,
            height=37.0
        )

        button_image_2 = PhotoImage(
            file=relative_to_assets("b2.png"))
        b2 = Button(
            window.uname_popup,
            image=button_image_2,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.complete_registration(fname, lname, email, phoneno, password),
            relief="flat"
        )
        b2.place(
            x=280.0,
            y=116.0,
            width=209.0,
            height=37.0
        )

        button_image_3 = PhotoImage(
            file=relative_to_assets("b3.png"))
        b3 = Button(
            window.uname_popup,
            image=button_image_3,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.check_uname(),
            relief="flat"
        )
        b3.place(
            x=347.0,
            y=59.0,
            width=134.0,
            height=30.0
        )

        window.uname_popup.grab_set()
        window.e1.bind('<KeyPress>', lambda event: window.key_pressed_uname())

        window.uname_popup.mainloop()

    def key_pressed_uname(window, event=None):
        global check
        check = False

    def check_uname(window):
        global check
        uname = window.e1.get()
        uname = uname.lower()
        response = send_request("check_username",uname)
        if response=='0':
            messagebox.showinfo("Accepted", "USER NAME accepted. And spaces or blank spaces in the USER NAME will be omitted and USER NAME will be converted to lower case for security reasons.")
            check=True
        elif response=='-1':
            messagebox.showerror("Failed!!!", "Unexpected Error occured. Try Again!")
        elif response=='2':
            messagebox.showerror("Failed!!!", "You cann't leave USER NAME empty.")
        else:
            messagebox.showerror("Already exist", "User Name already exist. Choose another User Name.")

    def complete_registration(window, fname, lname, email, phoneno, password):
        if check==True:
            print("Registration")
            uname = window.e1.get()
            uname = uname.lower()
            response = send_request("register", uname, fname, lname, email, phoneno, password)
            if response=='0':
                messagebox.showinfo("Successfull", "Account Created Successfully")
                response2 = send_request("final_mail", email.lower(), uname)
                if response2 == 0:
                    messagebox.showinfo("Mail", "Thank You for choosing V-MEDIA-PLAYER. CHECK YOUR MAIL.")
            else:
                messagebox.showerror("Error!!!", "Some unexpectd ERROR occured. TRY AGAIN")
            window.uname_popup.destroy()
        else:
            messagebox.showerror("USER NAME not verified!!!", "USER NAME not verified. Verify USER NAME.")

    def next(window, event=None):
        e1 = window.entry_1.get()
        e2 = window.entry_2.get()
        e3 = window.entry_3.get()
        e4 = window.entry_4.get()
        e5 = window.entry_5.get()
        e5 = e5.lower()
        if verified == False:
            messagebox.showerror("ERROR!!!", "E-mail not verified.")
        else:
            if e1=="" or e2=="" or e3=="" or e4=="" or e5=="":
                messagebox.showerror("Empty Field!!!", "Please fill all the fields.")
            else:
                window.destroy()
                window.after(100, lambda event = None: window.username(e1,e2,e5,e3,e4))

    def start_countdown(window):
        global remaining_time
        remaining_time = 90  # 1 minute 30 seconds in total
        window.update_timer()
        window.button_2.configure(state="disabled")  # Disable the button during countdown

    def update_timer(window):
        global remaining_time
        if remaining_time > 0:
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            window.label.configure(text=f"{minutes:02}:{seconds:02}")
            remaining_time -= 1
            window.after(1000, lambda : window.update_timer())  # Call this function again after 1 second
        else:
            window.label.configure(text="00:00")
            window.button_2.configure(state="normal")  # Enable the button after countdown finishes

    def validate_email(window, email):
        return bool(re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

    def verify(window):
        e5 = window.entry_5.get()
        e5 = e5.lower()
        print(e5)
        if e5=="":
            messagebox.showerror("Empty Field!!!","Please enter you email first.")
        else:
            v_email = window.validate_email(e5)
            if v_email == False:
                messagebox.show("Invalid email!!!", "Please enter a valid email.")
            else:
                response = send_request("email_verification", e5)
                if response == '1':
                    messagebox.showerror("Failed!!!", "OTP Generation Failed. Try Again!")
                elif response == '-1':
                    messagebox.showerror("Already exist!!!", "Email already exist.")
                elif response == '2':
                    messagebox.showerror("Failed!!!", "OTP Generation Failed. Try Again!")
                else:
                    messagebox.showinfo("OTP", "OTP generated successfully.")
                    window.start_countdown()
                    window.button_3.configure(state="normal")

    def center_window(self, master, width, height):
        """Centers the Toplevel window on the screen."""
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")