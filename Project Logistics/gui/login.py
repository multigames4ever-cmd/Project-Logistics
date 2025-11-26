"""
Login Window
Handles user authentication and login process.
"""
from tkinter import *
from tkinter import messagebox
import os

VALID_CREDENTIALS = {"admin": "password", "user": "1234"}

class LoginWindow:
    def __init__(self, master=None):
        self.window = master or Tk()
        self.window.title("Login")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        self.window.config(bg="#2E4057")
        self.window.attributes('-topmost', True)
        
        self.window.after(100, lambda: self.window.attributes('-topmost', False))

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
            if os.path.exists(icon_path):
                self.icon = PhotoImage(file=icon_path)
                self.window.iconphoto(True, self.icon)
        except Exception:
            self.icon = None

        self.center_window()

        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=0)
        self.window.grid_columnconfigure(0, weight=1)

        title = Label(self.window, text="Please enter your credentials",
                      bg="#2E4057", fg="white", font=("Segoe UI", 11))
        title.grid(row=0, column=0, pady=15)

        form = Frame(self.window, bg="#2E4057")
        form.grid(row=1, column=0, padx=20)

        Label(form, text="Username:", bg="#2E4057", fg="white").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.username_var = StringVar()
        self.username_entry = Entry(form, textvariable=self.username_var, width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=8)

        Label(form, text="Password:", bg="#2E4057", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.password_var = StringVar()
        self.password_entry = Entry(form, textvariable=self.password_var, show="*", width=25)
        self.password_entry.grid(row=1, column=1, padx=5, pady=8)

        self.show_var = BooleanVar(value=False)
        show_check = Checkbutton(form, text="Show", variable=self.show_var,
                                 command=self.toggle_password, bg="#2E4057", fg="white", selectcolor="#2E4057")
        show_check.grid(row=1, column=2, padx=5)

        btn_frame = Frame(self.window, bg="#2E4057")
        btn_frame.grid(row=2, column=0, pady=15)
        login_btn = Button(btn_frame, text="Login", width=10, command=self.attempt_login)
        login_btn.pack(side=LEFT, padx=5)
        cancel_btn = Button(btn_frame, text="Cancel", width=10, command=self.window.destroy)
        cancel_btn.pack(side=LEFT, padx=5)

        self.window.bind("<Return>", self.attempt_login)
        self.username_entry.focus_set()

    def center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def toggle_password(self):
        self.password_entry.config(show="" if self.show_var.get() else "*")

    def attempt_login(self, event=None):
        user = self.username_var.get().strip()
        pwd = self.password_var.get()
        if not user or not pwd:
            messagebox.showwarning("Login failed", "Please enter both username and password.")
            return
        if VALID_CREDENTIALS.get(user) == pwd:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")
            self.password_var.set("")
            self.password_entry.focus_set()

    def on_login_success(self, username):
        """Called after successful login - open main window"""
        # Destroy login window first
        try:
            self.window.destroy()
        except:
            pass
        
        from main_window import MainWindow
        root = Tk()
        
        main_app = MainWindow(root, username)
        main_app.run()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = LoginWindow()
    app.run()