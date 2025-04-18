from pathlib import Path
from pkgutil import get_loader
from tkinter import filedialog, simpledialog, Tk, Canvas, Entry, Text, Button, PhotoImage, Toplevel, messagebox, Frame
import tkinter as tk
from customtkinter import CTkLabel
from tkinter import ttk
import sys
from urllib import response
import Network
import os
import threading
import time

CHECK = False
file_path = ""

UNAME = ""
PASSWORD = ""
MLIST = {}
R1 = ""

# Determine base path based on execution mode
if getattr(sys, 'frozen', False):  # If running as an .exe
    OUTPUT_PATH = Path(sys._MEIPASS)
else:  # Running as a script
    OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH = OUTPUT_PATH / "account_assets" / "frame0"

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

class upload_popup(Toplevel):
    def __init__(window, uname="",mlist={},file_size="", master=None):
        super().__init__(master)
        window.geometry("645x600")
        window.configure(bg = "#292828")
        window.overrideredirect(True)

        window.f_size = float(file_size)

        if uname == "":
            window.uname = UNAME
        else:
            window.uname = uname

        if bool(mlist)==False:
            mlist = MLIST

        window.center_window(window.master, 645, 600)

        canvas = Canvas(
            window,
            bg = "#292828",
            height = 600,
            width = 645,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        canvas.create_text(
            17.0,
            8.0,
            anchor="nw",
            text="Available Space : ",
            fill="#FFFFFF",
            font=("Inter Bold", 20 * -1)
        )

        canvas.create_text(
            17.0,
            42.0,
            anchor="nw",
            text="Total Space : ",
            fill="#FF0000",
            font=("Inter Bold", 20 * -1)
        )

        window.label_space = CTkLabel(
            master=canvas, 
            text=file_size, 
            fg_color="#292828", 
            text_color="white", 
            font=("Inter", 16, "bold")
        )
        window.label_space.place(x=160, y=5)

        canvas.create_text(
            201.0,
            42.0,
            anchor="nw",
            text="5.0",
            fill="#FF0000",
            font=("Inter Bold", 20 * -1)
        )

        canvas.create_rectangle(
            5.0,
            299.0,
            640.0,
            300.0,
            fill="#FFFFFF",
            outline="")

        canvas.create_rectangle(
            5.0,
            76.0,
            640.0,
            77.0,
            fill="#FFFFFF",
            outline="")

        canvas.create_text(
            11.0,
            138.0,
            anchor="nw",
            text="Name",
            fill="#FFFFFF",
            font=("Inter Bold", 24 * -1)
        )

        canvas.create_text(
            11.0,
            199.0,
            anchor="nw",
            text="Description",
            fill="#FFFFFF",
            font=("Inter Bold", 24 * -1)
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            135.0,
            177.0,
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
            x=21.0,
            y=167.0,
            width=228.0,
            height=18.0
        )

        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            198.5,
            257.0,
            image=entry_image_2
        )
        window.entry_2 = Text(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.entry_2.place(
            x=31.0,
            y=228.0,
            width=335.0,
            height=56.0
        )
        
        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        window.button_1 = Button(
            canvas,
            background='#292828',
            state = "normal",
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.check(uname),
            relief="flat"
        )
        window.button_1.place(
            x=286.0,
            y=167.0,
            width=100.0,
            height=26.0
        )

        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        window.button_2 = Button(
            canvas,
            background='#292828',
            state = "normal",
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.upload_movie(),
            relief="flat"
        )
        window.button_2.place(
            x=459.0,
            y=151.0,
            width=122.0,
            height=116.0
        )
    
        canvas.create_text(
            11.0,
            86.0,
            anchor="nw",
            text="Upload Section",
            fill="#FF0000",
            font=("Inter Bold", 36 * -1)
        )

        canvas.create_text(
            11.0,
            310.0,
            anchor="nw",
            text="Media Uploaded",
            fill="#FF0000",
            font=("Inter Bold", 36 * -1)
        )

        canvas.create_text(
            465.0,
            267.0,
            anchor="nw",
            text="Upload File",
            fill="#FFFFFF",
            font=("Inter Bold", 20 * -1)
        )

        # Create a frame inside the canvas to hold the Treeview
        frame = Frame(canvas, background='#292828', height=188, width=604)
        frame.place(x=20, y=366)  # Place the frame inside the canvas

        # Configure Treeview styling
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#292828",
            foreground="white",
            fieldbackground="#292828",
           font=("Arial", 10)
        )
        style.configure("Treeview.Heading", background="#292828", foreground="black", font=("Arial", 10, "bold"))

        # Create the Treeview inside the frame
        columns = ["Movie Name", "Description"]
        window.tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)  # Reduce height if needed
        window.tree.heading("Movie Name", text="Movie Name")
        window.tree.heading("Description", text="Description")
        window.tree.column("Movie Name", anchor="center", width=290)  # Adjust width to fit frame
        window.tree.column("Description", anchor="center", width=290)

        # Use pack to make Treeview fit inside the frame
        window.tree.pack(expand=True, fill="both")

        # Insert data
        for mname, desc in mlist.items():
            window.tree.insert("", tk.END, values=(mname, desc))

        button_image_3 = PhotoImage(
            file=relative_to_assets("button_3.png"))
        window.button_3 = Button(
            canvas,
            background='#292828',
            state = "normal",
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.delete_button(),
            relief="flat"
        )
        window.button_3.place(
            x=466.0,
            y=562.0,
            width=155.0,
            height=30.0
        )

        button_image_4 = PhotoImage(
            file=relative_to_assets("button_4.png"))
        window.button_4 = Button(
            canvas,
            background='#292828',
            state = "normal",
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.destroy(),
            relief="flat"
        )
        window.button_4.place(
            x=23.0,
            y=562.0,
            width=155.0,
            height=30.0
        )

        button_image_5 = PhotoImage(
            file=relative_to_assets("button_5.png"))
        window.button_5 = Button(
            canvas,
            background='#292828',
            state = "normal",
            image=button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.delete_account(),
            relief="flat"
        )
        window.button_5.place(
            x=569.0,
            y=8.0,
            width=60.0,
            height=60.0
        )
        window.resizable(False, False)

        submit_image = PhotoImage(
            file=relative_to_assets("submit.png"))
        window.submit = Button(
            canvas,
            image=submit_image,
            background='#292828',
            state = "normal",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.submit_form(),
            relief="flat"
        )
        window.submit.place(
            x=460.0,
            y=90.0,
            width=133.0,
            height=30.0
        )

        window.label = CTkLabel(canvas, text="", bg_color='#292828', fg_color='#292828', font=("Inter Bold", 20))
        window.label.place(x=320, y=70)

        window.entry_1.bind('<KeyPress>', lambda event : window.on_keypressed_mname())

        window.grab_set()
        window.mainloop()

    def delete_account(window):
        r1 = Network.send_request("delete_mail", UNAME, PASSWORD, )
        print(r1)
        
        window.destroy()

        window.delete_popup = Toplevel()
        window.delete_popup.geometry("436x484")
        window.delete_popup.configure(bg = "#292828")

        window.delete_popup.overrideredirect(True)

        center_window_sub(window.delete_popup, window.master, 436, 484)

        canvas = Canvas(
            window.delete_popup,
            bg = "#292828",
            height = 484,
            width = 436,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        canvas.create_text(
            94.0,
            18.0,
            anchor="nw",
            text="DELETING ACCOUNT",
            fill="#FF0000",
            font=("Inter Bold", 24 * -1)
        )

        canvas.create_rectangle(
            74.0,
            55.0,
            360.0017395019531,
            56.0,
            fill="#FF0000",
            outline="")

        text_str = "Dear "+UNAME+","
        label1 = CTkLabel(canvas, text=text_str, bg_color='#292828', fg_color='#292828', font=("Inter Bold", 20))
        label1.place(x=5, y=55)
        
        canvas.create_text(
            48.0,
            113.0,
            anchor="nw",
            text="We are sad to see you go!  Thank you for being a  ",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            48.0,
            132.0,
            anchor="nw",
            text="part of V-Media Player and for trusting us with ",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            48.0,
            151.0,
            anchor="nw",
            text="your entertainment needs. We truly appreciate ",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            48.0,
            170.0,
            anchor="nw",
            text="your time with us and hope you had a great ",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            48.0,
            189.0,
            anchor="nw",
            text="experience.",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            48.0,
            208.0,
            anchor="nw",
            text="If you ever decide to return, we will be here to ",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )
        
        canvas.create_text(
            48.0,
            227.0,
            anchor="nw",
            text="welcome you back with open arms!",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            28.0,
            255.0,
            anchor="nw",
            text="Wishing you the best,",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        canvas.create_text(
            28.0,
            279.0,
            anchor="nw",
            text="The V-Media Player Team",
            fill="#FF0000",
            font=("Inter Bold", 16 * -1)
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("delete.png"))
        window.close_delete = Button(
            canvas,
            image=button_image_1,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: window.final_delete(r1),
            relief="flat"
        )
        window.close_delete.place(
            x=75.0,
            y=438.0,
            width=286.0,
            height=29.0
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("otp.png"))
        entry_bg_1 = canvas.create_image(
            324.0,
            402.5,
            image=entry_image_1
        )
        window.otp_1 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        window.otp_1.place(
            x=241.5,
            y=390.0,
            width=165.0,
            height=23.0
        )

        canvas.create_text(
            6.0,
            394.0,
            anchor="nw",
            text="Enter OTP send on your mail :",
            fill="#FFFFFF",
            font=("Inter Bold", 15 * -1)
        )

        canvas.create_text(
            116.0,
            315.0,
            anchor="nw",
            text="THANK YOU!",
            fill="#FFFFFF",
            font=("Inter Bold", 32 * -1)
        )

        button_image_3 = PhotoImage(file=relative_to_assets("close_button.png"))
        close_3 = Button(canvas, image=button_image_3, background='#292828', borderwidth=0, highlightthickness=0, command=lambda: window.delete_popup.destroy(), relief="flat")
        close_3.place(x=400.0, y=4.0, width=46.0, height=48.0)
        
        window.delete_popup.grab_set()
        window.delete_popup.mainloop()

    def final_delete(window, to_mail):
        global UNAME, PASSWORD, MLIST
        e1 = window.otp_1.get()
        if e1 == "":
            messagebox.showerror("Empty!!!", "You are required to enter the OTP send to your mail for verification.")
        else:
            print(to_mail, e1)
            response = Network.send_request("email_otp_verification", to_mail, e1, )
            if response == '0':
                r2 = Network.send_request("delete_account", UNAME, PASSWORD)
                messagebox.showinfo("Verification Successfull!", "OTP Verified Successfully and Account is deleted.")
                UNAME = ""
                PASSWORD = ""
                MLIST = {}
                window.delete_popup.destroy()
            elif response == '1':
                messagebox.showerror("Wrong OTP!!!", "OTP doesn't match. TRY AGAIN!")
            else:
                messagebox.showerror("Failed!!!", "Failed due to unexpected error. TRY AGAIN!")

    def delete_button(window):
        selected_item = window.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a scene to delete.")
        else:
            global file_path, UNAME, PASSWORD
            e1 = window.tree.item(selected_item)["values"][0]
            e2 = window.tree.item(selected_item)["values"][1]
            file_name = os.path.basename(file_path)
            response1 = Network.send_request("delete_movie", window.uname,e1,e2)
            # Remove the item from the treeview
            window.tree.delete(selected_item[0])
            window.tree.update_idletasks()

            # Update file size
            size = Network.send_request("file_size", UNAME, PASSWORD)
            window.label_space.configure(text = size)

    def on_keypressed_mname(window, event=None):
        global CHECK
        CHECK = False

    def add_movie(window):
        global file_path
        e1 = window.entry_1.get()
        e2 = window.entry_2.get("1.0", "end").strip()
        file_name = os.path.basename(R1)
        response = Network.send_request("add_movie",window.uname,e1,e2,file_name)
        if response=="0":
            messagebox.showinfo("Successfull", "Video Uploaded Successfully.")
        else:
            response2 = Network.send_request("delete_movie", window.uname,e1,e2,file_name)
            messagebox.showerror("Error!!!", "Some error has occured.")
        
    def disable_enable(window, state):
        if state == "normal":
            window.button_1.configure(state = "disabled")
            window.button_2.configure(state = "disabled")
            window.button_3.configure(state = "disabled")
            window.button_4.configure(state = "disabled")
            window.button_5.configure(state = "disabled")
            window.submit.configure(state = "disabled")
        else:
            window.button_1.configure(state = "normal")
            window.button_2.configure(state = "normal")
            window.button_3.configure(state = "normal")
            window.button_4.configure(state = "normal")
            window.button_5.configure(state = "normal")
            window.submit.configure(state = "normal")

    def update_label(window):
        global UNAME, PASSWORD
        uploaded = str(Network.UPLOADED)
        window.label.configure(text=f"{Network.UPLOADED:.2f}%")  # Format to 2 decimal places
    
        if Network.UPLOADED < 100:  # Stop updating after completion
            window.after(1000, window.update_label)
        else:
            window.add_movie()
            size = Network.send_request("file_size", UNAME, PASSWORD)
            e1 = window.entry_1.get()
            e2 = window.entry_2.get("1.0", "end").strip()
            window.label_space.configure(text = size)
            window.disable_enable("disabled")
            window.label.configure(text="")
            window.tree.insert("", tk.END, values=(e1, e2))
            window.tree.update()

    def do_not_close(window):
        messagebox.showinfo("Please do not close", "Please do not close the window until the upload is completed.")
            
    def submit_form(window):
        """Handles form submission and uploads the file."""
        global file_path, R1
        e1 = window.entry_1.get()
        e2 = window.entry_2.get("1.0", "end").strip()
        if CHECK and file_path and window.entry_2.get("1.0", "end").strip():
            print(file_path)

            ip = Network.get_ip_addresses()
        
            r1 = Network.send_request("upload", window.uname, file_path, ip, )
            if r1 != "0":
                R1 = r1
                threading.Thread(target=window.disable_enable, args=("normal", ), daemon=True).start()
                threading.Thread(target=window.update_label, daemon=True).start()
                threading.Thread(target=Network.start_server, args=(file_path,), daemon=True).start()
                threading.Thread(target=window.do_not_close, daemon=True).start()
            else:
                messagebox.showerror("ERROR!!!", "Unexpected error occured.")

    def check(window, uname):
        global CHECK
        e1 = window.entry_1.get()
        if '\\' in e1:
            messagebox.showerror("ERROR!!!", "Your movie name should not contain \\.")
            return
        elif '/' in e1:
            messagebox.showerror("ERROR!!!", "Your movie name should not contain /.")
            return
        if e1=="":
            messagebox.showerror("Empty!!!", "Please make sure that no field is empty.")
        else:
            response = Network.send_request("check", uname, e1)
            if response == '0':
                messagebox.showinfo("Successfully", "No previous entry exist.")
                CHECK = True
            else:
                messagebox.showerror("Failed!!!", "Unexpected Error occured.")

    def upload_movie(window):
        global file_path
        filetypes = [
            ("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.flv"),
            ("Audio Files", "*.mp3;*.wav;*.aac;*.ogg;*.flac"),
        ]
        file_path = filedialog.askopenfilename(filetypes=filetypes, title="Select a Media File")
        if file_path:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(file_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
            t_size = float(total_size/(1024*1024*1024))
            if window.f_size < t_size:
                messagebox.showerror("ERROR!!!", "Not enough space available.")

    def center_window(self, master, width, height):
        """Centers the Toplevel window on the screen."""
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")
