from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import mysql.connector


class DeliveryManagement:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.username = main_window.username
        
    def show(self):
        """Display delivery management content"""
        # Clear parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Title with back button
        title_frame = Frame(self.parent_frame, bg="#34495E", height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)
        
        Button(title_frame, text="← Dashboard", bg="#3498db", fg="white",
               font=("Segoe UI", 10, "bold"), command=self.main_window.show_dashboard).pack(side=LEFT, padx=20, pady=15)
        
        # Center the title
        title_container = Frame(title_frame, bg="#34495E")
        title_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        Label(title_container, text="🚛 Delivery Management", bg="#34495E", fg="white",
              font=("Segoe UI", 16, "bold")).pack()
        
        # Content container for centering
        content_container = Frame(self.parent_frame, bg="#2E4057")
        content_container.pack(fill=BOTH, expand=True)
        
        # Center frame - auto-size based on content
        center_frame = Frame(content_container, bg="#2E4057")
        center_frame.pack(expand=True, pady=20, padx=50)
        
        # Action buttons
        action_frame = Frame(center_frame, bg="#2E4057")
        action_frame.pack(fill=X, pady=10)
        
        Button(action_frame, text="Mark as Delivered", bg="#28A745", fg="white", width=20,
               font=("Segoe UI", 10), command=self.mark_as_delivered).pack(side=LEFT, padx=5)
        Button(action_frame, text="Move to Recycle Bin", bg="#FFC107", fg="black", width=22,
               font=("Segoe UI", 10), command=self.move_to_recycle_bin).pack(side=LEFT, padx=5)
        Button(action_frame, text="Delete Permanently", bg="#DC3545", fg="white", width=22,
               font=("Segoe UI", 10), command=self.delete_permanently).pack(side=LEFT, padx=5)
        Button(action_frame, text="Cancel Delivery", bg="#D9534F", fg="white", width=20,
               font=("Segoe UI", 10), command=self.cancel_delivery).pack(side=LEFT, padx=5)
        
        # Deliveries list
        list_frame = Frame(center_frame, bg="#2E4057")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        Label(list_frame, text="Deliveries", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=5)
        
        columns = ("ID", "Item", "Category", "Amount", "Status", "Truck ID", "Delivered At")
        self.delivery_tree = Treeview(list_frame, columns=columns, show="headings", height=15)
        
        widths = [50, 150, 120, 80, 100, 80, 150]
        for col, width in zip(columns, widths):
            self.delivery_tree.heading(col, text=col)
            self.delivery_tree.column(col, width=width, anchor=CENTER)
        
        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.delivery_tree.yview)
        self.delivery_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.delivery_tree.pack(fill=BOTH, expand=True)
        
        # Bottom buttons
        bottom_frame = Frame(center_frame, bg="#2E4057")
        bottom_frame.pack(fill=X, pady=10)
        
        Button(bottom_frame, text="Refresh Dashboard", width=20, bg="#17A2B8", fg="white",
               font=("Segoe UI", 10), command=self.main_window.show_dashboard).pack(side=LEFT, padx=10)
        Button(bottom_frame, text="Logout", width=15, bg="#DC3545", fg="white",
               font=("Segoe UI", 10), command=self.main_window.logout).pack(side=LEFT, padx=10)
        
        self.load_deliveries()
    
    def load_deliveries(self):
        """Load deliveries from database"""
        for item in self.delivery_tree.get_children():
            self.delivery_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, i.Name, i.Category, d.Delivery_Amount, d.Status, 
                       d.truck_id, d.Delivered_at
                FROM deliveries d
                LEFT JOIN inventory i ON d.inventory_id = i.id
                WHERE d.Deleted = 0
                ORDER BY d.id DESC
            """)
            
            for row in cursor.fetchall():
                delivery_id, name, category, amount, status, truck_id, delivered_at = row
                truck_display = truck_id if truck_id else "Not Assigned"
                delivered_display = delivered_at.strftime("%Y-%m-%d %H:%M") if delivered_at else "N/A"
                
                self.delivery_tree.insert("", END, values=(
                    delivery_id, name or "N/A", category or "N/A", amount, 
                    status, truck_display, delivered_display
                ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load deliveries: {e}")
    
    def mark_as_delivered(self):
        """Mark selected delivery as delivered"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a delivery to mark as delivered")
            return
        
        delivery_item = self.delivery_tree.item(selected[0])
        delivery_id = delivery_item['values'][0]
        truck_id = delivery_item['values'][5]
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE deliveries 
                SET Status='Delivered', Delivered_at=NOW() 
                WHERE id=%s
            """, (delivery_id,))
            
            # Free up the truck if assigned
            if truck_id and truck_id != "Not Assigned":
                cursor.execute("UPDATE trucks SET status='Available' WHERE id=%s", (truck_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Delivery marked as delivered!")
            self.load_deliveries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark as delivered: {e}")
    
    def move_to_recycle_bin(self):
        """Move delivery to recycle bin (soft delete)"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a delivery to move to recycle bin")
            return
        
        delivery_item = self.delivery_tree.item(selected[0])
        delivery_id = delivery_item['values'][0]
        
        if messagebox.askyesno("Confirm", "Move this delivery to recycle bin?"):
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                
                cursor.execute("UPDATE deliveries SET Deleted=1 WHERE id=%s", (delivery_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Delivery moved to recycle bin!")
                self.load_deliveries()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move to recycle bin: {e}")
    
    def delete_permanently(self):
        """Permanently delete delivery"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a delivery to delete permanently")
            return
        
        delivery_item = self.delivery_tree.item(selected[0])
        delivery_id = delivery_item['values'][0]
        
        if messagebox.askyesno("Confirm Permanent Delete", "This action cannot be undone. Delete permanently?"):
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM deliveries WHERE id=%s", (delivery_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Delivery permanently deleted!")
                self.load_deliveries()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete permanently: {e}")
    
    def cancel_delivery(self):
        """Cancel selected delivery and return items to inventory"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a delivery to cancel")
            return
        
        delivery_item = self.delivery_tree.item(selected[0])
        delivery_id = delivery_item['values'][0]
        delivery_amount = delivery_item['values'][3]
        truck_id = delivery_item['values'][5]
        
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel this delivery? Items will be returned to inventory."):
            try:
                conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
                cursor = conn.cursor()
                
                # Get delivery details
                cursor.execute("""
                    SELECT inventory_id, Delivery_Amount 
                    FROM deliveries 
                    WHERE id=%s
                """, (delivery_id,))
                result = cursor.fetchone()
                
                if result:
                    inventory_id, amount = result
                    
                    # Return items to inventory
                    cursor.execute("""
                        UPDATE inventory 
                        SET Quantity = Quantity + %s 
                        WHERE id = %s
                    """, (amount, inventory_id))
                    
                    # Mark delivery as deleted
                    cursor.execute("UPDATE deliveries SET Deleted=1 WHERE id=%s", (delivery_id,))
                    
                    # Free up the truck if assigned
                    if truck_id and truck_id != "Not Assigned":
                        try:
                            cursor.execute("UPDATE trucks SET status='Available' WHERE id=%s", (truck_id,))
                        except:
                            pass
                    
                    conn.commit()
                    messagebox.showinfo("Success", f"Delivery cancelled! {amount} items returned to inventory.")
                else:
                    messagebox.showerror("Error", "Delivery not found")
                
                conn.close()
                self.load_deliveries()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel delivery: {e}")
