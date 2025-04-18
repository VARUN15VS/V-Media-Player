import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, simpledialog, PhotoImage, Canvas, ttk, messagebox, Button, Entry
import vlc
import threading
from customtkinter import CTkLabel, CTkSlider, CTkOptionMenu, CTkScrollableFrame, CTkButton
import customtkinter as ctk
import os
import json
from ctypes.wintypes import HWND
from ctypes import alignment, windll, byref, c_int, sizeof
import socket
import requests
import urllib.parse
import time
import sys
import account
import register
import Network
from new_password import New_Password_Popup
from pathlib import Path

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999

remained_time = 0

# Determine base path based on execution mode
if getattr(sys, 'frozen', False):  # If running as an .exe
    OUTPUT_PATH = Path(sys._MEIPASS)
else:  # Running as a script
    OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH = OUTPUT_PATH / "Media_assets" / "frame0"

'''# Set VLC path inside the project folder
VLC_PATH = OUTPUT_PATH / "VLC"
os.environ["PATH"] += os.pathsep + str(VLC_PATH)'''

def relative_to_assets(path: str) -> str:
    full_path = ASSETS_PATH / path
    return str(full_path)  # Ensure it returns a string

# Define the VLC folder path
VLC_PATH = OUTPUT_PATH / "VLC"

# Ensure VLC DLLs and plugins are properly located
os.environ["PATH"] = str(VLC_PATH) + os.pathsep + os.environ["PATH"]
os.environ["VLC_PLUGIN_PATH"] = str(VLC_PATH / "plugins")  # Set plugin path

# Debugging: Check if VLC path is correct
print(f"VLC Path: {VLC_PATH}")
print(f"VLC Plugins Path: {os.environ.get('VLC_PLUGIN_PATH')}")

# Try loading VLC manually
try:
    vlc_lib_path = VLC_PATH / "libvlc.dll"

    if not vlc_lib_path.exists():
        raise FileNotFoundError(f"🚨 libvlc.dll not found at {vlc_lib_path}")

    ctypes.CDLL(str(vlc_lib_path))  # Manually load VLC DLL
    vlc_instance = vlc.Instance()
    
    if vlc_instance is None:
        raise Exception("🚨 VLC instance creation failed!")

    print("VLC initialized successfully!")

except Exception as e:
    print(f"VLC initialization failed: {e}")
    vlc_instance = None  # Ensure instance is not used later

class MediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.geometry('800x600')
        self.root.title("V-Player")
        self.root.after(100, lambda: self.titlebarcolor())
        self.root.after(100, lambda : self.zoomed_state())

        # Set the icon using relative path
        icon_path = relative_to_assets("V-Player-Logo.ico")  # Use the correct relative path
        self.root.iconbitmap(str(icon_path))

        # Video display panel
        self.panel = tk.Label(self.root, background="#000000") 
        self.panel.pack(fill="both", expand=True)
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.root, height=50, bg='#292828')
        self.buttons_frame.pack(side='bottom', fill='x')

        # Progress slider using CTkSlider
        self.progress = CTkSlider(
            self.buttons_frame,
            from_=0,
            to=100,
            orientation='horizontal',
            command=self.set_progress,
        )
        self.progress.pack(side='top', fill='x', padx=10, pady=5)  # Adjust padding for alignment

        # Volume slider using CTkSlider
        self.volume_slider = CTkSlider(
            self.buttons_frame,
            from_=0,
            to=100,
            orientation='horizontal',
            command=self.set_volume,
        )
        self.volume_slider.set(100)  # Set initial volume to 100%
        self.volume_slider.pack(side='right', padx=10, pady=10)  # Add padding for better alignment
        
        # Control buttons (aligned in a row as per image)
        self.play_image = PhotoImage(file = relative_to_assets("button_10.png"))
        self.play_button = tk.Button(self.buttons_frame, image=self.play_image, command=self.play_pause, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.play_button.pack(side="left", padx=10, pady=10)

        self.stop_image = PhotoImage(file=relative_to_assets("button_8.png"))
        self.stop_button = tk.Button(self.buttons_frame, image=self.stop_image, command=self.stop, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.stop_button.pack(side='left', padx=10, pady=10)

        self.load_image = PhotoImage(file=relative_to_assets("button_7.png"))
        self.load_button = tk.Button(self.buttons_frame, image=self.load_image, command=self.load_media, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.load_button.pack(side='left', padx=10, pady=10)

        self.url_image = PhotoImage(file=relative_to_assets("button_6.png"))
        self.load_url_button = tk.Button(self.buttons_frame, image=self.url_image, command=self.load_url_media, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.load_url_button.pack(side='left', padx=10, pady=10)

        self.timeframe_image = PhotoImage(file=relative_to_assets("button_23.png"))
        self.timeframe_button = tk.Button(self.buttons_frame, image=self.timeframe_image, command=self.add_timeframe_popup, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.timeframe_button.pack(side='left', padx=10, pady=10)

        self.upload_image = PhotoImage(file=relative_to_assets("upload.png"))
        self.upload_button = tk.Button(self.buttons_frame, image=self.upload_image, command=self.account, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.upload_button.pack(side='left', padx=10, pady=10)

        self.mute_var = False
        self.mute_image = PhotoImage(file = relative_to_assets("button_1.png"))
        self.mute_button = tk.Button(self.buttons_frame, image=self.mute_image, command=self.mute, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.mute_button.pack(side='right', padx=5, pady=10)

        # Fullscreen button
        self.fullscreen = False
        self.full_image = PhotoImage(file=relative_to_assets("button_2.png"))
        self.fullscreen_button = tk.Button(self.buttons_frame, image=self.full_image, command=self.toggle_fullscreen, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.fullscreen_button.pack(side='right', padx=10, pady=10)

        self.playback_speed_var = tk.DoubleVar(value=1.0)
        self.playback_image = PhotoImage(file = relative_to_assets("button_24.png"))
        self.playback_button = tk.Button(self.buttons_frame, image=self.playback_image, command=self.playback_speed_menu, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.playback_button.pack(side='right', padx=10, pady=10)

        self.loop_var = False
        self.loop_image = PhotoImage(file = relative_to_assets("Button_5.png"))
        self.loop_button = tk.Button(self.buttons_frame, image=self.loop_image, command=self.loop, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.loop_button.pack(side='right', padx=10, pady=10)

        self.option_image = PhotoImage(file = relative_to_assets("button_22.png"))
        self.option_button = tk.Button(self.buttons_frame, image=self.option_image, command=self.option, background="#292828", borderwidth=0, highlightthickness=0, relief="flat")
        self.option_button.pack(side='right', padx=10, pady=10)

        #Timer
        self.time_label = tk.Label(
            self.buttons_frame,
            text="00:00:00 / 00:00:00",
            fg="white",
            bg="#292828",
            font=("Arial", 12)
        )
        self.time_label.pack(side="right", pady=5, padx = 15)

        # VLC player instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(100)
        self.playing = False
        self.paused = False
        self.user_interacting = False  # Flag to track slider interaction
        
        # Hide and Appear
        self.inactivity_timer = 0
        self.hide_after = 3000
        self.root.bind_all('<Motion>', self.reset_timer)  # Bind motion to entire root
        self.root.bind_all('<KeyPress>', self.reset_timer)
        self.check_inactivity()

        # Play and pause
        self.root.bind_all('<space>', self.space_press)

        # Closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_progress()

        #Event Binders
        self.root.bind('<F>', self.f_pressed)
        self.root.bind('<f>', self.f_pressed)
        self.root.bind('<Escape>', self.esc_pressed)
        self.root.bind('<M>', self.m_pressed)
        self.root.bind('<m>', self.m_pressed)
        self.root.bind('<L>', self.l_pressed)
        self.root.bind('<l>', self.l_pressed)
        self.root.bind('<C>', self.c_pressed)
        self.root.bind('<c>', self.c_pressed)
        self.root.bind('<A>', self.a_pressed)
        self.root.bind('<a>', self.a_pressed)
        self.root.bind('<Control-L>', self.ctrl_l_pressed)
        self.root.bind('<Control-l>', self.ctrl_l_pressed)
        self.root.bind('<Control-U>', self.ctrl_u_pressed)
        self.root.bind('<Control-u>', self.ctrl_u_pressed)
        self.root.bind_all('<Right>', self.right_pressed)
        self.root.bind_all('<Left>', self.left_pressed)
        self.root.bind_all('<Up>', self.up_pressed)
        self.root.bind_all('<Down>', self.down_pressed)
        self.root.bind('<t>', self.t_pressed)
        self.root.bind('<T>', self.t_pressed)
        self.root.bind_all('<Alt-KeyPress-T>', self.alt_t_pressed)
        self.root.bind_all('<Alt-KeyPress-t>', self.alt_t_pressed)
        self.last_mouse_position = (0, 0)
        self.track_mouse_activity()

        # Bind slider interactions
        self.progress.bind("<Button-1>", self.on_slider_click)
        self.progress.bind("<ButtonRelease-1>", self.on_slider_release)
        self.check_loop()

        # Create a menu for speed selection
        self.speed_menu = tk.Menu(self.root, tearoff=0)
        
        speeds = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
        for speed in speeds:
            self.speed_menu.add_radiobutton(label=f"{speed}x", 
                                            variable=self.playback_speed_var,
                                            value=speed, 
                                            command=lambda s=speed: self.playback_speed(s))

    def alt_t_pressed(self, event=None):
        self.add_timeframe_popup()

    def t_pressed(self, event=None):
        if self.is_media_loaded(self.player):
            self.show_timeframes()
        else:
            messagebox.showerror("No Media", "No media is available to show closed captions or subtitles.")

    def c_pressed(self, event=None):
        if self.is_media_loaded(self.player):
            self.select_subtitles()
        else:
            messagebox.showerror("No Media", "No media is available to show closed captions or subtitles.")

    def a_pressed(self, event=None):
        if self.is_media_loaded(self.player):
            self.select_audio()
        else:
            messagebox.showerror("No Media", "No media file is available to show audio track.")

    def playback_speed_menu(self):
        """Show the speed selection menu above the playback button (drop-up)."""
        x,y = self.root.winfo_pointerxy()
        self.speed_menu.post(x,y)

    def playback_speed(self, speed):
        if self.player and self.player.is_playing():
            self.player.set_rate(speed)
        else:
            messagebox.showerror("No Media", "No media found! Please open the media file first.")

    def zoomed_state(self):
        self.root.state('zoomed')

    def track_mouse_activity(self):
        """Continuously track mouse motion even when VLC is active."""
        current_position = self.root.winfo_pointerxy()  # Get mouse position
        
        if current_position != self.last_mouse_position:
            self.last_mouse_position = current_position
            self.reset_timer()  # Call reset function when mouse moves
        
        self.root.after(100, self.track_mouse_activity)  # Check again in 100ms

    def f_pressed(self, event=None):
        self.reset_timer()
        self.toggle_fullscreen()

    def esc_pressed(self, event=None):
        self.reset_timer()
        if self.fullscreen==True:
            self.toggle_fullscreen()

    def m_pressed(self, event=None):
        self.reset_timer()
        self.mute()

    def l_pressed(self, event=None):
        self.reset_timer()
        self.loop()

    def ctrl_l_pressed(self, event=None):
        self.reset_timer()
        self.load_media()

    def ctrl_u_pressed(self, event=None):
        self.reset_timer()
        self.load_url_media()

    def right_pressed(self, event=None):
        self.reset_timer()
        self.forward_10()

    def left_pressed(self, event=None):
        self.reset_timer()
        self.backward_10()

    def up_pressed(self, event=None):
        self.reset_timer()
        self.volume_up()

    def down_pressed(self,event=None):
        self.reset_timer()
        self.volume_down()

    def login(self):
        self.account_popup.destroy()
        self.login_popup = tk.Toplevel(self.root)
        self.login_popup.geometry('340x500')
        self.login_popup.configure(background='#292828')
        self.center_window(self.login_popup)

        self.login_popup.overrideredirect(True)

        canvas = Canvas(self.login_popup, bg = "#292828", height = 500, width = 340, bd = 0, highlightthickness = 0, relief = "ridge")

        canvas.place(x = 0, y = 0)
        image_image_1 = PhotoImage(file=relative_to_assets("login_icon.png"))
        image_1 = canvas.create_image(170.0, 68.0, image=image_image_1)

        entry_image_1 = PhotoImage(file=relative_to_assets("login_entry_1.png"))
        entry_bg_1 = canvas.create_image(169.5, 215.0, image=entry_image_1)
        self.login_entry_1 = Entry(canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.login_entry_1.place(x=54.0, y=200.0, width=231.0, height=28.0)

        self.login_entry_2 = Entry(canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.login_entry_2.place(x=54.0, y=278.0, width=231.0, height=28.0)

        canvas.create_text(105.0, 165.0, anchor="nw", text="User-Name", fill="#FF0000", font=("Inter", 24 * -1))

        canvas.create_text(114.0, 243.0, anchor="nw", text="Password", fill="#FF0000", font=("Inter", 24 * -1))

        button_image_1 = PhotoImage(file=relative_to_assets("login_button.png"))
        button_1 = Button(canvas, image=button_image_1, background='#292828', borderwidth=0, highlightthickness=0, command=lambda: self.login_button(), relief="flat")
        button_1.place(x=64.0, y=349.0, width=212.0, height=49.0)

        button_image_2 = PhotoImage(file=relative_to_assets("forgot_button.png"))
        button_2 = Button(canvas, image=button_image_2, background='#292828', borderwidth=0, highlightthickness=0, command=lambda: self.forgot_credential(), relief="flat")
        button_2.place(x=96.0, y=436.0, width=147.0, height=31.0)

        button_image_3 = PhotoImage(file=relative_to_assets("close_button.png"))
        button_3 = Button(canvas, image=button_image_3, background='#292828', borderwidth=0, highlightthickness=0, command=lambda: self.login_popup.destroy(), relief="flat")
        button_3.place(x=285.0, y=4.0, width=46.0, height=48.0)

        self.login_popup.mainloop()

    def forgot_credential(self):
        print("Forgot")
        self.login_popup.destroy()
        self.email_verify_popup = tk.Toplevel()
        self.email_verify_popup.geometry("523x163")
        self.email_verify_popup.overrideredirect(True)
        self.center_window(self.email_verify_popup)

        canvas = Canvas(
            self.email_verify_popup,
            bg = "#292828",
            height = 163,
            width = 523,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        canvas.place(x = 0, y = 0)
        canvas.create_text(
            12.0,
            8.0,
            anchor="nw",
            text="Email Verification",
            fill="#FF0000",
            font=("Inter Bold", 32 * -1)
        )
        canvas.create_text(
            12.0,
            73.0,
            anchor="nw",
            text="Enter Mail : ",
            fill="#FFFFFF",
            font=("Inter Bold", 20 * -1)
        )
        canvas.create_text(
            41.0,
            114.0,
            anchor="nw",
            text="OTP :",
            fill="#FFFFFF",
            font=("Inter Bold", 20 * -1)
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            256.5,
            84.5,
            image=entry_image_1
        )
        self.email_1 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.email_1.place(
            x=151.5,
            y=71.0,
            width=210.0,
            height=25.0
        )
        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            256.5,
            125.5,
            image=entry_image_2
        )
        self.password_2 = Entry(
            canvas,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.password_2.place(
            x=151.5,
            y=112.0,
            width=210.0,
            height=25.0
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("verify.png"))
        self.b1 = Button(
            canvas,
            image=button_image_1,
            background='#292828',
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.send_mail_otp(),
            relief="flat"
        )
        self.b1.place(
            x=392.0,
            y=71.0,
            width=117.0,
            height=27.0
        )

        button_image_2 = PhotoImage(
            file=relative_to_assets("submit.png"))
        self.b2 = Button(
            canvas,
            image=button_image_2,
            background='#292828',
            borderwidth=0,
            state='disabled',
            highlightthickness=0,
            command=lambda: self.verification_otp(),
            relief="flat"
        )
        self.b2.place(
            x=392.0,
            y=112.0,
            width=117.0,
            height=27.0
        )

        button_image_3 = PhotoImage(file=relative_to_assets("close_button.png"))
        self.b3 = Button(canvas, image=button_image_3, state="normal", background='#292828', borderwidth=0, highlightthickness=0, command=lambda: self.email_verify_popup.destroy(), relief="flat")
        self.b3.place(x=455.0, y=4.0, width=46.0, height=48.0)

        self.time_label = CTkLabel(canvas, text="00:00", bg_color='#292828', fg_color='#292828', font=("Inter Bold", 16))
        self.time_label.place(x=310, y=25)

        self.email_verify_popup.grab_set()
        self.email_verify_popup.mainloop()

    def update_timer_90(self):
        global remained_time
        if remained_time > 0:
            minutes = remained_time // 60
            seconds = remained_time % 60
            self.time_label.configure(text=f"{minutes:02}:{seconds:02}")
            remained_time -= 1
            self.root.after(1000, lambda : self.update_timer_90())  # Call this function again after 1 second
        else:
            self.time_label.configure(text="00:00")
            self.b1.configure(state="normal")
            self.b3.configure(state="normal")

    def start_count_down(self):
        global remained_time
        remained_time = 90  # 1 minute 30 seconds in total
        self.b1.configure(state="disabled")
        self.b3.configure(state="disabled")
        self.update_timer_90()

    def send_mail_otp(self):
        email = self.email_1.get()
        if email == "":
            messagebox.showerror("No OTP Found!!!", "Please enter an OTP.")
        else:
            response = Network.send_request("direct_otp_mail", email.lower())
            if response == '2':
                messagebox.showerror("Failed!!!", "OTP Generation Failed. Try Again!")
            else:
                self.b2.configure(state = 'normal')
                messagebox.showinfo("OTP", "OTP generated successfully.")
                self.start_count_down()

    def verification_otp(self):
        global remained_time
        e1 = self.email_1.get()
        e2 = self.password_2.get()
        if e1 == "":
            messagebox.showerror("No OTP Found!!!", "Please enter an OTP.")
        else:
            response = Network.send_request("email_otp_verification", e1, e2)
            if response == '0':
                messagebox.showinfo("Verification Successfull!", "OTP Verified Successfully.")
                remained_time = 0
                self.root.after(2000, lambda : self.email_verify_popup.destroy())
                New_Password_Popup(email=e1)
            elif response == '1':
                messagebox.showerror("Wrong OTP!!!", "OTP doesn't match. TRY AGAIN!")
            else:
                messagebox.showerror("Failed!!!", "Failed due to unexpected error. TRY AGAIN!")

    def login_button(self):
        e1 = self.login_entry_1.get()
        e2 = self.login_entry_2.get()
        response = Network.send_request("login", e1, e2)
        if response == '-1':
            messagebox.showerror("INVALID", "Incorrect Credentials. TRY AGAIN!")
        else:
            mlist = {}
            mlist = Network.movie_list_request("movie_list",e1,e2)
            self.login_popup.destroy()
            account.UNAME = e1
            account.PASSWORD = e2
            account.upload_popup(uname = e1, mlist = mlist, file_size = response)

    def signup(self):
        self.account_popup.destroy()
        close_image_3 = PhotoImage(file=relative_to_assets("close_button.png"))
        register.Register(img = close_image_3)

    def account(self):
        if account.UNAME == "" and account.PASSWORD == "":
            self.account_popup = tk.Toplevel(self.root)
            self.account_popup.geometry('620x280')
            self.account_popup.configure(background='#292828')
            self.center_window(self.account_popup)

            self.account_popup.overrideredirect(True)

            canvas = Canvas(
                self.account_popup,
                bg="#292828",
                height=280,
                width=620,
                bd=0,
                highlightthickness=0,
                relief="ridge"
            )
            canvas.place(x=0, y=0)
            canvas.create_text(
                10.0, 27.0, anchor="nw",
                text="ACCESS ACCOUNT=>",
                fill="#FFFFFF",
                font=("Inter", 32 * -1)
            )
            canvas.create_text(
                10.0, 131.0, anchor="nw",
                text="CREATE ACCOUNT=>",
                fill="#FFFFFF",
                font=("Inter", 32 * -1)
            )
            button_image_1 = PhotoImage(file=relative_to_assets("login.png"))
            button_1 = Button(
                canvas,
                image=button_image_1,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: self.login(),
                background='#292828',
                relief="flat"
            )
            button_1.place(x=350.0, y=23.0, width=257.0, height=48.0)
                
            button_image_2 = PhotoImage(file=relative_to_assets("signup.png"))
            button_2 = Button(
                canvas,
                image=button_image_2,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: self.signup(),
                background='#292828',
                relief="flat"
            )
            button_2.place(x=350.0, y=120.0, width=257.0, height=48.0)

            font = ctk.CTkFont(size=32, weight='bold')
            button_3 = Button(
                canvas,
                text = "CLOSE",
                fg = "#292828",
                font=font,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: self.account_popup.destroy(),
                background='#FF0000',
                relief="flat"
            )
            button_3.place(x=210, y=215, width=186, height=45)

            bip = Network.discover_server()
            print(bip)
            Network.B_IP = bip
                
            self.account_popup.mainloop()

        else:
            r1 = Network.send_request("file_size", account.UNAME, account.PASSWORD)
            print(r1)
            mlist = {}
            mlist = Network.movie_list_request("movie_list",account.UNAME,account.PASSWORD)
            account.upload_popup(uname = account.UNAME, mlist = mlist, file_size = r1)
                
    def menu(self):
        # Create a new popup menu
        popup = tk.Menu(self.root, tearoff=0)
        
        # Add Submenus
        popup.add_command(label="Subtitles", command=self.select_subtitles)
        popup.add_command(label="Audio", command=self.select_audio)
        popup.add_command(label="Time Frame", command=self.show_timeframes)

        # Display the menu at the current mouse position
        x, y = self.root.winfo_pointerxy()
        popup.tk_popup(x, y)

    def is_media_loaded(self, player):
        return player.get_media() is not None

    def option(self):
        if self.is_media_loaded(self.player):
            self.menu()
        else:
            messagebox.showerror("No Media", "No media found! Please open the media file first.")

    def get_current_media_name(self, player):
        """Get the name of the currently playing media file."""
        media = player.get_media()
        if media:
            mrl = media.get_mrl()  # Get the Media Resource Locator (MRL)
            file_name = mrl.split('/')[-1]  # Extract the file name from the path
            return file_name
        return None

    def get_current_playback_time(self, player):
        """Get the current playback time in seconds."""
        return player.get_time() // 1000  # Convert milliseconds to seconds

    def add_timeframe_popup(self):
        if self.is_media_loaded(self.player):
            self.reset_timer()
            if not self.paused:
                self.play_pause()
                    
            # Creating popup for adding timeframe
            add_tf_popup = tk.Toplevel(self.root)
            add_tf_popup.geometry("400x300")
            add_tf_popup.configure(background="#292828")
            self.center_window(add_tf_popup)
            add_tf_popup.overrideredirect(True)  # Remove the title bar ribbon

            # Getting media information where it is stopped
            mname = self.get_current_media_name(self.player)
            mtime = self.get_current_playback_time(self.player)

            # Creating Treeview
            style = ttk.Style()
            style.configure("Treeview",
                            background="#292828",
                            foreground="#ffffff",
                            fieldbackground="#292828",
                            font=("Arial", 10))
            style.configure("Treeview.Heading", background="#292828", foreground="black", font=("Arial", 10, "bold"))

            col = ['Field', 'Value']
            tree = ttk.Treeview(add_tf_popup, columns=col, show="headings", height=2)
            tree.heading('Field', text='Field')
            tree.heading('Value', text='Value')
            tree.column('Field', anchor='center', width=120)
            tree.column('Value', anchor='center', width=240)
           
            tree.insert("", tk.END, values=("Media Name", mname))
            tree.insert("", tk.END, values=("Time (s)", mtime))
            tree.pack(side='top', pady=10, padx=10, fill='x')

            # Adding Scene Name Label and Entry Box
            scene_label = tk.Label(add_tf_popup, text="Scene Name:", bg="#292828", fg="white", font=("Arial", 10))
            scene_label.pack(pady=(10, 5))

            scene_entry = tk.Entry(add_tf_popup, font=("Arial", 10), background='#292828', fg='#ffffff')
            scene_entry.pack(pady=5, padx=10, fill='x')

            # Adding Buttons
            button_frame = tk.Frame(add_tf_popup, bg="#292828")
            button_frame.pack(side='bottom', pady=10, fill='x')

            cancel_button = tk.Button(button_frame, text="Cancel", bg="#ff4d4d", fg="white", font=("Arial", 10),
                                      command=add_tf_popup.destroy)
            cancel_button.pack(side='left', padx=20, ipadx=10)

            save_button = tk.Button(button_frame, text="Save", bg="#4CAF50", fg="white", font=("Arial", 10),
                                    command=lambda: self.save_timeframe(mname, mtime, add_tf_popup, scene_entry.get()))
            save_button.pack(side='right', padx=20, ipadx=10)

            # Add a border around the popup (optional)
            add_tf_popup.update()
            add_tf_popup.geometry(f"+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")
        else:
            messagebox.showerror("No Media", "No media found! Please open the media file first.")

    def save_timeframe(self, mname, mtime, popup, sname='Scene'):
        print(sname)
        self.add_scene(mname, sname, mtime)
        popup.destroy()

    def initialize_data_file(self):
        """Initialize the movie data file if it doesn't exist."""
        data_file = os.path.expanduser("~/.movie_timeframes.json")  # File in the user's home directory
        if not os.path.exists(data_file):
            with open(data_file, "w") as file:
                json.dump({}, file)  # Create an empty dictionary
        return data_file

    def add_scene(self, movie_name, scene_name, timeframe):
        """Add a scene for a movie with its timeframe."""
        data_file = self.initialize_data_file()
        with open(data_file, "r") as file:
            data = json.load(file)

        # Ensure the movie entry exists
        if movie_name not in data:
            data[movie_name] = {}

        # Add or update the scene's timeframe
        data[movie_name][scene_name] = timeframe

        # Save the updated data back to the file
        with open(data_file, "w") as file:
            json.dump(data, file, indent=4)

    def get_scenes(self, movie_name):
        """Retrieve saved scenes for a movie."""
        data_file = self.initialize_data_file()
        with open(data_file, "r") as file:
            data = json.load(file)
        return data.get(movie_name, {})  # Return an empty dictionary if the movie is not found

    def show_timeframes(self):
        """Show a popup with all saved timeframes for the current media."""
        movie_name = self.get_current_media_name(self.player)
        scenes = self.get_scenes(movie_name)

        popup = tk.Toplevel(self.root)
        popup.geometry("400x300")
        popup.configure(background="#292828")
        popup.title(f"Scenes for {movie_name}")
        self.center_window(popup)

        # Remove title bar
        popup.overrideredirect(True)

        # Treeview styling
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#292828",
            foreground="white",
            fieldbackground="#292828",
            font=("Arial", 10)
        )
        style.configure("Treeview.Heading", background="#292828", foreground="black", font=("Arial", 10, "bold"))

        # Treeview for scenes
        columns = ["Scene Name", "Time (s)"]
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=10)
        tree.heading("Scene Name", text="Scene Name")
        tree.heading("Time (s)", text="Time (s)")
        tree.column("Scene Name", anchor="center", width=200)
        tree.column("Time (s)", anchor="center", width=150)
        tree.pack(pady=10, padx=10, expand=True, fill="both")

        # Insert data
        for scene_name, timeframe in scenes.items():
            tree.insert("", tk.END, values=(scene_name, timeframe))

        # Buttons
        button_frame = tk.Frame(popup, bg="#292828")
        button_frame.pack(side="bottom", pady=10, fill="x")

        exit_button = tk.Button(
            button_frame, text="Exit", bg="#ff4d4d", fg="white", font=("Arial", 10), command=popup.destroy
        )
        exit_button.pack(side="left", padx=10, ipadx=10)

        delete_button = tk.Button(
            button_frame, text="Delete", bg="#f4a261", fg="white", font=("Arial", 10),
            command=lambda: self.delete_scene(tree, movie_name, popup)
        )
        delete_button.pack(side="left", padx=10, ipadx=10)

        go_button = tk.Button(
            button_frame, text="Go", bg="#4CAF50", fg="white", font=("Arial", 10),
            command=lambda: self.jump_to_timeframe(tree, movie_name, popup)
        )
        go_button.pack(side="right", padx=10, ipadx=10)

    def jump_to_timeframe(self, tree, movie_name, popup):
        """Jump to a specific timeframe with audio for the given movie and scene."""
        selected_item = tree.selection()
        if selected_item:
            scene_name = tree.item(selected_item)["values"][0]
            tf = tree.item(selected_item)["values"][1]

        # Retrieve the timeframe for the specified scene
        #timeframe = self.get_timeframe(movie_name, scene_name)
        timeframe = int(tf)
        if timeframe is not None:
            # Ensure the media is loaded
            if self.is_media_loaded(self.player):
                # Convert timeframe to milliseconds and set player position
                self.player.set_time(int(timeframe) * 1000)
            
                # Play the media to ensure audio is active
                if not self.player.is_playing():
                    self.player.play()
            
                # Provide feedback
                print(f"Jumped to {timeframe} seconds in {movie_name} and started playing.")
            else:
                print("No media loaded. Unable to jump to timeframe.")
        else:
            print(f"Scene '{scene_name}' not found for movie '{movie_name}'.")

        popup.destroy()

    def delete_empty_movie(self, movie_name):
        """Check if a movie exists without any scenes and delete it if empty."""
        data_file = self.initialize_data_file()
    
        # Load existing data
        with open(data_file, "r") as file:
            data = json.load(file)

        # Check if the movie exists and has no scenes
        if movie_name in data and not data[movie_name]:  # Empty dictionary check
            del data[movie_name]  # Remove the movie entry

            # Save the updated data back to the file
            with open(data_file, "w") as file:
                json.dump(data, file, indent=4)


    def delete_scene(self, tree, movie_name, popup):
        """Delete the selected scene from the data file and update the treeview."""
        selected_item = tree.selection()
    
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a scene to delete.")
            return

        scene_name = tree.item(selected_item[0], "values")[0]  # Get selected scene name

        data_file = self.initialize_data_file()
    
        with open(data_file, "r") as file:
            data = json.load(file)

        # Check if movie and scene exist in data
        if movie_name in data and scene_name in data[movie_name]:
            del data[movie_name][scene_name]  # Delete the scene

            # Save updated data back to the file
            with open(data_file, "w") as file:
                json.dump(data, file, indent=4)

            # Remove the item from the treeview
            tree.delete(selected_item[0])
            tree.update_idletasks()  # Force update

            # Remove movie from JSON file if it has no scenes left
            self.delete_empty_movie(movie_name)

            messagebox.showinfo("Deleted", f"Scene '{scene_name}' deleted successfully.")
    
        else:
            messagebox.showerror("Error", "Scene not found.")

        popup.destroy()  # Close the popup

    def select_subtitles(self):
        subtitle_popup = tk.Toplevel(self.root)
        subtitle_popup.title("Select Subtitle Track")
        subtitle_popup.geometry("300x200")
        subtitle_popup.configure(bg="#292828")
        self.center_window(subtitle_popup)

        # Remove title bar
        subtitle_popup.overrideredirect(True)

        # Query available subtitle tracks
        subtitle_tracks = self.player.video_get_spu_description()
        if not subtitle_tracks:
            tk.Label(
                subtitle_popup,
                text="No subtitles available.",
                fg="white",
                bg="#292828",
                font=("Arial", 12),
            ).pack(pady=20)
            tk.Button(
                subtitle_popup,
                text="Close",
                command=subtitle_popup.destroy,
                bg="#444444",
                fg="white",
                font=("Arial", 10),
                relief="flat",
            ).pack(pady=10)
            return

        # Current subtitle track
        current_subtitle = self.player.video_get_spu()

        # Create radio buttons for each subtitle track
        tk.Label(
            subtitle_popup,
            text="Available Subtitle Tracks:",
            fg="white",
            bg="#292828",
            font=("Arial", 12),
        ).pack(pady=10)

        sframe = CTkScrollableFrame(subtitle_popup, width = 200, height = 80, bg_color='#292828', fg_color='#292828')
        sframe.pack()

        subtitle_var = tk.IntVar(value=current_subtitle)
        for track in subtitle_tracks:
            track_id, track_name = track
            tk.Radiobutton(
                sframe,
                text=track_name.decode("utf-8") if track_name else f"Track {track_id}",
                variable=subtitle_var,
                value=track_id,
                bg="#292828",
                fg="white",
                font=("Arial", 10),
                selectcolor="#444444",
                command=lambda: self.change_subtitle_track(subtitle_var.get()),
            ).pack(anchor="w", padx=20)

        # Add 'Disable' option
        tk.Radiobutton(
            sframe,
            text="Disable Subtitles",
            variable=subtitle_var,
            value=-1,  # ID for disabling subtitles
            bg="#292828",
            fg="white",
            font=("Arial", 10),
            selectcolor="#444444",
            command=lambda: self.disable_subtitles(),
        ).pack(anchor="w", padx = 20)
    
        # Add 'Load External Subtitles' option
        tk.Button(
            sframe,
            text="Load External Subtitles",
            command=lambda: self.load_external_subtitles(),
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            relief="flat",
        ).pack(pady=10)

        # Add a close button
        tk.Button(
            sframe,
            text="Close",
            command=subtitle_popup.destroy,
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            relief="flat",
        ).pack()
            
    def center_window(self, window):
        """Centers a Tkinter window relative to the main application window."""
        window.update_idletasks()

        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        popup_width = window.winfo_width()
        popup_height = window.winfo_height()

        pos_x = main_x + (main_width // 2) - (popup_width // 2)
        pos_y = main_y + (main_height // 2) - (popup_height // 2)

        window.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")

    def change_subtitle_track(self, track_id):
        """Change the subtitle track to the selected one."""
        result = self.player.video_set_spu(track_id)
        if result == -1:
            print("Failed to change the subtitle track.")
        else:
            print(f"Subtitle track changed to ID {track_id}.")

    def disable_subtitles(self):
        """Disable subtitles."""
        self.player.video_set_spu(-1)
        print("Subtitles disabled.")

    def load_external_subtitles(self):
        """Load external subtitles."""
        subtitle_path = filedialog.askopenfilename(filetypes=[("Subtitle Files", "*.srt;*.sub;*.txt")])
        if subtitle_path:
            try:
                self.player.video_set_subtitle_file(subtitle_path)
                print(f"Subtitles loaded: {os.path.basename(subtitle_path)}")
            except Exception as e:
                print(f"Failed to load subtitles: {e}")

    def select_audio(self):
        # Create a new popup for audio track selection
        audio_popup = tk.Toplevel(self.root)
        audio_popup.title("Select Audio Track")
        audio_popup.geometry("300x200")
        audio_popup.configure(bg="#292828")
        self.center_window(audio_popup)

        # Remove title bar
        audio_popup.overrideredirect(True)

        # Query available audio tracks
        track_description = self.player.audio_get_track_description()
        if not track_description:
            tk.Label(
                audio_popup,
                text="No audio tracks available.",
                fg="white",
                bg="#292828",
                font=("Arial", 12),
            ).pack(pady=20)
            tk.Button(
                audio_popup,
                text="Close",
                command=audio_popup.destroy,
                bg="#444444",
                fg="white",
                font=("Arial", 10),
                relief="flat",
            ).pack(pady=10)
            return

        # Current audio track
        current_track = self.player.audio_get_track()

        # Create radio buttons for each track
        tk.Label(
            audio_popup,
            text="Available Audio Tracks:",
            fg="white",
            bg="#292828",
            font=("Arial", 12),
        ).pack(pady=10)

        sframe = CTkScrollableFrame(audio_popup, bg_color='#292828', fg_color='#292828')
        sframe.pack()

        audio_var = tk.IntVar(value=current_track)  # Set the current track as selected
        for track in track_description:
            track_id, track_name = track
            tk.Radiobutton(
                sframe,
                text=track_name.decode("utf-8"),
                variable=audio_var,
                value=track_id,
                bg="#292828",
                fg="white",
                font=("Arial", 10),
                selectcolor="#444444",
                command=lambda: self.change_audio_track(audio_var.get()),
            ).pack(anchor="w", padx=20)

        # Add a close button
        tk.Button(
            sframe,
            text="Close",
            command=audio_popup.destroy,
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            relief="flat",
        ).pack(pady=20)

    def change_audio_track(self, track_id):
        """Change the audio track to the selected one."""
        result = self.player.audio_set_track(track_id)
        if result == -1:
            print("Failed to change the audio track.")
        else:
            print(f"Audio track changed to ID {track_id}.")
               
    def loop(self):
        """Toggle loop mode."""
        self.loop_var = not self.loop_var  # Toggle loop state
        if self.loop_var:
            self.loop_icon = PhotoImage(file=relative_to_assets("button_21.png"))  # Loop enabled icon
            self.loop_button.configure(image=self.loop_icon)
        else:
            self.loop_icon = PhotoImage(file=relative_to_assets("Button_5.png"))  # Loop disabled icon
            self.loop_button.configure(image=self.loop_icon)

    def check_loop(self):
        """Check if the video has ended and restart if loop mode is enabled."""
        if self.loop_var and self.playing:
            current_time = self.player.get_time()
            length = self.player.get_length()
            if current_time >= length - 500:  # Check if the video is close to ending
                self.player.set_time(0)  # Restart the video
                self.player.play()  # Ensure the video continues playing
        self.root.after(100, self.check_loop)  # Recheck every 100ms

    def mute(self):
        """Toggle mute state and update the UI accordingly."""
        if not self.mute_var:
            # Mute the audio
            self.player.audio_set_mute(True)
            self.volume_slider.set(0)  # Update the slider visually
            self.mute_icon = PhotoImage(file=relative_to_assets("button_3.png"))  # Muted icon
            self.mute_button.configure(image=self.mute_icon)
            self.mute_var = True
        else:
            # Unmute the audio and restore volume
            self.player.audio_set_mute(False)
            current_volume = self.player.audio_get_volume()
            self.volume_slider.set(current_volume)  # Restore volume on slider
            self.mute_icon = PhotoImage(file=relative_to_assets("button_1.png"))  # Unmuted icon
            self.mute_button.configure(image=self.mute_icon)
            self.mute_var = False

    def space_press(self, event=None):
        self.play_pause()
        self.reset_timer()

    def reset_timer(self, event=None):
        """Reset the inactivity timer when there is activity."""
        self.inactivity_timer = 0
        if not self.buttons_frame.winfo_ismapped():  # If the frame is hidden
            self.buttons_frame.pack(side="bottom", fill="x")  # Show the frame

    def check_inactivity(self):
        """Check for inactivity and hide the frame after a timeout."""
        self.inactivity_timer += 100  # Increment inactivity timer by 100ms
        if self.inactivity_timer >= self.hide_after:
            if self.buttons_frame.winfo_ismapped():  # If the frame is visible
                self.buttons_frame.pack_forget()  # Hide the frame
        # Schedule the next check
        self.root.after(100, self.check_inactivity)

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        current_state = self.root.attributes("-fullscreen")
        if current_state:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.root.overrideredirect(False)  # Show the title bar again
        else:
            self.fullscreen=True
            self.root.attributes("-fullscreen", True)
            self.root.overrideredirect(True)  # Hide the title bar

        if self.fullscreen==True:
            self.fullscreen_icon = PhotoImage(file = relative_to_assets("button_9.png"))
            self.fullscreen_button.configure(image=self.fullscreen_icon)
        else:
            self.fullscreen_icon = PhotoImage(file = relative_to_assets("button_2.png"))
            self.fullscreen_button.configure(image=self.fullscreen_icon)

    def play_pause(self):
        if self.paused:
            self.player.play()
            self.paused = False
            self.play_icon = PhotoImage(file = relative_to_assets("button_10.png"))
            self.play_button.configure(image=self.play_icon)
        elif self.playing:
            self.player.pause()
            self.paused = True
            self.play_icon = PhotoImage(file = relative_to_assets("button_4.png"))
            self.play_button.configure(image=self.play_icon)
        else:
            self.player.play()
            self.playing = True
            self.paused = False
            threading.Thread(target=self.update_video_frame).start()
            self.play_icon = PhotoImage(file = relative_to_assets("button_10.png"))
            self.play_button.configure(image=self.play_icon)

    def stop(self):
        self.player.stop()
        self.playing = False
        self.paused = False

    def load_media(self):
        """Load a media file (video or audio)."""
        filetypes = [
            ("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.flv"),
            ("Audio Files", "*.mp3;*.wav;*.aac;*.ogg;*.flac"),
        ]
        file_path = filedialog.askopenfilename(filetypes=filetypes, title="Select a Media File")
        if file_path:
            # Ensure VLC player instance is initialized
            if not hasattr(self, 'player') or self.player is None:
                print("VLC player was None! Creating a new one.")
                self.player = self.instance.media_player_new()
            media = self.instance.media_new(file_path)
            self.player.set_media(media)
            self.player.set_hwnd(self.panel.winfo_id())
            self.player.play()
            self.playing = True
            self.paused = False

            # Reset progress slider range for the new media
            self.progress.configure(to=100)  # Temporary placeholder, will be updated dynamically

    def show_loading_popup(self):
        """Display a loading popup with a progress bar."""
        self.loading_popup = tk.Toplevel(self.root)
        self.loading_popup.geometry("400x150")
        self.loading_popup.configure(bg="black")
        self.center_window(self.loading_popup)

        # Remove title bar
        self.loading_popup.overrideredirect(True)  

        # Center the popup
        self.loading_popup.update_idletasks()
        screen_width = self.loading_popup.winfo_screenwidth()
        screen_height = self.loading_popup.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 150) // 2
        self.loading_popup.geometry(f"400x150+{x}+{y}")

        # Display message
        label = tk.Label(
            self.loading_popup,
            text="Please wait!\nV-Player is loading the media.\nIt may take a few moments.",
            fg="white", bg="black",
            font=("Arial", 12),
            justify="center"
        )
        label.pack(pady=20)

        # Loading bar (indeterminate animation)
        self.progress_bar2 = ttk.Progressbar(self.loading_popup, mode="indeterminate", length=300)
        self.progress_bar2.pack(pady=10)
        self.progress_bar2.start(10)  # Start animation

        self.loading_popup.update()
            
    def close_loading_popup(self):
        """Close the loading popup."""
        if hasattr(self, 'loading_popup'):
            self.progress_bar2.stop()
            self.loading_popup.destroy()

    def load_url_media(self):
        if account.UNAME=="" and account.PASSWORD=="":
            messagebox.showerror("Not Logged In", "You need to login the account first to use this feature.")
            return
        else:
            bip = Network.discover_server()
            print(bip)
            Network.B_IP = bip

            movie_name = simpledialog.askstring("Input", "Enter movie user name and movie name (e.g., user_name/file_name, song.mp3):")
            if movie_name != None:
                def fetch_and_play():
                    try:
                        # Show loading popup
                        self.show_loading_popup()

                        # Encode filename to handle spaces and special characters
                        encoded_movie_name = urllib.parse.quote(movie_name)
                        
                        # Construct the streaming URL
                        server_url = f"http://{bip}:8000/{encoded_movie_name}"

                        print(f"Streaming from: {server_url}")

                        # Ensure VLC player instance is initialized
                        if not hasattr(self, 'player') or self.player is None:
                            print("VLC player was None! Creating a new one.")
                            self.player = self.instance.media_player_new()
                        # Load media and set it to VLC player
                        media = self.instance.media_new(server_url)
                        self.player.set_media(media)
                        self.player.set_hwnd(self.panel.winfo_id())
                        self.player.play()
                        self.playing = True
                        self.paused = False

                        # Wait until VLC starts playing
                        max_wait_time = 30  # Max 30 seconds to start playing
                        elapsed_time = 0

                        while self.player.get_state() not in [vlc.State.Playing, vlc.State.Ended] and elapsed_time < max_wait_time:
                            time.sleep(0.5)  # Check every 500ms
                            elapsed_time += 0.5
                                
                        # Close loading popup once the media starts playing
                        if self.player.get_state() == vlc.State.Playing:
                            print("Media started playing, closing popup.")
                        else:
                            print("Media failed to start within time limit.")

                    except Exception as e:
                        print(f"Error: here {e}")

                    finally:
                        self.close_loading_popup()  # Close popup regardless of success or failure

                # Run fetching process in a separate thread
                threading.Thread(target=fetch_and_play, daemon=True).start()

    def set_volume(self, volume):
        #self.player.audio_set_volume(int(volume))
        volume = int(volume)
        self.player.audio_set_volume(volume)
        if volume > 0:
            # If the volume is increased from 0, unmute
            self.mute_var = False
            self.player.audio_set_mute(False)
            self.mute_icon = PhotoImage(file=relative_to_assets("button_1.png"))  # Unmuted icon
            self.mute_button.configure(image=self.mute_icon)
        else:
            # If the volume is set to 0, consider it muted
            self.mute_var = True
            self.player.audio_set_mute(True)
            self.mute_icon = PhotoImage(file=relative_to_assets("button_3.png"))  # Muted icon
            self.mute_button.configure(image=self.mute_icon)

    def set_progress(self, value):
        """Jump to a specific section when the progress slider is moved."""
        if self.user_interacting:  # Only update when the user is actively interacting
            jump_time = int(float(value) * 1000)  # Convert seconds to milliseconds
            self.player.set_time(jump_time)

    def on_slider_click(self, event):
        """Mark the slider as being interacted with."""
        self.user_interacting = True

    def on_slider_release(self, event):
        """Mark the slider as no longer being interacted with."""
        self.user_interacting = False
        self.set_progress(self.progress.get())

    def on_closing(self):
        if self.player.is_playing():
            self.player.stop()
            self.stop()
        self.player.release()  # Release the VLC player instance
        self.instance.release()  # Release the VLC instance
        self.root.quit()  # Ensure Tkinter event loop exits
        self.root.destroy()  # Destroy the window immediately

    def update_progress(self):
        """Update the progress slider to reflect the current playback position."""
        if self.playing and not self.user_interacting:
            length = self.player.get_length() / 1000  # Media length in seconds
            current_time = self.player.get_time() / 1000  # Current playback time in seconds

            if length > 0:
                self.progress.configure(to=length)  # Dynamically set the slider's maximum value
                self.progress.set(current_time)

                # Format the time values to HH:MM:SS
                current_time_formatted = self.format_time(current_time)
                length_formatted = self.format_time(length)

                # Update the time label
                self.time_label.config(text=f"{current_time_formatted} / {length_formatted}")

        self.root.after(500, self.update_progress)  # Update every 500ms

    def update_video_frame(self):
        """Update the video frame (if necessary) in the future."""
        while self.playing:
            self.root.update_idletasks()

    def format_time(self, seconds):
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"

    def forward_10(self):
        """Move forward 10 seconds in the media."""
        current_time = self.player.get_time()  # Get current playback time in milliseconds
        new_time = current_time + 10000  # Add 10 seconds (10,000 milliseconds)
        media_length = self.player.get_length()  # Get the total length of the media
        if new_time < media_length:  # Ensure it doesn't exceed media length
            self.player.set_time(new_time)  # Set the new playback time
        else:
            self.player.set_time(media_length - 1)  # Set to near the end if exceeded

    def backward_10(self):
        """Move backward 10 seconds in the media."""
        current_time = self.player.get_time()  # Get current playback time in milliseconds
        new_time = current_time - 10000  # Subtract 10 seconds (10,000 milliseconds)
        if new_time > 0:  # Ensure it doesn't go below 0
            self.player.set_time(new_time)  # Set the new playback time
        else:
            self.player.set_time(0)  # Set to the start if negative

    def volume_up(self):
        """Increase the volume by 1."""
        current_volume = self.player.audio_get_volume()
        if current_volume < 100:  # Ensure volume does not exceed 100%
            new_volume = current_volume + 1
            self.player.audio_set_volume(new_volume)
            self.volume_slider.set(new_volume)  # Update the volume slider

    def volume_down(self):
        """Decrease the volume by 1."""
        current_volume = self.player.audio_get_volume()
        if current_volume > 0:  # Ensure volume does not go below 0%
            new_volume = current_volume - 1
            self.player.audio_set_volume(new_volume)
            self.volume_slider.set(new_volume)  # Update the volume slider

    def titlebarcolor(window):
        try:
            hwnd = windll.user32.GetParent(window.winfo_id())

            # Set custom title bar color (#292828)
            DWMWA_ATTRIBUTE_COLOR = 35
            COLOR = int(0x000000)  # Convert HEX to integer
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_ATTRIBUTE_COLOR, byref(c_int(COLOR)), sizeof(c_int))

            # Set white title bar text color
            DWMWA_ATTRIBUTE_TEXT = 36  # Title bar text color
            TEXT_COLOR = ctypes.c_int(0xFFFFFF)  #c_int(1)   1 = Light mode (White text)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_ATTRIBUTE_TEXT, byref(TEXT_COLOR), sizeof(TEXT_COLOR))

        except Exception as e:
            pass

if __name__ == '__main__':
    root = ctk.CTk()
    app = MediaPlayer(root)
    root.mainloop()
