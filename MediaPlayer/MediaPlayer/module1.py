from pathlib import Path
import tkinter as tk
from tkinter import filedialog, simpledialog, PhotoImage, Canvas, ttk, messagebox
import vlc
import threading
from customtkinter import CTkSlider, CTkOptionMenu
import customtkinter as ctk
import os
import json
from ctypes.wintypes import HWND
from ctypes import alignment, windll, byref, c_int, sizeof
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999

# Define paths for assets
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Varun\OneDrive\Desktop\MediaPlayer\Media_assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class MediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.geometry('800x600')
        self.root.title("V-Player")
        self.root.iconbitmap('V-Player-Logo.ico')
        self.root.after(100, lambda: self.titlebarcolor())
        self.root.after(100, lambda : self.zoomed_state())

        # Video display panel
        self.panel = tk.Label(self.root, background="#292828") 
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
        self.root.bind_all('<F>', self.f_pressed)
        self.root.bind_all('<f>', self.f_pressed)
        self.root.bind_all('<Escape>', self.esc_pressed)
        self.root.bind_all('<M>', self.m_pressed)
        self.root.bind_all('<m>', self.m_pressed)
        self.root.bind_all('<L>', self.l_pressed)
        self.root.bind_all('<l>', self.l_pressed)
        self.root.bind_all('<Control-L>', self.ctrl_l_pressed)
        self.root.bind_all('<Control-l>', self.ctrl_l_pressed)
        self.root.bind_all('<Control-U>', self.ctrl_u_pressed)
        self.root.bind_all('<Control-u>', self.ctrl_u_pressed)
        self.root.bind_all('<Right>', self.right_pressed)
        self.root.bind_all('<Left>', self.left_pressed)
        self.root.bind_all('<Up>', self.up_pressed)
        self.root.bind_all('<Down>', self.down_pressed)
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
            style.configure("Treeview.Heading", background="#292828", foreground="white", font=("Arial", 10, "bold"))

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

        # Treeview styling
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#292828",
            foreground="white",
            fieldbackground="#292828",
            font=("Arial", 10)
        )
        style.configure("Treeview.Heading", background="#292828", foreground="white", font=("Arial", 10, "bold"))

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
        if selected_item:
            scene_name = tree.item(selected_item)["values"][0]  # Get the selected scene name
            data_file = self.initialize_data_file()
            with open(data_file, "r") as file:
                data = json.load(file)

            if movie_name in data and scene_name in data[movie_name]:
                del data[movie_name][scene_name]  # Delete the scene
                    
                # Save the updated data back to the file
                with open(data_file, "w") as file:
                    json.dump(data, file, indent=4)

                # Remove the item from the treeview
                tree.delete(selected_item)

                #Remove moive name from json file if it has no scene
                self.delete_empty_movie(movie_name)

            popup.destroy()

    def select_subtitles(self):
        subtitle_popup = tk.Toplevel(self.root)
        subtitle_popup.title("Select Subtitle Track")
        subtitle_popup.geometry("300x200")
        subtitle_popup.configure(bg="#292828")

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

        subtitle_var = tk.IntVar(value=current_subtitle)
        for track in subtitle_tracks:
            track_id, track_name = track
            tk.Radiobutton(
                subtitle_popup,
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
            subtitle_popup,
            text="Disable Subtitles",
            variable=subtitle_var,
            value=-1,  # ID for disabling subtitles
            bg="#292828",
            fg="white",
            font=("Arial", 10),
            selectcolor="#444444",
            command=lambda: self.disable_subtitles(),
        ).pack(anchor="w", padx=20)
    
        # Add 'Load External Subtitles' option
        tk.Button(
            subtitle_popup,
            text="Load External Subtitles",
            command=lambda: self.load_external_subtitles(),
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            relief="flat",
        ).pack(pady=10)

        # Add a close button
        tk.Button(
            subtitle_popup,
            text="Close",
            command=subtitle_popup.destroy,
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            relief="flat",
        ).pack(pady=20)

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

        audio_var = tk.IntVar(value=current_track)  # Set the current track as selected
        for track in track_description:
            track_id, track_name = track
            tk.Radiobutton(
                audio_popup,
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
            audio_popup,
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
            media = self.instance.media_new(file_path)
            self.player.set_media(media)
            self.player.set_hwnd(self.panel.winfo_id())
            self.playing = False
            self.paused = False

            # Reset progress slider range for the new media
            self.progress.configure(to=100)  # Temporary placeholder, will be updated dynamically

    def show_loading_popup(self):
        """Display a loading popup with a progress bar."""
        self.loading_popup = tk.Toplevel(self.root)
        self.loading_popup.geometry("400x150")
        self.loading_popup.configure(bg="black")

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
        movie_name = simpledialog.askstring("Input", "Enter movie filename (e.g., Murder.On.The.Orient.Express.2017.1080p.BluRay.Dual.mkv):")
    
        if movie_name:
            def fetch_media():
                try:
                    # Show loading popup
                    self.show_loading_popup()
                
                    # Connect to the server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((SERVER_HOST, SERVER_PORT))
                    client_socket.sendall(movie_name.encode())  # Send filename to server
                
                    # Receive the streamed video
                    with open("received_video.mp4", "wb") as file:
                        while True:
                            data = client_socket.recv(4096)
                            if not data:
                                break
                            file.write(data)

                    client_socket.close()
                    print("Video received successfully.")

                    # Load the received media into VLC
                    media = self.instance.media_new("received_video.mp4")
                    self.player.set_media(media)
                    self.player.set_hwnd(self.panel.winfo_id())
                    self.playing = False
                    self.paused = False

                except Exception as e:
                    print(f"Error: {e}")

                finally:
                    self.close_loading_popup()  # Close loading popup when done

            # Run the fetching process in a separate thread
            threading.Thread(target=fetch_media, daemon=True).start()

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

    def titlebarcolor(self):
        try:
            hwnd = windll.user32.GetParent(self.root.winfo_id())

            # Set custom title bar color (#292828)
            DWMWA_ATTRIBUTE_COLOR = 35
            COLOR = int(0x292828)  # Convert HEX to integer
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_ATTRIBUTE_COLOR, byref(c_int(COLOR)), sizeof(c_int))

            # Set white title bar text color
            DWMWA_ATTRIBUTE_TEXT = 36  # Title bar text color
            TEXT_COLOR = int(0xffffff)  #c_int(1)   1 = Light mode (White text)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_ATTRIBUTE_TEXT, byref(TEXT_COLOR), sizeof(TEXT_COLOR))

        except Exception as e:
            print(f"Failed to set title bar color: {e}")

if __name__ == '__main__':
    root = ctk.CTk()
    app = MediaPlayer(root)
    root.mainloop()
