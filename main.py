import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import os
import util
import numpy as np
from PIL import Image, ImageTk
import threading
import time

class BiometricApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Biometric Authentication System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#191c24")
        
        # Set theme colors
        self.primary_color = "#6c63ff"      # Purple
        self.secondary_color = "#03dac6"    # Teal
        self.bg_color = "#191c24"           # Dark blue-gray
        self.text_color = "#ffffff"         # White
        self.error_color = "#cf6679"        # Pinkish-red
        self.success_color = "#03dac6"      # Teal
        
        # Load and set window icon
        icon_dir = "./assets"
        os.makedirs(icon_dir, exist_ok=True)
        
        # Initialize camera preview
        self.is_camera_active = False
        self.camera_thread = None
        self.stop_camera = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, 
                            text="BIOMETRIC AUTHENTICATION", 
                            font=("Helvetica", 24, "bold"), 
                            fg=self.primary_color, 
                            bg=self.bg_color)
        title_label.pack(side="left")
        
        # Create tab control
        self.tab_control = ttk.Notebook(main_frame)
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_create("custom_theme", parent="alt", settings={
            "TNotebook": {"configure": {"background": self.bg_color, "tabmargins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {
                "configure": {"padding": [10, 5], "background": self.bg_color, "foreground": self.text_color},
                "map": {"background": [("selected", self.primary_color)],
                        "foreground": [("selected", self.text_color)],
                        "expand": [("selected", [1, 1, 1, 0])]}
            },
            "TFrame": {"configure": {"background": self.bg_color}},
            "TLabel": {"configure": {"background": self.bg_color, "foreground": self.text_color}},
            "TButton": {"configure": {"font": ("Helvetica", 12), "background": self.primary_color}}
        })
        style.theme_use("custom_theme")
        
        # Create tabs
        register_tab = ttk.Frame(self.tab_control)
        verify_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(register_tab, text="Register")
        self.tab_control.add(verify_tab, text="Verify")
        self.tab_control.pack(expand=1, fill="both")
        
        # Register Tab
        self.setup_register_tab(register_tab)
        
        # Verify Tab
        self.setup_verify_tab(verify_tab)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.bg_color, height=30)
        status_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        self.status_label = tk.Label(status_frame, 
                                text="Ready", 
                                fg=self.text_color, 
                                bg=self.bg_color, 
                                anchor="w")
        self.status_label.pack(fill="x", side="left")
        
        # Version info
        version_label = tk.Label(status_frame, 
                              text="v1.0.0", 
                              fg=self.text_color, 
                              bg=self.bg_color, 
                              anchor="e")
        version_label.pack(fill="x", side="right")
    
    def setup_register_tab(self, parent):
        # Left panel - Form
        left_panel = tk.Frame(parent, bg=self.bg_color)
        left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Username entry
        username_frame = tk.Frame(left_panel, bg=self.bg_color)
        username_frame.pack(fill="x", pady=10)
        
        username_label = tk.Label(username_frame, 
                               text="Username", 
                               font=("Helvetica", 12), 
                               fg=self.text_color, 
                               bg=self.bg_color, 
                               anchor="w")
        username_label.pack(fill="x")
        
        self.register_username_entry = tk.Entry(username_frame, 
                                          font=("Helvetica", 12), 
                                          bg="#2d3035", 
                                          fg=self.text_color, 
                                          insertbackground=self.text_color, 
                                          relief="flat", 
                                          highlightthickness=1, 
                                          highlightcolor=self.primary_color, 
                                          highlightbackground="#2d3035")
        self.register_username_entry.pack(fill="x", ipady=5)
        
        # Instructions
        instructions_frame = tk.Frame(left_panel, bg=self.bg_color)
        instructions_frame.pack(fill="x", pady=20)
        
        instructions_label = tk.Label(instructions_frame, 
                                   text="Registration Process:", 
                                   font=("Helvetica", 12, "bold"), 
                                   fg=self.primary_color, 
                                   bg=self.bg_color, 
                                   anchor="w")
        instructions_label.pack(fill="x")
        
        steps_text = "1. Enter your username\n2. Click 'Capture Face' to record your face\n3. Click 'Record Voice' to save your voice\n4. Click 'Register' to complete"
        steps_label = tk.Label(instructions_frame, 
                            text=steps_text, 
                            font=("Helvetica", 11), 
                            fg=self.text_color, 
                            bg=self.bg_color, 
                            justify="left", 
                            anchor="w")
        steps_label.pack(fill="x", pady=5)
        
        # Register button
        btn_frame = tk.Frame(left_panel, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=20)
        
        self.capture_face_btn = tk.Button(btn_frame, 
                                     text="Capture Face", 
                                     font=("Helvetica", 12), 
                                     bg=self.secondary_color, 
                                     fg="#191c24", 
                                     activebackground=self.primary_color, 
                                     activeforeground=self.text_color, 
                                     relief="flat", 
                                     padx=15, 
                                     pady=8, 
                                     command=self.start_face_capture_reg)
        self.capture_face_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.record_voice_btn = tk.Button(btn_frame, 
                                     text="Record Voice", 
                                     font=("Helvetica", 12), 
                                     bg=self.secondary_color, 
                                     fg="#191c24", 
                                     activebackground=self.primary_color, 
                                     activeforeground=self.text_color, 
                                     relief="flat", 
                                     padx=15, 
                                     pady=8, 
                                     command=self.record_voice_reg)
        self.record_voice_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        register_btn = tk.Button(left_panel, 
                              text="Register", 
                              font=("Helvetica", 14, "bold"), 
                              bg=self.primary_color, 
                              fg=self.text_color, 
                              activebackground=self.secondary_color, 
                              activeforeground="#191c24", 
                              relief="flat", 
                              padx=20, 
                              pady=10, 
                              command=self.register_new_user)
        register_btn.pack(fill="x", pady=20)
        
        # Right panel - Preview
        right_panel = tk.Frame(parent, bg=self.bg_color)
        right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        preview_label = tk.Label(right_panel, 
                              text="Camera Preview", 
                              font=("Helvetica", 12, "bold"), 
                              fg=self.primary_color, 
                              bg=self.bg_color)
        preview_label.pack(pady=(0, 10))
        
        self.reg_preview_frame = tk.Label(right_panel, bg="#2d3035", width=300, height=300)
        self.reg_preview_frame.pack(pady=10)
        
        self.reg_status_text = tk.StringVar()
        self.reg_status_text.set("No face captured")
        
        status_label = tk.Label(right_panel, 
                             textvariable=self.reg_status_text, 
                             font=("Helvetica", 10), 
                             fg=self.text_color, 
                             bg=self.bg_color)
        status_label.pack(pady=10)
    
    def setup_verify_tab(self, parent):
        # Left panel - Form
        left_panel = tk.Frame(parent, bg=self.bg_color)
        left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Username entry
        username_frame = tk.Frame(left_panel, bg=self.bg_color)
        username_frame.pack(fill="x", pady=10)
        
        username_label = tk.Label(username_frame, 
                               text="Username", 
                               font=("Helvetica", 12), 
                               fg=self.text_color, 
                               bg=self.bg_color, 
                               anchor="w")
        username_label.pack(fill="x")
        
        self.verify_username_entry = tk.Entry(username_frame, 
                                        font=("Helvetica", 12), 
                                        bg="#2d3035", 
                                        fg=self.text_color, 
                                        insertbackground=self.text_color, 
                                        relief="flat", 
                                        highlightthickness=1, 
                                        highlightcolor=self.primary_color, 
                                        highlightbackground="#2d3035")
        self.verify_username_entry.pack(fill="x", ipady=5)
        
        # Instructions
        instructions_frame = tk.Frame(left_panel, bg=self.bg_color)
        instructions_frame.pack(fill="x", pady=20)
        
        instructions_label = tk.Label(instructions_frame, 
                                   text="Verification Process:", 
                                   font=("Helvetica", 12, "bold"), 
                                   fg=self.primary_color, 
                                   bg=self.bg_color, 
                                   anchor="w")
        instructions_label.pack(fill="x")
        
        steps_text = "1. Enter your username\n2. Click 'Capture Face' to verify your face\n3. Click 'Record Voice' to verify your voice\n4. Click 'Verify' to authenticate"
        steps_label = tk.Label(instructions_frame, 
                            text=steps_text, 
                            font=("Helvetica", 11), 
                            fg=self.text_color, 
                            bg=self.bg_color, 
                            justify="left", 
                            anchor="w")
        steps_label.pack(fill="x", pady=5)
        
        # Verify buttons
        btn_frame = tk.Frame(left_panel, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=20)
        
        self.capture_face_verify_btn = tk.Button(btn_frame, 
                                           text="Capture Face", 
                                           font=("Helvetica", 12), 
                                           bg=self.secondary_color, 
                                           fg="#191c24", 
                                           activebackground=self.primary_color, 
                                           activeforeground=self.text_color, 
                                           relief="flat", 
                                           padx=15, 
                                           pady=8, 
                                           command=self.start_face_capture_verify)
        self.capture_face_verify_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.record_voice_verify_btn = tk.Button(btn_frame, 
                                           text="Record Voice", 
                                           font=("Helvetica", 12), 
                                           bg=self.secondary_color, 
                                           fg="#191c24", 
                                           activebackground=self.primary_color, 
                                           activeforeground=self.text_color, 
                                           relief="flat", 
                                           padx=15, 
                                           pady=8, 
                                           command=self.record_voice_verify)
        self.record_voice_verify_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        verify_btn = tk.Button(left_panel, 
                            text="Verify", 
                            font=("Helvetica", 14, "bold"), 
                            bg=self.primary_color, 
                            fg=self.text_color, 
                            activebackground=self.secondary_color, 
                            activeforeground="#191c24", 
                            relief="flat", 
                            padx=20, 
                            pady=10, 
                            command=self.verify_user)
        verify_btn.pack(fill="x", pady=20)
        
        # Right panel - Preview
        right_panel = tk.Frame(parent, bg=self.bg_color)
        right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        preview_label = tk.Label(right_panel, 
                              text="Camera Preview", 
                              font=("Helvetica", 12, "bold"), 
                              fg=self.primary_color, 
                              bg=self.bg_color)
        preview_label.pack(pady=(0, 10))
        
        self.verify_preview_frame = tk.Label(right_panel, bg="#2d3035", width=300, height=300)
        self.verify_preview_frame.pack(pady=10)
        
        self.verify_status_text = tk.StringVar()
        self.verify_status_text.set("No verification performed")
        
        self.verify_status_label = tk.Label(right_panel, 
                                       textvariable=self.verify_status_text, 
                                       font=("Helvetica", 10), 
                                       fg=self.text_color, 
                                       bg=self.bg_color)
        self.verify_status_label.pack(pady=10)
        
        # Score display frame
        self.scores_frame = tk.Frame(right_panel, bg=self.bg_color)
        self.scores_frame.pack(fill="x", pady=10)
        
        # Face score
        self.face_score_var = tk.StringVar()
        self.face_score_var.set("Face: N/A")
        face_score_label = tk.Label(self.scores_frame, 
                                 textvariable=self.face_score_var, 
                                 font=("Helvetica", 10), 
                                 fg=self.text_color, 
                                 bg=self.bg_color)
        face_score_label.pack(side="left", expand=True)
        
        # Voice score
        self.voice_score_var = tk.StringVar()
        self.voice_score_var.set("Voice: N/A")
        voice_score_label = tk.Label(self.scores_frame, 
                                  textvariable=self.voice_score_var, 
                                  font=("Helvetica", 10), 
                                  fg=self.text_color, 
                                  bg=self.bg_color)
        voice_score_label.pack(side="right", expand=True)
        
        # Progress bars
        self.face_progress = ttk.Progressbar(right_panel, orient="horizontal", length=140, mode="determinate")
        self.face_progress.pack(pady=(5, 0))
        
        self.voice_progress = ttk.Progressbar(right_panel, orient="horizontal", length=140, mode="determinate")
        self.voice_progress.pack(pady=(5, 0))
    
    # Camera handling methods
    def start_camera_stream(self, target_label, action_type):
        if self.is_camera_active:
            return
            
        self.is_camera_active = True
        self.stop_camera = False
        
        def camera_stream():
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not cap.isOpened():
                self.update_status("❌ ERROR: Could not access the camera!", is_error=True)
                self.is_camera_active = False
                return
                
            countdown = 3
            countdown_start = time.time()
            show_countdown = True
            frames_captured = 0
            best_frame = None
            
            while not self.stop_camera:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert frame to RGB for tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Add countdown if needed
                current_time = time.time()
                if show_countdown and current_time - countdown_start > 1:
                    countdown -= 1
                    countdown_start = current_time
                    
                    if countdown <= 0:
                        show_countdown = False
                        frames_captured = 0
                
                # Display countdown or frame number
                if show_countdown:
                    cv2.putText(rgb_frame, str(countdown), (int(frame.shape[1]/2)-50, int(frame.shape[0]/2)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)
                elif frames_captured < 5:
                    frames_captured += 1
                    best_frame = frame.copy()  # Save the current frame
                    cv2.putText(rgb_frame, f"Capturing... {frames_captured}/5", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Draw green border when capturing
                    rgb_frame = cv2.rectangle(rgb_frame, (0, 0), (rgb_frame.shape[1]-1, rgb_frame.shape[0]-1), 
                                             (0, 255, 0), 5)
                    
                    if frames_captured >= 5:
                        # Save the captured frame
                        if action_type == "register":
                            username = self.register_username_entry.get().strip()
                            user_dir = f"./db/{username}"
                            os.makedirs(user_dir, exist_ok=True)
                            face_path = os.path.join(user_dir, "face.jpg")
                            cv2.imwrite(face_path, best_frame)
                            self.reg_face_path = face_path
                            self.reg_status_text.set("✅ Face captured successfully!")
                        else:  # verify
                            face_path = "./temp_face.jpg"
                            cv2.imwrite(face_path, best_frame)
                            self.verify_face_path = face_path
                            self.verify_status_text.set("✅ Face captured successfully!")
                        
                        # Stop camera after capturing
                        self.stop_camera = True
                        break
                
                # Resize for display
                pil_img = Image.fromarray(rgb_frame)
                pil_img = pil_img.resize((300, 300), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=pil_img)
                
                # Update the label
                target_label.imgtk = imgtk
                target_label.configure(image=imgtk)
                
                self.root.update()
                
            cap.release()
            self.is_camera_active = False
        
        # Start the camera in a separate thread
        self.camera_thread = threading.Thread(target=camera_stream)
        self.camera_thread.daemon = True
        self.camera_thread.start()
    
    def start_face_capture_reg(self):
        username = self.register_username_entry.get().strip()
        if not username:
            self.show_error("Username cannot be empty!")
            return
            
        self.reg_status_text.set("Looking at the camera...")
        self.start_camera_stream(self.reg_preview_frame, "register")
        
    def start_face_capture_verify(self):
        username = self.verify_username_entry.get().strip()
        if not username:
            self.show_error("Username cannot be empty!")
            return
            
        self.verify_status_text.set("Looking at the camera...")
        self.start_camera_stream(self.verify_preview_frame, "verify")
        
    def record_voice_reg(self):
        username = self.register_username_entry.get().strip()
        if not username:
            self.show_error("Username cannot be empty!")
            return
            
        user_dir = f"./db/{username}"
        os.makedirs(user_dir, exist_ok=True)
        voice_path = os.path.join(user_dir, "voice.wav")
        
        phrase = "Hello, this is a test phrase."
        self.update_status(f"Say the phrase: {phrase}")
        
        # Create custom dialog for voice recording
        dialog = tk.Toplevel(self.root)
        dialog.title("Voice Recording")
        dialog.geometry("400x250")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, 
                                  self.root.winfo_rooty() + 50))
        
        tk.Label(dialog, 
              text="Voice Recording", 
              font=("Helvetica", 16, "bold"), 
              fg=self.primary_color, 
              bg=self.bg_color).pack(pady=(20, 10))
        
        tk.Label(dialog, 
              text=f"Please say the following phrase:", 
              font=("Helvetica", 12), 
              fg=self.text_color, 
              bg=self.bg_color).pack(pady=5)
        
        tk.Label(dialog, 
              text=f'"{phrase}"', 
              font=("Helvetica", 14, "italic"), 
              fg=self.secondary_color, 
              bg=self.bg_color).pack(pady=10)
        
        timer_var = tk.StringVar()
        timer_var.set("5")
        timer_label = tk.Label(dialog, 
                            textvariable=timer_var, 
                            font=("Helvetica", 24), 
                            fg=self.text_color, 
                            bg=self.bg_color)
        timer_label.pack(pady=10)
        
        # Start recording process
        def start_recording():
            for i in range(5, 0, -1):
                timer_var.set(str(i))
                dialog.update()
                time.sleep(1)
                
            timer_var.set("Recording...")
            dialog.update()
            
            # Record audio
            util.record_audio(voice_path, phrase)
            
            timer_var.set("Done!")
            dialog.update()
            time.sleep(1)
            dialog.destroy()
            
            self.reg_status_text.set("✅ Voice recorded successfully!")
            
        threading.Thread(target=start_recording, daemon=True).start()
        
    def record_voice_verify(self):
        username = self.verify_username_entry.get().strip()
        if not username:
            self.show_error("Username cannot be empty!")
            return
            
        user_dir = f"./db/{username}"
        if not os.path.exists(user_dir):
            self.show_error("User not found! Register first.")
            return
            
        voice_path = "./temp_voice.wav"
        phrase = "Hello, this is a test phrase."
        
        # Create custom dialog for voice recording
        dialog = tk.Toplevel(self.root)
        dialog.title("Voice Recording")
        dialog.geometry("400x250")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, 
                                  self.root.winfo_rooty() + 50))
        
        tk.Label(dialog, 
              text="Voice Verification", 
              font=("Helvetica", 16, "bold"), 
              fg=self.primary_color, 
              bg=self.bg_color).pack(pady=(20, 10))
        
        tk.Label(dialog, 
              text=f"Please say the following phrase:", 
              font=("Helvetica", 12), 
              fg=self.text_color, 
              bg=self.bg_color).pack(pady=5)
        
        tk.Label(dialog, 
              text=f'"{phrase}"', 
              font=("Helvetica", 14, "italic"), 
              fg=self.secondary_color, 
              bg=self.bg_color).pack(pady=10)
        
        timer_var = tk.StringVar()
        timer_var.set("5")
        timer_label = tk.Label(dialog, 
                            textvariable=timer_var, 
                            font=("Helvetica", 24), 
                            fg=self.text_color, 
                            bg=self.bg_color)
        timer_label.pack(pady=10)
        
        # Start recording process
        def start_recording():
            for i in range(5, 0, -1):
                timer_var.set(str(i))
                dialog.update()
                time.sleep(1)
                
            timer_var.set("Recording...")
            dialog.update()
            
            # Record audio
            util.record_audio(voice_path, phrase)
            self.verify_voice_path = voice_path
            
            timer_var.set("Done!")
            dialog.update()
            time.sleep(1)
            dialog.destroy()
            
            self.verify_status_text.set("✅ Voice recorded successfully!")
            
        threading.Thread(target=start_recording, daemon=True).start()
    
    def register_new_user(self):
        username = self.register_username_entry.get().strip()
        if not username:
            self.show_error("Username cannot be empty!")
            return
            
        user_dir = f"./db/{username}"
        os.makedirs(user_dir, exist_ok=True)
        
        face_path = os.path.join(user_dir, "face.jpg")
        voice_path = os.path.join(user_dir, "voice.wav")
        
        # Check if face is captured
        if not hasattr(self, 'reg_face_path') or not os.path.exists(self.reg_face_path):
            self.show_error("You need to capture your face first!")
            return
            
        # Check if voice is recorded
        if not os.path.exists(voice_path):
            self.show_error("You need to record your voice first!")
            return
            
        # Extract & Save Face Embeddings
        self.update_status("Processing face data...")
        face_embedding = util.extract_face_features(face_path)
        if face_embedding is None:
            self.show_error("Face not detected properly! Try again.")
            return
            
        np.save(os.path.join(user_dir, "face_embedding.npy"), face_embedding)
        
        # Extract & Save Voice Embeddings
        self.update_status("Processing voice data...")
        voice_embedding = util.extract_voice_features(voice_path)
        np.save(os.path.join(user_dir, "voice_embedding.npy"), voice_embedding)
        
        # Success animation
        self.show_success_animation()
        self.show_success(f"User {username} registered successfully!")
        self.update_status("Ready")
        
        # Reset status
        self.reg_status_text.set("Registration complete")
    
    def verify_user(self):
        username = self.verify_username_entry.get().strip()
        if not username:
            self.show_error("Username cannot be empty!")
            return
            
        user_dir = f"./db/{username}"
        if not os.path.exists(user_dir):
            self.show_error("User not found! Register first.")
            return
            
        # Check if face is captured
        if not hasattr(self, 'verify_face_path') or not os.path.exists(self.verify_face_path):
            self.show_error("You need to capture your face first!")
            return
            
        # Check if voice is recorded
        if not hasattr(self, 'verify_voice_path') or not os.path.exists(self.verify_voice_path):
            self.show_error("You need to record your voice first!")
            return
            
        stored_face_embedding_path = os.path.join(user_dir, "face_embedding.npy")
        stored_voice_embedding_path = os.path.join(user_dir, "voice_embedding.npy")
        
        # Compare Faces
        self.update_status("Analyzing face...")
        face_score = util.compare_faces(self.verify_face_path, stored_face_embedding_path)
        
        # Compare Voices
        self.update_status("Analyzing voice...")
        voice_score = util.compare_voices(stored_voice_embedding_path, self.verify_voice_path)
        
        # Update progress bars
        self.face_progress["value"] = int(face_score * 100)
        self.voice_progress["value"] = int(voice_score * 100)
        
        # Update score labels
        self.face_score_var.set(f"Face: {face_score:.2f}")
        self.voice_score_var.set(f"Voice: {voice_score:.2f}")
        
        total_score = (face_score + voice_score) / 2
        self.update_status(f"Face Score: {face_score:.2f}, Voice Score: {voice_score:.2f}, Total: {total_score:.2f}")
        
        # Verify result
        if total_score >= 0.7:
            self.show_success(f"✅ Verified as {username}!")
            self.verify_status_text.set("Authentication Successful")
            self.show_success_animation()
        else:
            self.show_error("❌ Verification failed! Try again.")
            self.verify_status_text.set("Authentication Failed")
    
    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.update_status(message, is_error=True)
    
    def show_success(self, message):
        messagebox.showinfo("Success", message)
        self.update_status(message)
    
    def update_status(self, message, is_error=False):
        self.status_label.config(text=message, fg=self.error_color if is_error else self.text_color)
        self.root.update_idletasks()
    
    def show_success_animation(self):
        # Create a success animation overlay
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}")
        overlay.configure(bg="black")  # Solid black (or any other valid color)  # Semi-transparent background
        overlay.wm_attributes("-alpha", 0.5)
        # Success frame
        success_frame = tk.Frame(overlay, bg=self.bg_color, padx=40, pady=40)
        success_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        checkmark = tk.Label(success_frame, text="✓", font=("Helvetica", 60), fg=self.success_color, bg=self.bg_color)
        checkmark.pack()
        
        success_label = tk.Label(success_frame, text="Success!", font=("Helvetica", 24, "bold"), fg=self.text_color, bg=self.bg_color)
        success_label.pack(pady=10)
        
        # Close animation after delay
        def close_overlay():
            overlay.destroy()
            
        overlay.after(1500, close_overlay)


if __name__ == "__main__":
    # Create db directory if it doesn't exist
    os.makedirs("./db", exist_ok=True)
    
    # Create assets directory if it doesn't exist
    os.makedirs("./assets", exist_ok=True)
    
    root = tk.Tk()
    app = BiometricApp(root)
    root.mainloop()