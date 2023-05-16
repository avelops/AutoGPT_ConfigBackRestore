import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import sys

BACKUP_FOLDER = "ai_settings"
SETTINGS_FILE = "ai_settings.yaml"
selected_folder = None
CONFIG_FILE = "config.txt"


def get_selected_folder():
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            folder_path = file.read().strip()
            if folder_path and os.path.isdir(folder_path):
                return folder_path

    return ""


def save_selected_folder(folder_path):
    with open(CONFIG_FILE, "w") as file:
        file.write(folder_path)


def get_backup_folder():
    # Create the backup folder if it doesn't exist
    backup_folder = os.path.join(os.getcwd(), BACKUP_FOLDER)
    os.makedirs(backup_folder, exist_ok=True)
    return backup_folder


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder.set(folder_path)
        save_selected_folder(folder_path)


def create_backup():
    folder_path = selected_folder.get()
    if not folder_path:
        messagebox.showinfo("Error", "Please select the folder first.")
        return

    settings_file = os.path.join(folder_path, SETTINGS_FILE)
    if not os.path.isfile(settings_file):
        messagebox.showinfo("Error", "The settings file does not exist in the selected folder.")
        return

    backup_folder = os.path.join(folder_path, "ai_settings")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Get the current value of "ai_name" from the settings file
    with open(settings_file, "r") as file:
        settings = file.read()
    ai_name = settings.split("ai_name: ")[1].split("\n")[0]

    if not ai_name:
        messagebox.showinfo("Error", "The 'ai_name' field is missing or empty in the settings file.")
        return

    backup_file = f"{ai_name}.yaml"
    backup_path = os.path.join(backup_folder, backup_file)

    try:
        shutil.copy(settings_file, backup_path)
        messagebox.showinfo("Backup Created", f"Backup '{ai_name}' created successfully!")
    except Exception as e:
        messagebox.showinfo("Error", f"Failed to create the backup: {str(e)}")


def restore_backup():
    folder_path = selected_folder.get()
    if not folder_path:
        messagebox.showinfo("Error", "Please select the folder first.")
        return

    backup_folder = os.path.join(folder_path, "ai_settings")
    backups = os.listdir(backup_folder)
    if not os.path.exists(backup_folder):
        messagebox.showinfo("No Backups", "No backups found!")
        return

    # Create a file dialog to select the backup file to restore
    restore_dialog = tk.Toplevel()
    restore_dialog.title("Select Backup File")

    backup_listbox = tk.Listbox(restore_dialog, selectmode=tk.SINGLE)
    backup_listbox.pack(padx=10, pady=10)

    for backup in backups:
        backup_listbox.insert(tk.END, backup)


def show_backups():
    folder_path = selected_folder.get()
    if not folder_path:
        messagebox.showinfo("Error", "Please select the folder first.")
        return

    backup_folder = os.path.join(folder_path, "ai_settings")
    backups = os.listdir(backup_folder)

    if not os.path.exists(backup_folder):
        messagebox.showinfo("No Backups", "No backups found!")
        return

    # Create a listbox to show the available backups
    show_dialog = tk.Toplevel()
    show_dialog.title("Available Backups")

    backup_listbox = tk.Listbox(show_dialog)
    backup_listbox.pack(padx=10, pady=10)

    for backup in backups:
        backup_listbox.insert(tk.END, backup)

    def view_backup():
        selected_backup = backup_listbox.curselection()
        if not selected_backup:
            messagebox.showinfo("Error", "Please select a backup file.")
            return

        backup_file = backup_listbox.get(selected_backup[0])

        # Read the backup file content
        backup_path = os.path.join(backup_folder, backup_file)
        with open(backup_path, "r") as file:
            backup_content = file.read()

        # Display the backup content in a scrollable text box
        view_dialog = tk.Toplevel()
        view_dialog.title("Backup Content")

        text_box = scrolledtext.ScrolledText(view_dialog, width=40, height=10)
        text_box.pack(padx=10, pady=10)
        text_box.insert(tk.END, backup_content)
        text_box.configure(state="disabled")

    def restore_selected():
        selected_backup = backup_listbox.curselection()
        if not selected_backup:
            messagebox.showinfo("Error", "Please select a backup file.")
            return

        backup_file = backup_listbox.get(selected_backup[0])

        # Get the original settings file path
        settings_file = os.path.join(selected_folder.get(), SETTINGS_FILE)

        # Confirm the restore action
        confirm = messagebox.askyesno("Confirm Restore", "Are you sure you want to restore the backup?")
        if confirm:
            # Restore the backup by overwriting the original settings file
            backup_path = os.path.join(backup_folder, backup_file)
            shutil.copy(backup_path, settings_file)
            messagebox.showinfo("Restore Complete", "Backup restored successfully!")

    view_button = tk.Button(show_dialog, text="View Backup", command=view_backup)
    view_button.pack(pady=5)

    restore_button = tk.Button(show_dialog, text="Restore Selected", command=restore_selected)
    restore_button.pack(pady=5)


# Check if tkinter is installed and install it if missing
try:
    import tkinter
except ImportError:
    messagebox.showinfo("Dependency Missing", "tkinter library is not found. Installing...")

    # Install tkinter using pip
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinter"])

# Create the GUI
root = tk.Tk()
root.title("AI Settings Backup")
root.geometry("300x200")

selected_folder = tk.StringVar()
selected_folder.set(get_selected_folder())

folder_label = tk.Label(root, text="Currently Selected folder is:")
folder_label.pack(pady=5)

folder_path_label = tk.Label(root, textvariable=selected_folder)
folder_path_label.pack(pady=5)

select_folder_button = tk.Button(root, text="Select Folder", command=select_folder)
select_folder_button.pack(pady=10)

backup_button = tk.Button(root, text="Backup", command=create_backup)
backup_button.pack(pady=5)

show_backups_button = tk.Button(root, text="Show Backups", command=show_backups)
show_backups_button.pack(pady=5)

root.mainloop()
