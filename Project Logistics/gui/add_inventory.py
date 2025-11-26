"""
Add Inventory Window
Allows adding new inventory items to the system.
"""
from tkinter import *
from tkinter import messagebox, ttk
import os
import mysql.connector
from mysql.connector import Error


class AddInventory:
	def __init__(self, master, username=None):
		self.window = master or Tk()
		self.username = username
		self.window.geometry("600x400")
		self.window.title("Add Inventory")
		try:
			icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
			if os.path.exists(icon_path):
				self.icon = PhotoImage(file=icon_path)
				self.window.iconphoto(True, self.icon)
		except Exception:
			self.icon = None
		self.window.config(bg="#2E4057")

		self.window.grid_rowconfigure(0, weight=0)
		self.window.grid_rowconfigure(1, weight=1)
		self.window.grid_rowconfigure(2, weight=0)
		self.window.grid_rowconfigure(3, weight=0)
		self.window.grid_columnconfigure(0, weight=1)

		header = Label(self.window, text="Add Inventory", bg="#2E4057", fg="white", font=("Segoe UI", 14, "bold"))
		header.grid(row=0, column=0, pady=15)

		action_frame = Frame(self.window, bg="#2E4057")
		action_frame.grid(row=1, column=0, pady=10)
		Button(action_frame, text="Add Item", width=15, bg="#28A745", fg="white", font=("Segoe UI", 11, "bold"),
		       command=self.add_item).pack()

		form_frame = Frame(self.window, bg="#2E4057")
		form_frame.grid(row=2, column=0, padx=20, pady=10)
		form_frame.grid_columnconfigure(1, weight=1)

		Label(form_frame, text="Name:", bg="#2E4057", fg="white").grid(row=1, column=0, sticky="w", pady=5)
		self.name_var = StringVar()
		name_entry = Entry(form_frame, textvariable=self.name_var, width=30)
		name_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

		Label(form_frame, text="Category:", bg="#2E4057", fg="white").grid(row=2, column=0, sticky="w", pady=5)
		category_frame = Frame(form_frame, bg="#2E4057")
		category_frame.grid(row=2, column=1, pady=5, padx=10, sticky="ew")
		
		self.category_var = StringVar()
		self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, width=22, state="readonly")
		self.category_combo.pack(side=LEFT)
		
		# Buttons for category management
		Button(category_frame, text="+", width=2, bg="#28A745", fg="white", font=("Segoe UI", 8, "bold"),
		       command=self.add_category).pack(side=LEFT, padx=(3,1))
		Button(category_frame, text="-", width=2, bg="#DC3545", fg="white", font=("Segoe UI", 8, "bold"),
		       command=self.remove_category).pack(side=LEFT, padx=1)
		
		self.load_categories()

		Label(form_frame, text="Quantity:", bg="#2E4057", fg="white").grid(row=3, column=0, sticky="w", pady=5)
		self.quantity_var = StringVar()
		quantity_entry = Entry(form_frame, textvariable=self.quantity_var, width=30)
		quantity_entry.grid(row=3, column=1, pady=5, padx=10, sticky="w")

		Label(form_frame, text="Brand:", bg="#2E4057", fg="white").grid(row=4, column=0, sticky="w", pady=5)
		self.brand_var = StringVar()
		brand_entry = Entry(form_frame, textvariable=self.brand_var, width=30)
		brand_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")

		button_frame = Frame(self.window, bg="#2E4057")
		button_frame.grid(row=3, column=0, pady=15)
		Button(button_frame, text="Update", width=10, bg="#007BFF", fg="white",
		       command=self.go_to_update).pack(side=LEFT, padx=5)
		Button(button_frame, text="Remove", width=10, bg="#D9534F", fg="white",
		       command=self.go_to_remove).pack(side=LEFT, padx=5)
		Button(button_frame, text="Back", width=10, bg="#FF8C42", fg="white",
		       command=self.back_to_main).pack(side=LEFT, padx=5)

	def init_categories_table(self):
		"""Initialize the categories table with default categories"""
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			
			# Create categories table
			cursor.execute(
				"""
				CREATE TABLE IF NOT EXISTS categories (
				  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
				  name VARCHAR(100) NOT NULL UNIQUE,
				  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
				"""
			)
			
			# Check if categories table is empty and seed with default categories
			cursor.execute("SELECT COUNT(*) FROM categories")
			count = cursor.fetchone()[0]
			
			if count == 0:
				default_categories = [
					"Electronics", "Clothing", "Food & Beverages", "Books", 
					"Toys & Games", "Home & Garden", "Sports & Outdoors", 
					"Health & Beauty", "Automotive", "Office Supplies"
				]
				
				for category in default_categories:
					try:
						cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
					except Error:
						pass  # Skip if category already exists
				
			conn.commit()
			cursor.close()
			conn.close()
			
		except Error as e:
			messagebox.showerror("Database Error", f"Error initializing categories: {e}")

	def load_categories(self):
		"""Load categories from database into combobox"""
		self.init_categories_table()
		
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			cursor.execute("SELECT name FROM categories ORDER BY name")
			categories = [row[0] for row in cursor.fetchall()]
			
			self.category_combo['values'] = categories
			if categories:
				self.category_combo.current(0)  # Select first category by default
			
			cursor.close()
			conn.close()
			
		except Error as e:
			messagebox.showerror("Database Error", f"Error loading categories: {e}")

	def add_category(self):
		"""Add a new category through dialog"""
		dialog = Toplevel(self.window)
		dialog.title("Add New Category")
		dialog.geometry("300x150")
		dialog.config(bg="#2E4057")
		dialog.grab_set()  # Make dialog modal
		
		# Center dialog
		dialog.transient(self.window)
		x = self.window.winfo_rootx() + 150
		y = self.window.winfo_rooty() + 100
		dialog.geometry(f"+{x}+{y}")
		
		Label(dialog, text="Enter new category name:", bg="#2E4057", fg="white", 
		      font=("Segoe UI", 10)).pack(pady=15)
		
		new_category_var = StringVar()
		entry = Entry(dialog, textvariable=new_category_var, width=25, font=("Segoe UI", 10))
		entry.pack(pady=10)
		entry.focus()
		
		btn_frame = Frame(dialog, bg="#2E4057")
		btn_frame.pack(pady=15)
		
		def save_category():
			category_name = new_category_var.get().strip()
			if not category_name:
				messagebox.showwarning("Input Error", "Please enter a category name.")
				return
			
			try:
				conn = mysql.connector.connect(
					host="127.0.0.1",
					user="root",
					password="",
					database="inventories"
				)
				cursor = conn.cursor()
				cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
				conn.commit()
				cursor.close()
				conn.close()
				
				messagebox.showinfo("Success", f"Category '{category_name}' added successfully!")
				self.load_categories()
				self.category_var.set(category_name)  # Select the newly added category
				dialog.destroy()
				
			except Error as e:
				if "Duplicate entry" in str(e):
					messagebox.showerror("Error", "This category already exists!")
				else:
					messagebox.showerror("Database Error", f"Error adding category: {e}")
		
		Button(btn_frame, text="Add", bg="#28A745", fg="white", width=8,
		       command=save_category).pack(side=LEFT, padx=5)
		Button(btn_frame, text="Cancel", bg="#6C757D", fg="white", width=8,
		       command=dialog.destroy).pack(side=LEFT, padx=5)
		
		# Bind Enter key to save
		dialog.bind('<Return>', lambda e: save_category())

	def remove_category(self):
		"""Remove selected category after confirmation"""
		selected_category = self.category_var.get()
		if not selected_category:
			messagebox.showwarning("Selection Error", "Please select a category to remove.")
			return
		
		# Check if category is in use
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			cursor.execute("SELECT COUNT(*) FROM inventory WHERE Category = %s", (selected_category,))
			count = cursor.fetchone()[0]
			
			if count > 0:
				messagebox.showwarning("Cannot Delete", 
				                      f"Category '{selected_category}' is being used by {count} item(s). "
				                      "Please update or remove those items first.")
				cursor.close()
				conn.close()
				return
			
			# Confirm deletion
			if messagebox.askyesno("Confirm Delete", 
			                      f"Are you sure you want to delete the category '{selected_category}'?"):
				cursor.execute("DELETE FROM categories WHERE name = %s", (selected_category,))
				conn.commit()
				self.load_categories()
			
			cursor.close()
			conn.close()
			
		except Error as e:
			messagebox.showerror("Database Error", f"Error removing category: {e}")

	
	def center_window(self):
		self.window.update_idletasks()
		geom = self.window.geometry().split('+')[0].split('x')
		w = int(geom[0]) if geom[0] else 600
		h = int(geom[1]) if len(geom) > 1 and geom[1] else 400
		x = (self.window.winfo_screenwidth() // 2) - (w // 2)
		y = (self.window.winfo_screenheight() // 2) - (h // 2)
		self.window.geometry(f"{w}x{h}+{x}+{y}")

	def add_item(self):
		if not self.validate_fields():
			return

		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			
			try:
				cursor.execute("ALTER TABLE inventory MODIFY id INT NOT NULL AUTO_INCREMENT")
			except Error:
				pass
			try:
				cursor.execute("ALTER TABLE inventory AUTO_INCREMENT = 1")
			except Error:
				pass

			cursor.execute("""
				CREATE TABLE IF NOT EXISTS inventory (
					ID INT AUTO_INCREMENT PRIMARY KEY,
					Name VARCHAR(255) NOT NULL,
					Category VARCHAR(100),
					Quantity INT DEFAULT 0,
					Brand VARCHAR(100),
					Deleted TINYINT DEFAULT 0,
					Being_Delivered TINYINT DEFAULT 0
				)
			""")

			query = "INSERT INTO inventory (Name, Category, Quantity, Brand) VALUES (%s, %s, %s, %s)"
			values = (
				self.name_var.get(),
				self.category_var.get(),
				int(self.quantity_var.get()),
				self.brand_var.get()
			)

			cursor.execute(query, values)
			conn.commit()

			messagebox.showinfo("Success", "Item added successfully!")
			self.clear_fields()
			cursor.close()
			conn.close()
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def validate_fields(self):
			# ID is auto-generated by the database (AUTO_INCREMENT)
		if not self.name_var.get():
			messagebox.showwarning("Validation Error", "Please enter item name.")
			return False
		if not self.category_var.get():
			messagebox.showwarning("Validation Error", "Please enter category.")
			return False
		if not self.quantity_var.get():
			messagebox.showwarning("Validation Error", "Please enter quantity.")
			return False
		try:
			int(self.quantity_var.get())
		except ValueError:
			messagebox.showwarning("Validation Error", "Quantity must be a number.")
			return False
		if not self.brand_var.get():
			messagebox.showwarning("Validation Error", "Please enter brand.")
			return False
		return True

	def clear_fields(self):
		self.name_var.set("")
		self.category_var.set("")
		self.quantity_var.set("")
		self.brand_var.set("")

	def back_to_main(self):
		self.window.destroy()