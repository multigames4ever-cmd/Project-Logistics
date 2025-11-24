from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import mysql.connector


class RealTimeTracker:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.username = main_window.username
        
    def show(self):
        """Display real-time tracker content"""
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
        Label(title_container, text="📍 Real-Time Tracker", bg="#34495E", fg="white",
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
        
        Button(action_frame, text="Refresh", bg="#17A2B8", fg="white", width=18,
               font=("Segoe UI", 10), command=self.load_active_deliveries).pack(side=LEFT, padx=5)
        
        # Active deliveries list
        list_frame = Frame(center_frame, bg="#2E4057")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        Label(list_frame, text="Active Deliveries (In Transit)", bg="#2E4057", fg="white",
              font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=5)
        
        columns = ("Delivery ID", "Item", "Amount", "Truck ID", "License Plate", "Status")
        self.tracker_tree = Treeview(list_frame, columns=columns, show="headings", height=12)
        
        widths = [100, 200, 100, 100, 150, 120]
        for col, width in zip(columns, widths):
            self.tracker_tree.heading(col, text=col)
            self.tracker_tree.column(col, width=width, anchor=CENTER)
        
        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.tracker_tree.yview)
        self.tracker_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tracker_tree.pack(fill=BOTH, expand=True)
        
        # Statistics frame
        stats_frame = Frame(self.parent_frame, bg="#34495E", relief=RIDGE, bd=2)
        stats_frame.pack(fill=X, pady=10, padx=20)
        
        Label(stats_frame, text="📊 Statistics", bg="#34495E", fg="white",
              font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        self.stats_container = Frame(stats_frame, bg="#34495E")
        self.stats_container.pack(pady=10, padx=20, fill=X)
        
        # Bottom buttons
        bottom_frame = Frame(content_container, bg="#2E4057")
        bottom_frame.pack(fill=X, pady=10, padx=50)
        
        Button(bottom_frame, text="Refresh Dashboard", width=20, bg="#17A2B8", fg="white",
               font=("Segoe UI", 10), command=self.main_window.show_dashboard).pack(side=LEFT, padx=10)
        Button(bottom_frame, text="Logout", width=15, bg="#DC3545", fg="white",
               font=("Segoe UI", 10), command=self.main_window.logout).pack(side=LEFT, padx=10)
        
        self.load_active_deliveries()
        self.load_statistics()
    
    def load_active_deliveries(self):
        """Load active deliveries (In Transit)"""
        for item in self.tracker_tree.get_children():
            self.tracker_tree.delete(item)
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, i.Name, d.Delivery_Amount, d.truck_id, 
                       t.license_plate, d.Status
                FROM deliveries d
                LEFT JOIN inventory i ON d.inventory_id = i.id
                LEFT JOIN trucks t ON d.truck_id = t.id
                WHERE d.Status = 'In Transit' AND d.Deleted = 0
                ORDER BY d.id DESC
            """)
            
            for row in cursor.fetchall():
                delivery_id, name, amount, truck_id, license_plate, status = row
                self.tracker_tree.insert("", END, values=(
                    delivery_id,
                    name or "N/A",
                    amount,
                    truck_id if truck_id else "N/A",
                    license_plate or "N/A",
                    f"🚚 {status}"
                ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load active deliveries: {e}")
    
    def load_statistics(self):
        """Load delivery statistics"""
        # Clear existing stats
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            
            # Total deliveries
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Deleted=0")
            total = cursor.fetchone()[0]
            
            # Pending deliveries
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='Pending' AND Deleted=0")
            pending = cursor.fetchone()[0]
            
            # In Transit deliveries
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='In Transit' AND Deleted=0")
            in_transit = cursor.fetchone()[0]
            
            # Delivered
            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='Delivered' AND Deleted=0")
            delivered = cursor.fetchone()[0]
            
            # Available trucks
            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='Available' AND deleted=0")
            available_trucks = cursor.fetchone()[0]
            
            # Trucks in use
            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='In Use' AND deleted=0")
            trucks_in_use = cursor.fetchone()[0]
            
            conn.close()
            
            # Display stats in grid
            stats = [
                ("Total Deliveries", total, "#3498DB"),
                ("Pending", pending, "#F39C12"),
                ("In Transit", in_transit, "#9B59B6"),
                ("Delivered", delivered, "#27AE60"),
                ("Available Trucks", available_trucks, "#1ABC9C"),
                ("Trucks in Use", trucks_in_use, "#E74C3C")
            ]
            
            for idx, (label, value, color) in enumerate(stats):
                stat_box = Frame(self.stats_container, bg=color, relief=RAISED, bd=2)
                stat_box.grid(row=idx//3, column=idx%3, padx=10, pady=10, sticky=NSEW)
                
                Label(stat_box, text=str(value), bg=color, fg="white",
                      font=("Segoe UI", 20, "bold")).pack(pady=(10, 5))
                Label(stat_box, text=label, bg=color, fg="white",
                      font=("Segoe UI", 10)).pack(pady=(0, 10))
            
            # Configure grid weights
            for i in range(3):
                self.stats_container.grid_columnconfigure(i, weight=1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {e}")
