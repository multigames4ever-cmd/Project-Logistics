"""
Remove Inventory Window
Allows removing inventory items from the system.
"""
from tkinter import *
from tkinter import messagebox
import os
import mysql.connector
from mysql.connector import Error



class RemoveInventory:
	def __init__(self, master, username=None, item_id=None):
		self.window = master or Tk()
		self.username = username
		self.item_id = item_id
		self.window.geometry("600x400")
		self.window.title("Remove Inventory")
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

		header = Label(self.window, text="Remove Inventory", bg="#2E4057", fg="white", font=("Segoe UI", 14, "bold"))
		header.grid(row=0, column=0, pady=15)



		form_frame = Frame(self.window, bg="#2E4057")
		form_frame.grid(row=2, column=0, padx=20, pady=10)

		Label(form_frame, text="Item ID:", bg="#2E4057", fg="white").grid(row=0, column=0, sticky="w", pady=5)
		self.id_var = StringVar()
		Entry(form_frame, textvariable=self.id_var, width=30).grid(row=0, column=1, pady=5, padx=10)

		Label(form_frame, text="Name:", bg="#2E4057", fg="white").grid(row=1, column=0, sticky="w", pady=5)
		self.name_var = StringVar()
		name_entry = Entry(form_frame, textvariable=self.name_var, width=30, state="readonly")
		name_entry.grid(row=1, column=1, pady=5, padx=10)
		self.name_entry = name_entry

		Label(form_frame, text="Brand:", bg="#2E4057", fg="white").grid(row=2, column=0, sticky="w", pady=5)
		self.brand_var = StringVar()
		brand_entry = Entry(form_frame, textvariable=self.brand_var, width=30, state="readonly")
		brand_entry.grid(row=2, column=1, pady=5, padx=10)
		self.brand_entry = brand_entry

		Button(form_frame, text="Load Item", width=15, bg="#6C757D", fg="white",
		       command=self.load_item).grid(row=3, column=0, columnspan=2, pady=10)

		button_frame = Frame(self.window, bg="#2E4057")
		button_frame.grid(row=3, column=0, pady=15)
		Button(button_frame, text="Move to Recycle Bin", width=16, bg="#D9534F", fg="white",
			command=self.remove_item).pack(side=LEFT, padx=5)
		Button(button_frame, text="Restore", width=10, bg="#28A745", fg="white",
			command=self.restore_item).pack(side=LEFT, padx=5)
		Button(button_frame, text="Delete Permanently", width=16, bg="#8B0000", fg="white",
			command=self.permanently_delete).pack(side=LEFT, padx=5)
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

	def remove_item(self):
		if not self.id_var.get():
			messagebox.showwarning("Validation Error", "Please enter item ID.")
			return

		if not messagebox.askyesno("Confirm", "Move this item to Recycle Bin?"):
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
				cursor.execute("ALTER TABLE inventory ADD COLUMN Deleted TINYINT(1) NOT NULL DEFAULT 0")
			except Error:
				pass

			query = "UPDATE inventory SET Deleted=1 WHERE ID=%s"
			values = (int(self.id_var.get()),)

			cursor.execute(query, values)
			conn.commit()

			if cursor.rowcount == 0:
				messagebox.showwarning("Operation Failed", "Item ID not found.")
			else:
				self.clear_fields()
			
			cursor.close()
			conn.close()
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def load_item(self):
		if not self.id_var.get() and not self.item_id:
			messagebox.showwarning("Validation Error", "Please enter item ID.")
			return
		item_lookup = int(self.id_var.get()) if self.id_var.get() else int(self.item_id)

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
			
			query = "SELECT Name, Brand FROM inventory WHERE ID=%s"
			values = (item_lookup,)

			cursor.execute(query, values)
			result = cursor.fetchone()

			if result:
				self.id_var.set(str(item_lookup))
				self.name_var.set(result[0])
				self.brand_var.set(result[1])
			else:
				messagebox.showwarning("Not Found", "Item ID not found.")
				self.clear_fields()

			cursor.close()
			conn.close()
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def clear_fields(self):
		self.id_var.set("")
		self.name_var.set("")
		self.brand_var.set("")

	def restore_item(self):
		if not self.id_var.get():
			messagebox.showwarning("Validation Error", "Please enter item ID.")
			return
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			query = "UPDATE inventory SET Deleted=0 WHERE id=%s"
			cursor.execute(query, (int(self.id_var.get()),))
			conn.commit()
			if cursor.rowcount == 0:
				messagebox.showwarning("Restore Failed", "Item ID not found in Recycle Bin.")
			else:
				messagebox.showinfo("Success", "Item restored.")
				self.clear_fields()
			cursor.close()
			conn.close()
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def permanently_delete(self):
		if not self.id_var.get():
			messagebox.showwarning("Validation Error", "Please enter item ID.")
			return
		if not messagebox.askyesno("Confirm Permanent Delete", "This will permanently delete the item. Continue?"):
			return
		try:
			conn = mysql.connector.connect(
				host="127.0.0.1",
				user="root",
				password="",
				database="inventories"
			)
			cursor = conn.cursor()
			query = "DELETE FROM inventory WHERE id=%s"
			cursor.execute(query, (int(self.id_var.get()),))
			conn.commit()
			if cursor.rowcount == 0:
				messagebox.showwarning("Delete Failed", "Item ID not found.")
			else:
				messagebox.showinfo("Success", "Item permanently deleted.")
				self.clear_fields()
			cursor.close()
			conn.close()
		except Error as e:
			messagebox.showerror("Database Error", f"Error: {e}")

	def back_to_main(self):
		self.window.destroy()