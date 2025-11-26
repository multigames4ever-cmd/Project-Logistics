"""
Book Delivery Window
Allows booking a delivery for an inventory item.
"""
from tkinter import *
from tkinter import messagebox
import mysql.connector


class BookDeliveryWindow:
        # Book Delivery window for creating deliveries
    def __init__(self, master, username=None, item_id=None, callback=None):
        self.master = master
        self.username = username
        self.item_id = item_id
        self.callback = callback
        
        self.window = Toplevel(master)
        self.window.title("Book Delivery")
        self.window.geometry("750x550")
        self.window.configure(bg="#2C3E50")
        
        self.load_item_details()
        
        if not hasattr(self, 'item_name'):
            return
        
        self.window.update_idletasks()
        width = 750
        height = 550
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        Label(self.window, text="Book Delivery", bg="#2C3E50", fg="white",
              font=("Segoe UI", 16, "bold")).pack(pady=20)
        
        info_frame = Frame(self.window, bg="#34495E", relief=RIDGE, bd=2)
        info_frame.pack(pady=10, padx=50, fill=X)
        
        Label(info_frame, text="", bg="#34495E").pack(pady=10)
        
        Label(info_frame, text=f"Item ID: {self.item_id}", bg="#34495E", fg="white",
              font=("Segoe UI", 13)).pack(anchor=W, padx=30, pady=5)
        Label(info_frame, text=f"Name: {self.item_name}", bg="#34495E", fg="white",
              font=("Segoe UI", 13)).pack(anchor=W, padx=30, pady=5)
        Label(info_frame, text=f"Category: {self.item_category}", bg="#34495E", fg="white",
              font=("Segoe UI", 13)).pack(anchor=W, padx=30, pady=5)
        Label(info_frame, text=f"Available Quantity: {self.item_quantity}", bg="#34495E", fg="white",
              font=("Segoe UI", 13)).pack(anchor=W, padx=30, pady=5)
        Label(info_frame, text=f"Brand: {self.item_brand}", bg="#34495E", fg="white",
              font=("Segoe UI", 13)).pack(anchor=W, padx=30, pady=5)
        
        Label(info_frame, text="", bg="#34495E").pack(pady=10)
        
        amount_frame = Frame(self.window, bg="#2C3E50")
        amount_frame.pack(pady=20)
        
        Label(amount_frame, text="Delivery Amount:", bg="#2C3E50", fg="white",
              font=("Segoe UI", 13)).grid(row=0, column=0, padx=15, pady=5)
        self.amount_entry = Entry(amount_frame, font=("Segoe UI", 13), width=25)
        self.amount_entry.grid(row=0, column=1, padx=15, pady=5)
        
        btn_frame = Frame(self.window, bg="#2C3E50")
        btn_frame.pack(pady=20)
        
        Button(btn_frame, text="Book Delivery", bg="#52BE80", fg="white",
               font=("Segoe UI", 12), width=18, command=self.book_delivery).pack(side=LEFT, padx=15)
        Button(btn_frame, text="Cancel", bg="#ABB2B9", fg="white",
               font=("Segoe UI", 12), width=15, command=self.window.destroy).pack(side=LEFT, padx=15)
    
    def load_item_details(self):
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT Name, Category, Quantity, Brand FROM inventory WHERE id=%s AND (Deleted=0 OR Deleted IS NULL)", (self.item_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.item_name = result[0]
                self.item_category = result[1]
                self.item_quantity = result[2]
                self.item_brand = result[3]
            else:
                messagebox.showerror("Error", "Item not found")
                if hasattr(self, 'window'):
                    self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load item details: {e}")
            if hasattr(self, 'window'):
                self.window.destroy()
    
    def book_delivery(self):
        delivery_amount = self.amount_entry.get().strip()
        
        if not delivery_amount:
            messagebox.showwarning("Input Required", "Please enter delivery amount")
            return
        
        try:
            delivery_amount = int(delivery_amount)
            if delivery_amount <= 0:
                messagebox.showwarning("Invalid Amount", "Delivery amount must be greater than 0")
                return
            if delivery_amount > self.item_quantity:
                messagebox.showwarning("Insufficient Quantity",
                                     f"Cannot deliver {delivery_amount}. Only {self.item_quantity} available.")
                return
            
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO deliveries (inventory_id, Name, Category, Delivery_Amount, Status, Deleted)
                    VALUES (%s, %s, %s, %s, 'Pending', 0)
                """, (self.item_id, self.item_name, self.item_category, delivery_amount))
                
                cursor.execute("""
                    UPDATE inventory 
                    SET Quantity = Quantity - %s 
                    WHERE id = %s
                """, (delivery_amount, self.item_id))
                
                conn.commit()
                
                if self.callback:
                    self.callback()
                
                self.window.destroy()
                
            except mysql.connector.Error as db_err:
                conn.rollback()
                messagebox.showerror("Database Error", f"Failed to book delivery: {db_err}")
            finally:
                conn.close()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Delivery amount must be a number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to book delivery: {e}")


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    BookDeliveryWindow(root, "user", 1)
    root.mainloop()
