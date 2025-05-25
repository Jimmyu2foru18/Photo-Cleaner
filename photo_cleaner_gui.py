#!/usr/bin/env python3
"""
Photo Cleaner GUI - NSFW Content Detection Tool

A graphical user interface for the Photo Cleaner application
that provides an intuitive way to scan and organize photos.

Author: Photo Cleaner Tool
Version: 1.0.0
"""

import os
import sys
import json
import threading
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    from PIL import Image, ImageTk
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap import Style
    from tktooltip import ToolTip
except ImportError as e:
    print(f"Error importing required GUI libraries: {e}")
    print("Installing required GUI packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "customtkinter", "ttkbootstrap", "tkinter-tooltip"], check=True)
        print("GUI packages installed successfully. Please restart the application.")
    except subprocess.CalledProcessError:
        print("Failed to install GUI packages. Please install them manually:")
        print("pip install customtkinter ttkbootstrap tkinter-tooltip")
    sys.exit(1)

# Try to import TensorFlow and related packages
TENSORFLOW_AVAILABLE = False
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    import numpy as np
    TENSORFLOW_AVAILABLE = True
    print("TensorFlow is available. Full functionality enabled.")
except ImportError:
    print("Warning: TensorFlow is not available. Limited functionality mode.")
    print("To enable full functionality, install TensorFlow:")
    print("pip install tensorflow tensorflow-hub")

# Import the photo cleaner modules
try:
    from simple_photo_cleaner import SimplePhotoCleaner
    SIMPLE_CLEANER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import SimplePhotoCleaner module.")
    print("The GUI will still work but will use subprocess to run the scripts.")
    SIMPLE_CLEANER_AVAILABLE = False

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PhotoCleanerApp(ctk.CTk):
    """Main application window for Photo Cleaner GUI."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Photo Cleaner - NSFW Content Detection Tool")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize variables
        self.input_dir = ctk.StringVar(value="")
        self.output_dir = ctk.StringVar(value="")
        self.threshold = ctk.DoubleVar(value=self.config["settings"]["default_threshold"])
        self.use_advanced = ctk.BooleanVar(value=False)
        self.dry_run = ctk.BooleanVar(value=self.config["safety"]["dry_run_by_default"])
        self.verbose = ctk.BooleanVar(value=self.config["settings"]["logging"]["verbose_by_default"])
        
        # Create UI elements
        self.create_ui()
        
        # Initialize scanning state
        self.scanning = False
        self.scan_thread = None
        
    def load_config(self):
        """Load configuration from config.json."""
        config_path = Path(__file__).parent / "config.json"
        
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default configuration
            return {
                "settings": {
                    "default_threshold": 0.7,
                    "logging": {"verbose_by_default": False}
                },
                "safety": {"dry_run_by_default": False}
            }
    
    def create_ui(self):
        """Create the user interface."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header with logo and title
        self.create_header()
        
        # Create input section
        self.create_input_section()
        
        # Create options section
        self.create_options_section()
        
        # Create action buttons
        self.create_action_buttons()
        
        # Create status section
        self.create_status_section()
        
        # Create footer
        self.create_footer()
    
    def create_header(self):
        """Create header with logo and title."""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # App title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Photo Cleaner", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 0))
        
        # App subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="NSFW Content Detection Tool", 
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Separator
        separator = ctk.CTkFrame(self.main_frame, height=2)
        separator.pack(fill="x", pady=(0, 20))
    
    def create_input_section(self):
        """Create input directory selection section."""
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", pady=(0, 20))
        
        # Input directory
        input_label = ctk.CTkLabel(
            input_frame, 
            text="Input Directory:", 
            font=ctk.CTkFont(weight="bold")
        )
        input_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        input_entry = ctk.CTkEntry(
            input_frame, 
            textvariable=self.input_dir,
            width=500
        )
        input_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        input_button = ctk.CTkButton(
            input_frame, 
            text="Browse", 
            command=self.browse_input_dir
        )
        input_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Output directory
        output_label = ctk.CTkLabel(
            input_frame, 
            text="Output Directory:\n(optional)", 
            font=ctk.CTkFont(weight="bold")
        )
        output_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        output_entry = ctk.CTkEntry(
            input_frame, 
            textvariable=self.output_dir,
            width=500
        )
        output_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        output_button = ctk.CTkButton(
            input_frame, 
            text="Browse", 
            command=self.browse_output_dir
        )
        output_button.grid(row=1, column=2, padx=10, pady=10)
        
        # Configure grid
        input_frame.grid_columnconfigure(1, weight=1)
    
    def create_options_section(self):
        """Create options section."""
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(fill="x", pady=(0, 20))
        
        # Options label
        options_label = ctk.CTkLabel(
            options_frame, 
            text="Scan Options", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        options_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Threshold slider
        threshold_frame = ctk.CTkFrame(options_frame)
        threshold_frame.pack(fill="x", padx=10, pady=5)
        
        threshold_label = ctk.CTkLabel(
            threshold_frame, 
            text="Sensitivity Threshold:", 
            font=ctk.CTkFont(weight="bold")
        )
        threshold_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        threshold_slider = ctk.CTkSlider(
            threshold_frame, 
            from_=0.0, 
            to=1.0, 
            number_of_steps=100,
            variable=self.threshold
        )
        threshold_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        threshold_value = ctk.CTkLabel(
            threshold_frame, 
            text=f"{self.threshold.get():.2f}"
        )
        threshold_value.grid(row=0, column=2, padx=10, pady=10)
        
        # Update threshold value label when slider changes
        def update_threshold_label(value):
            threshold_value.configure(text=f"{float(value):.2f}")
        
        threshold_slider.configure(command=update_threshold_label)
        
        # Configure grid
        threshold_frame.grid_columnconfigure(1, weight=1)
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(options_frame)
        checkbox_frame.pack(fill="x", padx=10, pady=5)
        
        # Advanced mode checkbox
        advanced_checkbox = ctk.CTkCheckBox(
            checkbox_frame, 
            text="Use Advanced Mode (OpenNSFW2)", 
            variable=self.use_advanced,
            onvalue=True, 
            offvalue=False
        )
        advanced_checkbox.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Dry run checkbox
        dry_run_checkbox = ctk.CTkCheckBox(
            checkbox_frame, 
            text="Dry Run (Preview Only)", 
            variable=self.dry_run,
            onvalue=True, 
            offvalue=False
        )
        dry_run_checkbox.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Verbose checkbox
        verbose_checkbox = ctk.CTkCheckBox(
            checkbox_frame, 
            text="Verbose Logging", 
            variable=self.verbose,
            onvalue=True, 
            offvalue=False
        )
        verbose_checkbox.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Configure grid
        checkbox_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Add tooltips
        ToolTip(advanced_checkbox, msg="Use the more accurate OpenNSFW2 neural network model (requires more resources)")
        ToolTip(dry_run_checkbox, msg="Preview what would happen without actually moving any files")
        ToolTip(verbose_checkbox, msg="Enable detailed logging for debugging")
        ToolTip(threshold_slider, msg="Higher values are more strict (0.7 recommended)")
    
    def create_action_buttons(self):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", pady=(0, 20))
        
        # Scan button
        self.scan_button = ctk.CTkButton(
            button_frame, 
            text="Start Scan", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.start_scan
        )
        self.scan_button.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        # Stop button
        self.stop_button = ctk.CTkButton(
            button_frame, 
            text="Stop Scan", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.stop_scan,
            state="disabled"
        )
        self.stop_button.pack(side="right", padx=10, pady=10, fill="x", expand=True)
    
    def create_status_section(self):
        """Create status section with progress bar and log."""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Status label
        status_label = ctk.CTkLabel(
            status_frame, 
            text="Status", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Progress frame
        progress_frame = ctk.CTkFrame(status_frame)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        # Status message
        self.status_message = ctk.CTkLabel(
            progress_frame, 
            text="Ready",
            anchor="w"
        )
        self.status_message.pack(fill="x", padx=10, pady=(10, 5))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Log frame
        log_frame = ctk.CTkFrame(status_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Log label
        log_label = ctk.CTkLabel(
            log_frame, 
            text="Log", 
            font=ctk.CTkFont(weight="bold")
        )
        log_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Log text box
        self.log_text = ctk.CTkTextbox(log_frame, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_text.configure(state="disabled")
    
    def create_footer(self):
        """Create footer with links and info."""
        footer_frame = ctk.CTkFrame(self.main_frame)
        footer_frame.pack(fill="x")
        
        # Help button
        help_button = ctk.CTkButton(
            footer_frame, 
            text="Help", 
            command=self.show_help,
            width=80
        )
        help_button.pack(side="left", padx=10, pady=10)
        
        # About button
        about_button = ctk.CTkButton(
            footer_frame, 
            text="About", 
            command=self.show_about,
            width=80
        )
        about_button.pack(side="left", padx=10, pady=10)
        
        # Open report button
        self.report_button = ctk.CTkButton(
            footer_frame, 
            text="Open Report", 
            command=self.open_report,
            width=100,
            state="disabled"
        )
        self.report_button.pack(side="right", padx=10, pady=10)
        
        # Open folder button
        self.folder_button = ctk.CTkButton(
            footer_frame, 
            text="Open Output Folder", 
            command=self.open_output_folder,
            width=150,
            state="disabled"
        )
        self.folder_button.pack(side="right", padx=10, pady=10)
    
    def browse_input_dir(self):
        """Open file dialog to select input directory."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.set(directory)
    
    def browse_output_dir(self):
        """Open file dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def log(self, message):
        """Add message to log text box."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def update_status(self, message, progress=None):
        """Update status message and progress bar."""
        self.status_message.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
    
    def start_scan(self):
        """Start the scanning process."""
        # Validate input
        input_dir = self.input_dir.get()
        if not input_dir:
            messagebox.showerror("Error", "Please select an input directory.")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("Error", "Input directory does not exist.")
            return
        
        # Check if TensorFlow is available when using advanced mode
        use_advanced = self.use_advanced.get()
        if use_advanced and not globals().get('TENSORFLOW_AVAILABLE', False):
            result = messagebox.askquestion("TensorFlow Not Available", 
                "TensorFlow is not installed, which is required for advanced mode.\n\n"
                "Would you like to continue with simple mode instead?", 
                icon='warning')
            if result == 'yes':
                self.use_advanced.set(False)
                use_advanced = False
            else:
                messagebox.showinfo("Scan Cancelled", 
                    "Scan has been cancelled. Please install TensorFlow to use advanced mode:\n"
                    "pip install tensorflow tensorflow-hub")
                return
        
        # Get output directory
        output_dir = self.output_dir.get() or input_dir
        
        # Get options
        threshold = self.threshold.get()
        dry_run = self.dry_run.get()
        verbose = self.verbose.get()
        
        # Update UI
        self.scanning = True
        self.scan_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.update_status("Initializing scan...", 0.05)
        
        # Clear log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        
        # Log scan parameters
        self.log(f"Starting scan with the following parameters:")
        self.log(f"Input directory: {input_dir}")
        self.log(f"Output directory: {output_dir}")
        self.log(f"Threshold: {threshold:.2f}")
        self.log(f"Mode: {'Advanced' if use_advanced else 'Simple'}")
        self.log(f"Dry run: {'Yes' if dry_run else 'No'}")
        self.log(f"Verbose: {'Yes' if verbose else 'No'}")
        self.log("---")
        
        # Check if we should use direct module import or subprocess
        if not use_advanced and globals().get('SIMPLE_CLEANER_AVAILABLE', False) and globals().get('TENSORFLOW_AVAILABLE', False):
            self.log("Using direct module import for better performance")
            # Start scanning in a separate thread using direct module import
            self.scan_thread = threading.Thread(
                target=self._run_direct_scan, 
                args=(input_dir, output_dir, threshold, dry_run, verbose)
            )
            self.scan_thread.daemon = True
            self.scan_thread.start()
            return
        
        # Start scan in a separate thread using subprocess
        self.scan_thread = threading.Thread(
            target=self.run_scan,
            args=(input_dir, output_dir, threshold, use_advanced, dry_run, verbose)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def run_scan(self, input_dir, output_dir, threshold, use_advanced, dry_run, verbose):
        """Run the scan process in a separate thread."""
        try:
            # Update status
            self.update_status("Scanning photos...", 0.1)
            
            # Determine which script to use
            script = "photo_cleaner.py" if use_advanced else "simple_photo_cleaner.py"
            
            # Build command
            cmd = [
                sys.executable,
                os.path.join(os.path.dirname(os.path.abspath(__file__)), script),
                "-i", input_dir,
                "-t", str(threshold)
            ]
            
            if output_dir != input_dir:
                cmd.extend(["-o", output_dir])
            
            if dry_run:
                cmd.append("--dry-run")
            
            if verbose:
                cmd.append("-v")
            
            # Log command
            self.log(f"Running command: {' '.join(cmd)}")
            
            # Run process and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Process output
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                    
                # Update log
                self.log(line.strip())
                
                # Update progress based on output
                if "Scanning photos" in line:
                    self.update_status("Scanning photos...", 0.3)
                elif "SCAN COMPLETE" in line:
                    self.update_status("Scan complete!", 1.0)
                
            # Wait for process to complete
            process.wait()
            
            # Check return code
            if process.returncode == 0:
                self.log("Scan completed successfully.")
                
                # Enable report and folder buttons
                report_path = os.path.join(output_dir, "scan_report.txt")
                if os.path.exists(report_path):
                    self.report_button.configure(state="normal")
                
                self.folder_button.configure(state="normal")
                
                # Final status update
                self.update_status("Scan completed successfully!", 1.0)
                
                # Show completion message
                if not dry_run:
                    messagebox.showinfo(
                        "Scan Complete", 
                        "Photo scan completed successfully!\n\n"
                        f"Check the output folder for organized photos.\n"
                        f"A detailed report is available in {report_path}."
                    )
                else:
                    messagebox.showinfo(
                        "Dry Run Complete", 
                        "Photo scan dry run completed successfully!\n\n"
                        "No files were moved. Check the log for details."
                    )
            else:
                self.log(f"Scan failed with return code {process.returncode}.")
                self.update_status("Scan failed!", 0.0)
                messagebox.showerror("Error", "Scan failed. Check the log for details.")
                
        except Exception as e:
            self.log(f"Error during scan: {e}")
            self.update_status("Error during scan!", 0.0)
            messagebox.showerror("Error", f"An error occurred during the scan:\n{e}")
            
        finally:
            # Reset UI
            self.scanning = False
            self.scan_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def stop_scan(self):
        """Stop the scanning process."""
        if not self.scanning:
            return
            
        # Confirm stop
        if messagebox.askyesno("Confirm", "Are you sure you want to stop the scan?"):
            self.log("Stopping scan...")
            self.update_status("Stopping scan...", 0.0)
            
            # Set scanning flag to False
            self.scanning = False
            
            # Reset UI
            self.scan_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def open_report(self):
        """Open the scan report."""
        output_dir = self.output_dir.get() or self.input_dir.get()
        report_path = os.path.join(output_dir, "scan_report.txt")
        
        if os.path.exists(report_path):
            # Open report with default text editor
            if sys.platform == "win32":
                os.startfile(report_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", report_path])
            else:
                subprocess.run(["xdg-open", report_path])
        else:
            messagebox.showerror("Error", "Report file not found.")
    
    def open_output_folder(self):
        """Open the output folder."""
        output_dir = self.output_dir.get() or self.input_dir.get()
        
        if os.path.exists(output_dir):
            # Open folder in file explorer
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
        else:
            messagebox.showerror("Error", "Output directory not found.")
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
        Photo Cleaner Help
        
        This tool scans photos for NSFW content and organizes them into separate folders based on sensitivity thresholds.
        
        Usage:
        1. Select an input directory containing photos to scan
        2. Optionally select an output directory (defaults to input directory)
        3. Adjust the sensitivity threshold (higher values are more strict)
        4. Choose between Simple and Advanced mode
        5. Enable Dry Run to preview without moving files
        6. Click Start Scan to begin
        
        Output Structure:
        - clean_photos/     : Photos below threshold
        - sensitive_photos/ : Photos above threshold
        - photo_cleaner.log : Operation log
        - scan_report.txt   : Summary report
        
        For more information, see the README.md file.
        """
        
        help_window = ctk.CTkToplevel(self)
        help_window.title("Photo Cleaner Help")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        help_window.grab_set()  # Make window modal
        
        # Help text
        help_textbox = ctk.CTkTextbox(help_window, wrap="word")
        help_textbox.pack(fill="both", expand=True, padx=20, pady=20)
        help_textbox.insert("1.0", help_text)
        help_textbox.configure(state="disabled")
        
        # Close button
        close_button = ctk.CTkButton(
            help_window, 
            text="Close", 
            command=help_window.destroy
        )
        close_button.pack(pady=(0, 20))
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        Photo Cleaner - NSFW Content Detection Tool
        Version 1.0.0
        
        A tool for automatically scanning photos for NSFW content
        and organizing them into appropriate folders based on
        sensitivity thresholds.
        
        Features:
        - Automated NSFW Detection
        - Configurable Sensitivity
        - Automatic Organization
        - Batch Processing
        - Safe Operation
        
        This software is licensed under the MIT License.
        See LICENSE file for details.
        """
        
        about_window = ctk.CTkToplevel(self)
        about_window.title("About Photo Cleaner")
        about_window.geometry("500x400")
        about_window.resizable(True, True)
        about_window.grab_set()  # Make window modal
        
        # About text
        about_textbox = ctk.CTkTextbox(about_window, wrap="word")
        about_textbox.pack(fill="both", expand=True, padx=20, pady=20)
        about_textbox.insert("1.0", about_text)
        about_textbox.configure(state="disabled")
        
        # Close button
        close_button = ctk.CTkButton(
            about_window, 
            text="Close", 
            command=about_window.destroy
        )
        close_button.pack(pady=(0, 20))


def main():
    """Main function."""
    app = PhotoCleanerApp()
    app.mainloop()


if __name__ == "__main__":
    main()