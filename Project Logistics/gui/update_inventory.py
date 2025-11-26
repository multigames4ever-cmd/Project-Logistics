"""
Update Inventory Window
Allows updating existing inventory items.
"""
from tkinter import *
from tkinter import messagebox, ttk
import os
import mysql.connector
from mysql.connector import Error



class UpdateInventory:
	def __init__(self, master=None, username=None, item_id=None):
		self.window = master or Tk()
		self.username = username
		self.item_id = item_id
		self.window.geometry("600x400")
		self.window.title("Update Inventory")
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

		header = Label(self.window, text="Update Inventory", bg="#2E4057", fg="white", font=("Segoe UI", 14, "bold"))
		header.grid(row=0, column=0, pady=15)

		action_frame = Frame(self.window, bg="#2E4057")
		action_frame.grid(row=1, column=0, pady=10)
		Button(action_frame, text="Update Item", width=15, bg="#007BFF", fg="white", font=("Segoe UI", 11, "bold"),
		       command=self.update_item).pack()

		form_frame = Frame(self.window, bg="#2E4057")
		form_frame.grid(row=2, column=0, padx=20, pady=10)
		form_frame.grid_columnconfigure(1, weight=1)

		Label(form_frame, text="Item ID:", bg="#2E4057", fg="white").grid(row=0, column=0, sticky="w", pady=5)
		self.id_var = StringVar()
		id_entry = Entry(form_frame, textvariable=self.id_var, width=30)
		id_entry.grid(row=0, column=1, pady=5, padx=10, sticky="w")

		Label(form_frame, text="Name:", bg="#2E4057", fg="white").grid(row=1, column=0, sticky="w", pady=5)
		self.name_var = StringVar()
		name_entry = Entry(form_frame, textvariable=self.name_var, width=30)
		name_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

		Label(form_frame, text="Category:", bg="#2E4057", fg="white").grid(row=2, column=0, sticky="w", pady=5)
		category_frame = Frame(form_frame, bg="#2E4057")
		category_frame.grid(row=2, column=1, pady=5, padx=10, sticky="w")
		
		self.category_var = StringVar()
		self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, width=27, state="readonly")
		self.category_combo.grid(row=0, column=0)
		
		# Buttons for category management
		Button(category_frame, text="+", width=2, bg="#28A745", fg="white", font=("Segoe UI", 8, "bold"),
		       command=self.add_category).grid(row=0, column=1, padx=(3,1))
		Button(category_frame, text="-", width=2, bg="#DC3545", fg="white", font=("Segoe UI", 8, "bold"),
		       command=self.remove_category).grid(row=0, column=2, padx=1)
		
		self.load_categories()

		Label(form_frame, text="Quantity:", bg="#2E4057", fg="white").grid(row=3, column=0, sticky="w", pady=5)
		self.quantity_var = StringVar()
		quantity_entry = Entry(form_frame, textvariable=self.quantity_var, width=30)
		quantity_entry.grid(row=3, column=1, pady=5, padx=10, sticky="w")

		Label(form_frame, text="Delivery Amount:", bg="#2E4057", fg="white").grid(row=4, column=0, sticky="w", pady=5)
		self.delivery_amount_var = StringVar()
		delivery_entry = Entry(form_frame, textvariable=self.delivery_amount_var, width=30)
		delivery_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")

		Button(form_frame, text="Load Item", width=15, bg="#6C757D", fg="white",
		       command=self.load_item).grid(row=5, column=0, columnspan=2, pady=10)

		button_frame = Frame(self.window, bg="#2E4057")
		button_frame.grid(row=3, column=0, pady=15)
		Button(button_frame, text="Add", width=10, bg="#28A745", fg="white",
		       command=self.go_to_add).pack(side=LEFT, padx=5)
		Button(button_frame, text="Remove", width=10, bg="#D9534F", fg="white",
		       command=self.go_to_remove).pack(side=LEFT, padx=5)
		Button(button_frame, text="Back", width=10, bg="#FF8C42", fg="white",
		       command=self.back_to_main).pack(side=LEFT, padx=5)

		if self.item_id:
			self.load_item()

		self.center_window()

	def center_window(self):
		self.window.update_idletasks()
		geom = self.window.geometry().split('+')[0].split('x')
		w = int(geom[0]) if geom[0] else 600
		h = int(geom[1]) if len(geom) > 1 and geom[1] else 400
		x = (self.window.winfo_screenwidth() // 2) - (w // 2)
		y = (self.window.winfo_screenheight() // 2) - (h // 2)
		self.window.geometry(f"{w}x{h}+{x}+{y}")

	def show_book_delivery_form(self):
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			
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
	def load_item(self):
		if not self.item_id:
			return
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			query = "SELECT Name, Category, Quantity, Being_Delivered FROM inventory WHERE ID=%s"
			cursor.execute(query, (int(self.item_id),))
			row = cursor.fetchone()
			cursor.close()
			conn.close()
			if row:
				self.id_var.set(str(self.item_id))
				self.name_var.set(row[0])
				self.category_var.set(row[1])
				self.quantity_var.set(str(row[2]))
				self.delivery_amount_var.set("")
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def update_item(self):
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

			# Ensure table exists with correct structure
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
			
			cursor.execute("SELECT Quantity, Being_Delivered FROM inventory WHERE ID=%s", (int(self.id_var.get()),))
			old = cursor.fetchone()
			old_quantity = old[0] if old else None
			old_being = int(old[1]) if old and old[1] is not None else 0
			delivery_amount = int(self.delivery_amount_var.get()) if self.delivery_amount_var.get() else 0
			being_flag = 1 if delivery_amount > 0 else 0
			if being_flag == 1 and old_being == 0:
				if old_quantity is None:
					messagebox.showerror("Error", "Cannot determine current quantity for this item.")
					cursor.close()
					conn.close()
					return
				if delivery_amount > old_quantity:
					messagebox.showwarning("Validation Error", "Delivery Amount cannot be greater than current quantity.")
					cursor.close()
					conn.close()
					return
				if delivery_amount == old_quantity:
					quantity_to_set = 0
					mark_deleted = 1
				else:
					quantity_to_set = old_quantity - delivery_amount
					mark_deleted = 0
			else:
				quantity_to_set = int(self.quantity_var.get())
				mark_deleted = 0

			if being_flag == 1 and mark_deleted == 1:
				query = "UPDATE inventory SET Name=%s, Category=%s, Quantity=%s, Being_Delivered=%s, Deleted=1 WHERE ID=%s"
				values = (
					self.name_var.get(),
					self.category_var.get(),
					int(quantity_to_set),
					being_flag,
					int(self.id_var.get())
				)
			else:
				query = "UPDATE inventory SET Name=%s, Category=%s, Quantity=%s, Being_Delivered=%s WHERE ID=%s"
				values = (
					self.name_var.get(),
					self.category_var.get(),
					int(quantity_to_set),
					being_flag,
					delivery_amount,
					int(self.id_var.get())
				)

			cursor.execute(query, values)
			conn.commit()

			if cursor.rowcount == 0:
				messagebox.showwarning("Update Failed", "Item ID not found.")
			else:
				was_being = being_flag
				try:
					qty_after = int(quantity_to_set)
				except Exception:
					qty_after = None
				try:
					item_id_local = int(self.id_var.get())
				except Exception:
					item_id_local = None
				if was_being and item_id_local is not None:
					try:
						cursor.execute(
							"CREATE TABLE IF NOT EXISTS deliveries (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, inventory_id INT, Name VARCHAR(255), Category VARCHAR(255), Delivery_Amount INT, Status VARCHAR(32), Delivered_at DATETIME DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
						)
					except Error:
						pass
					try:
						cursor.execute("SELECT id FROM deliveries WHERE inventory_id=%s AND Status='Being Delivered'", (item_id_local,))
						row = cursor.fetchone()
						if row:
							cursor.execute("UPDATE deliveries SET Delivery_Amount=%s, Name=%s, Category=%s WHERE id=%s", (delivery_amount, self.name_var.get(), self.category_var.get(), int(row[0])))
						else:
							cursor.execute("INSERT INTO deliveries (inventory_id, Name, Category, Delivery_Amount, Status) VALUES (%s, %s, %s, %s, %s)", (item_id_local, self.name_var.get(), self.category_var.get(), delivery_amount, 'Being Delivered'))
						conn.commit()
						try:
							if mark_deleted == 1 or qty_after == 0:
								cursor.execute("DELETE FROM inventory WHERE id=%s", (item_id_local,))
								conn.commit()
						except Error:
							pass
					except Error:
						pass
				self.clear_fields()

			cursor.close()
			conn.close()
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def validate_fields(self):
		if not self.id_var.get():
			messagebox.showwarning("Validation Error", "Please enter item ID.")
			return False
		try:
			int(self.id_var.get())
		except ValueError:
			messagebox.showwarning("Validation Error", "Item ID must be a number.")
			return False
		if not self.name_var.get():
			messagebox.showwarning("Validation Error", "Please enter item name.")
			return False
		if not self.category_var.get():
			messagebox.showwarning("Validation Error", "Please enter category.")
			return False
		if self.delivery_amount_var.get():
			try:
				val = int(self.delivery_amount_var.get())
			except ValueError:
				messagebox.showwarning("Validation Error", "Delivery Amount must be a number.")
				return False
			if val <= 0:
				messagebox.showwarning("Validation Error", "Delivery Amount must be greater than zero.")
				return False
		else:
			if not self.quantity_var.get():
				messagebox.showwarning("Validation Error", "Please enter quantity.")
				return False
			try:
				int(self.quantity_var.get())
			except ValueError:
				messagebox.showwarning("Validation Error", "Quantity must be a number.")
				return False
		return True

	def clear_fields(self):
		self.id_var.set("")
		self.name_var.set("")
		self.category_var.set("")
		self.quantity_var.set("")
		self.delivery_amount_var.set("")

	def smooth_transition_to(self, target_class, *args):
		"""Smooth transition to another window"""
		try:
			current_x = self.window.winfo_x()
			current_y = self.window.winfo_y()
		except:
			try:
				current_x = (self.window.winfo_screenwidth() // 2) - 400
				current_y = (self.window.winfo_screenheight() // 2) - 300
			except:
				current_x = 400
				current_y = 300
		
		# Hide current window first
		try:
			self.window.withdraw()
			self.window.update()  # Process the withdraw
		except:
			pass
		
		# Create new window (already starts hidden if target class uses withdraw pattern)
		new_root = Tk()
		new_root.withdraw()  # Ensure it starts hidden
		
		try:
			new_root.geometry(f"+{current_x}+{current_y}")
		except:
			new_root.geometry("+400+300")
		
		# Create app instance
		app = target_class(new_root, *args)
		
		# Destroy old window
		try:
			self.window.destroy()
		except:
			pass
		
		app.run()

	def back_to_main(self):
		self.window.destroy()
