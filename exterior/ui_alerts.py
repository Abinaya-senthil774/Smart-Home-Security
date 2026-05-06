"""
DESCRIPTION: 
This module handles the user interface alert system for the home security project.
It isolates the Tkinter blocking logic from the main computer vision loop.

INPUT: 
No direct arguments. It is triggered when an unknown person or suspicious motion is detected.

OUTPUT: 
Returns a string response ('yes' or 'no') based on the user's click in the message box dialog.
"""

import tkinter as tk
from tkinter import messagebox

def ask_user():
    root = tk.Tk()
    root.withdraw()  # Hide the root window so only the dialog box appears
    response = messagebox.askquestion("New Person Detected", "Is this person someone you know?")
    root.destroy()   # Destroy the root to clean up Tkinter resources
    return response
