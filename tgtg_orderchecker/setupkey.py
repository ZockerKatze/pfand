
import tkinter as tk
from tkinter import messagebox
import os

# Get the current working directory
current_directory = os.getcwd()

# Check if the current directory is already 'tgtg_orderchecker', if so adjust the path
if current_directory.endswith('tgtg_orderchecker'):
    KEY_FILE_PATH = os.path.join(current_directory, 'key.py')
else:
    KEY_FILE_PATH = os.path.join(current_directory, 'tgtg_orderchecker', 'key.py')

# Function to modify the key.py file
def modify_key_file(access_token, refresh_token, cookie):
    try:
        # Check if the key.py file exists
        if os.path.exists(KEY_FILE_PATH):
            # Ask the user if they want to replace the existing file
            result = messagebox.askyesno("File Exists", f"{KEY_FILE_PATH} already exists. Do you want to replace it?")
            if not result:
                return  # If user chooses "No", do nothing and return

        # Open and modify the file with new values
        with open(KEY_FILE_PATH, 'w') as file:
            file.write(f'''from tgtg import TgtgClient

client = TgtgClient(access_token="{access_token}",
                    refresh_token="{refresh_token}",
                    cookie="{cookie}")
''')
        messagebox.showinfo("Success", f"{KEY_FILE_PATH} has been updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to modify {KEY_FILE_PATH}: {str(e)}")

# Function to handle the Tkinter window for user input
def ask_for_tokens():
    def submit_tokens():
        access_token = access_token_entry.get()
        refresh_token = refresh_token_entry.get()
        cookie = cookie_entry.get()

        if not access_token or not refresh_token or not cookie:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Modify the key file
        modify_key_file(access_token, refresh_token, cookie)

    # Create Tkinter window
    root = tk.Tk()
    root.title("Enter API Credentials")

    # Add labels and entry fields for the tokens and cookie
    tk.Label(root, text="Access Token:").grid(row=0, column=0)
    access_token_entry = tk.Entry(root, width=40)
    access_token_entry.grid(row=0, column=1)

    tk.Label(root, text="Refresh Token:").grid(row=1, column=0)
    refresh_token_entry = tk.Entry(root, width=40)
    refresh_token_entry.grid(row=1, column=1)

    tk.Label(root, text="Cookie:").grid(row=2, column=0)
    cookie_entry = tk.Entry(root, width=40)
    cookie_entry.grid(row=2, column=1)

    # Submit button to process the tokens
    submit_button = tk.Button(root, text="Submit", command=submit_tokens)
    submit_button.grid(row=3, columnspan=2)

    # Keep the window on top
    root.attributes("-topmost", True)

    # Start Tkinter main loop
    root.mainloop()

# Run the application
if __name__ == "__main__":
    ask_for_tokens()

