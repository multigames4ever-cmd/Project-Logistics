"""
Main dashboard window for Project Logistics.
Handles navigation, statistics, and launching management windows.
"""
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview, Notebook
import os
import mysql.connector
from mysql.connector import Error
from fleet_management import FleetManagement
from inventory import InventoryManagement
from delivery_management import DeliveryManagement
from realtimetracker import RealTimeTracker

class MainWindow:
        # Main application window initialization
    def __init__(self, master, username):
        self.window = master
        self.username = username
        self.window.title(f"Main Window - {username}")
        self.window.geometry("1400x800")
        self.window.resizable(True, True)
        self.window.config(bg="#2E4057")

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
            if os.path.exists(icon_path):
                self.icon = PhotoImage(file=icon_path)
                self.window.iconphoto(True, self.icon)
        except Exception:
            pass

        self.center_window()
        self.create_widgets()
        
        self.fleet_mgmt = None
        self.inventory_mgmt = None
        self.delivery_mgmt = None
        self.tracker = None

    def center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
            # Create header and main layout
        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=0)
        self.window.grid_columnconfigure(0, weight=1)

        header = Label(self.window, text=f"Project Logistics Dashboard - Welcome, {self.username}!",
                       bg="#2E4057", fg="white", font=("Segoe UI", 16, "bold"))
        header.grid(row=0, column=0, pady=20)

        # Create scrollable container
        canvas_frame = Frame(self.window, bg="#2E4057")
        canvas_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Create canvas and scrollbars
        self.canvas = Canvas(canvas_frame, bg="#2E4057", highlightthickness=0)
        v_scrollbar = Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        h_scrollbar = Scrollbar(canvas_frame, orient=HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        def on_mousewheel(event):
            try:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.main_frame = Frame(self.canvas, bg="#2E4057")
        self.canvas.create_window((50, 30), window=self.main_frame, anchor='nw')
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        # Statistics Panel
        stats_frame = Frame(self.main_frame, bg="#34495E", relief=RAISED, bd=2)
        stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        stats_frame.grid_rowconfigure(0, weight=0)
        stats_frame.grid_rowconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)

        Label(stats_frame, text="Statistics Overview", bg="#34495E", fg="white", 
              font=("Segoe UI", 12, "bold")).grid(row=0, column=0, pady=10)
        self.stats_content = Frame(stats_frame, bg="#34495E")
        self.stats_content.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Fleet Status Panel
        trucks_frame = Frame(self.main_frame, bg="#34495E", relief=RAISED, bd=2)
        trucks_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        trucks_frame.grid_rowconfigure(0, weight=0)
        trucks_frame.grid_rowconfigure(1, weight=1)
        trucks_frame.grid_columnconfigure(0, weight=1)

        Label(trucks_frame, text="Fleet Status", bg="#34495E", fg="white", 
              font=("Segoe UI", 12, "bold")).grid(row=0, column=0, pady=10)
        self.trucks_content = Frame(trucks_frame, bg="#34495E")
        self.trucks_content.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Navigation Panel
        nav_frame = Frame(self.main_frame, bg="#34495E", relief=RAISED, bd=2)
        nav_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        nav_frame.grid_rowconfigure(0, weight=0)
        nav_frame.grid_rowconfigure(1, weight=1)
        nav_frame.grid_columnconfigure(0, weight=1)

        Label(nav_frame, text="Quick Navigation", bg="#34495E", fg="white", 
              font=("Segoe UI", 12, "bold")).grid(row=0, column=0, pady=10)
        nav_buttons = Frame(nav_frame, bg="#34495E")
        nav_buttons.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        Button(nav_buttons, text="Delivery Management", width=20, bg="#28A745", fg="white",
               command=self.open_delivery).pack(pady=5, fill=X)
        Button(nav_buttons, text="Fleet Management", width=20, bg="#007BFF", fg="white",
               command=self.open_fleet).pack(pady=5, fill=X)
        Button(nav_buttons, text="Inventory", width=20, bg="#FD7E14", fg="white",
               command=self.open_inventory).pack(pady=5, fill=X)
        Button(nav_buttons, text="Real-time Tracker", width=20, bg="#6610F2", fg="white",
               command=self.open_tracker).pack(pady=5, fill=X)
        Button(nav_buttons, text="Recycle Bin", width=20, bg="#6C757D", fg="white",
               command=self.open_recycle_bin).pack(pady=5, fill=X)

        # Recent Deliveries Panel
        recent_frame = Frame(self.main_frame, bg="#34495E", relief=RAISED, bd=2)
        recent_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        recent_frame.grid_rowconfigure(0, weight=0)
        recent_frame.grid_rowconfigure(1, weight=1)
        recent_frame.grid_columnconfigure(0, weight=1)

        Label(recent_frame, text="Recent Deliveries", bg="#34495E", fg="white", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, pady=10)
        tree_container = Frame(recent_frame, bg="#34495E")
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        scrollbar = Scrollbar(tree_container)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.recent_tree = Treeview(tree_container, columns=("DelID", "Name", "Truck", "Status", "Date"), height=10, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.recent_tree.yview)
        self.recent_tree.column("#0", width=0, stretch=NO)
        self.recent_tree.column("DelID", anchor=CENTER, width=60)
        self.recent_tree.column("Name", anchor=W, width=150)
        self.recent_tree.column("Truck", anchor=CENTER, width=80)
        self.recent_tree.column("Status", anchor=W, width=120)
        self.recent_tree.column("Date", anchor=W, width=140)
        self.recent_tree.heading("#0", text="", anchor=W)
        self.recent_tree.heading("DelID", text="Del ID", anchor=CENTER)
        self.recent_tree.heading("Name", text="Item Name", anchor=W)
        self.recent_tree.heading("Truck", text="Truck", anchor=CENTER)
        self.recent_tree.heading("Status", text="Status", anchor=W)
        self.recent_tree.heading("Date", text="Date", anchor=W)
        self.recent_tree.grid(row=0, column=0, sticky="nsew")


        # Button frame
        button_frame = Frame(self.window, bg="#2E4057")
        button_frame.grid(row=2, column=0, pady=20)
        
        Button(button_frame, text="Logout", width=12, bg="#DC3545", fg="white", 
               command=self.logout).pack(side=LEFT, padx=10)

        # Configure canvas scroll region
        def configure_scroll_region(event):
            try:
                if self.main_frame.winfo_exists():
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    canvas_width = self.canvas.winfo_width()
                    frame_width = self.main_frame.winfo_reqwidth()
                    if canvas_width > frame_width:
                        x_offset = (canvas_width - frame_width) // 2
                        canvas_items = self.canvas.find_all()
                        if canvas_items:
                            self.canvas.coords(canvas_items[0], x_offset, 30)
            except:
                pass
        
        self.main_frame.bind('<Configure>', configure_scroll_region)
        self.canvas.bind('<Configure>', configure_scroll_region)
        
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        self.load_statistics()
        self.load_fleet_status()
        self.load_recent_deliveries()

    def load_statistics(self):
        for child in self.stats_content.winfo_children():
            child.destroy()

        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM inventory WHERE (Deleted=0 OR Deleted IS NULL)")
            total_items = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM inventory WHERE (Deleted=0 OR Deleted IS NULL) AND Quantity > 0")
            items_in_stock = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='Pending' AND (Deleted=0 OR Deleted IS NULL)")
            pending_deliveries = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='In Transit' AND (Deleted=0 OR Deleted IS NULL)")
            active_deliveries = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM deliveries WHERE Status='Delivered' AND (Deleted=0 OR Deleted IS NULL)")
            completed_deliveries = cursor.fetchone()[0] or 0

            cursor.close()
            conn.close()

            stats = [
                ("Total Items", total_items, "#28A745"),
                ("In Stock", items_in_stock, "#007BFF"),
                ("Pending Delivery", pending_deliveries, "#FFC107"),
                ("Active Deliveries", active_deliveries, "#17A2B8"),
                ("Completed", completed_deliveries, "#6C757D")
            ]

            for i, (label, value, color) in enumerate(stats):
                stat_frame = Frame(self.stats_content, bg=color, relief=RAISED, bd=1)
                stat_frame.grid(row=i, column=0, pady=3, padx=5, sticky="ew")
                self.stats_content.grid_columnconfigure(0, weight=1)
                
                Label(stat_frame, text=str(value), bg=color, fg="white", 
                      font=("Segoe UI", 12, "bold")).pack(pady=1)
                Label(stat_frame, text=label, bg=color, fg="white", 
                      font=("Segoe UI", 8)).pack(pady=1)

        except Error as e:
            Label(self.stats_content, text=f"Error: {e}", bg="#34495E", fg="red", 
                  wraplength=200).pack(pady=10)

    def load_fleet_status(self):
        for child in self.trucks_content.winfo_children():
            child.destroy()

        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM trucks WHERE (Deleted=0 OR Deleted IS NULL)")
            total_trucks = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='Available' AND (Deleted=0 OR Deleted IS NULL)")
            available_trucks = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='In Use' AND (Deleted=0 OR Deleted IS NULL)")
            in_use_trucks = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM trucks WHERE status='Maintenance' AND (Deleted=0 OR Deleted IS NULL)")
            maintenance_trucks = cursor.fetchone()[0] or 0

            cursor.close()
            conn.close()

            fleet_stats = [
                ("Total Trucks", total_trucks, "#17A2B8"),
                ("Available", available_trucks, "#28A745"),
                ("In Use", in_use_trucks, "#FFC107"),
                ("Maintenance", maintenance_trucks, "#DC3545")
            ]

            for i, (label, value, color) in enumerate(fleet_stats):
                stat_frame = Frame(self.trucks_content, bg=color, relief=RAISED, bd=1)
                stat_frame.grid(row=i, column=0, pady=3, padx=5, sticky="ew")
                self.trucks_content.grid_columnconfigure(0, weight=1)
                
                Label(stat_frame, text=str(value), bg=color, fg="white", 
                      font=("Segoe UI", 12, "bold")).pack(pady=1)
                Label(stat_frame, text=label, bg=color, fg="white", 
                      font=("Segoe UI", 8)).pack(pady=1)

        except Error as e:
            Label(self.trucks_content, text=f"Error: {e}", bg="#34495E", fg="red", 
                  wraplength=200).pack(pady=10)

    def load_recent_deliveries(self):
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)

        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT d.id, i.Name, t.license_plate, d.Status, d.Delivered_at 
                FROM deliveries d 
                LEFT JOIN inventory i ON d.inventory_id = i.id
                LEFT JOIN trucks t ON d.truck_id = t.id 
                WHERE d.Deleted=0
                ORDER BY d.id DESC LIMIT 10
            """)
            deliveries = cursor.fetchall()

            if deliveries:
                for delivery in deliveries:
                    delivery_id, name, truck, status, date = delivery
                    truck_display = truck if truck else "Not Assigned"
                    date_display = date.strftime("%Y-%m-%d %H:%M") if date else "Pending"
                    
                    self.recent_tree.insert("", "end", values=(
                        delivery_id, name or "Unknown Item", truck_display, status or "Pending", date_display
                    ))
            else:
                self.recent_tree.insert("", "end", values=("--", "No deliveries", "--", "--", "--"))

            cursor.close()
            conn.close()

        except Error as e:
            self.recent_tree.insert("", "end", values=("Error", f"Database error: {e}", "--", "--", "--"))

    def clear_main_content(self):
        """Clear the main canvas content area"""
        try:
            self.canvas.unbind('<Configure>')
        except:
            pass
        for widget in self.canvas.winfo_children():
            try:
                widget.unbind('<Configure>')
            except:
                pass
            widget.destroy()
    
    def show_dashboard(self):
            # Show the main dashboard view
        try:
            self.canvas.unbind('<Configure>')
        except:
            pass
        self.clear_main_content()
        
        # Clear all existing widgets from window before recreating dashboard
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.create_widgets()
    
    def open_delivery(self):
            # Open the Delivery Management window
        self.clear_main_content()
        container = Frame(self.canvas, bg="#2E4057")
        canvas_window = self.canvas.create_window((0, 0), window=container, anchor='nw')
        
        content_frame = Frame(container, bg="#2E4057", width=1300)
        content_frame.pack(padx=50, pady=20)
        
        if not self.delivery_mgmt:
            self.delivery_mgmt = DeliveryManagement(content_frame, self)
        else:
            self.delivery_mgmt.parent_frame = content_frame
        self.delivery_mgmt.show()
        
        def center_content(event=None):
            try:
                if container.winfo_exists():
                    container.update_idletasks()
                    canvas_width = self.canvas.winfo_width()
                    content_width = container.winfo_reqwidth()
                    x_offset = max(0, (canvas_width - content_width) // 2)
                    self.canvas.coords(canvas_window, x_offset, 0)
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        
        self.canvas.bind('<Configure>', center_content)
        content_frame.bind('<Configure>', center_content)
        center_content()
    
    def open_fleet(self):
            # Open the Fleet Management window
        self.clear_main_content()
        
        container = Frame(self.canvas, bg="#2E4057")
        canvas_window = self.canvas.create_window((0, 0), window=container, anchor='nw')
        
        content_frame = Frame(container, bg="#2E4057", width=1300)
        content_frame.pack(padx=50, pady=20)
        
        if not self.fleet_mgmt:
            self.fleet_mgmt = FleetManagement(content_frame, self)
        else:
            self.fleet_mgmt.parent_frame = content_frame
        self.fleet_mgmt.show()
        
        def center_content(event=None):
            try:
                if container.winfo_exists():
                    container.update_idletasks()
                    canvas_width = self.canvas.winfo_width()
                    content_width = container.winfo_reqwidth()
                    x_offset = max(0, (canvas_width - content_width) // 2)
                    self.canvas.coords(canvas_window, x_offset, 0)
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        
        self.canvas.bind('<Configure>', center_content)
        content_frame.bind('<Configure>', center_content)
        center_content()
    
    def open_inventory(self):
            # Open the Inventory Management window
        self.clear_main_content()
        
        container = Frame(self.canvas, bg="#2E4057")
        canvas_window = self.canvas.create_window((0, 0), window=container, anchor='nw')
        
        content_frame = Frame(container, bg="#2E4057", width=1300)
        content_frame.pack(padx=50, pady=20)
        
        if not self.inventory_mgmt:
            self.inventory_mgmt = InventoryManagement(content_frame, self)
        else:
            self.inventory_mgmt.parent_frame = content_frame
        self.inventory_mgmt.show()
        
        def center_content(event=None):
            try:
                if container.winfo_exists():
                    container.update_idletasks()
                    canvas_width = self.canvas.winfo_width()
                    content_width = container.winfo_reqwidth()
                    x_offset = max(0, (canvas_width - content_width) // 2)
                    self.canvas.coords(canvas_window, x_offset, 0)
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        
        self.canvas.bind('<Configure>', center_content)
        content_frame.bind('<Configure>', center_content)
        center_content()
    
    def open_tracker(self):
            # Open the Real-Time Tracker window
        self.clear_main_content()
        
        container = Frame(self.canvas, bg="#2E4057")
        canvas_window = self.canvas.create_window((0, 0), window=container, anchor='nw')
        
        content_frame = Frame(container, bg="#2E4057", width=1300)
        content_frame.pack(padx=50, pady=20)
        
        if not self.tracker:
            self.tracker = RealTimeTracker(content_frame, self)
        else:
            self.tracker.parent_frame = content_frame
        self.tracker.show()
        
        def center_content(event=None):
            try:
                if container.winfo_exists():
                    container.update_idletasks()
                    canvas_width = self.canvas.winfo_width()
                    content_width = container.winfo_reqwidth()
                    x_offset = max(0, (canvas_width - content_width) // 2)
                    self.canvas.coords(canvas_window, x_offset, 0)
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        
        self.canvas.bind('<Configure>', center_content)
        content_frame.bind('<Configure>', center_content)
        center_content()
    
    def open_recycle_bin(self):
            # Open the Recycle Bin window
        self.clear_main_content()
        container = Frame(self.canvas, bg="#2E4057")
        canvas_window = self.canvas.create_window((0, 0), window=container, anchor='nw')
        topbar_outer = Frame(container, bg="#2E4057")
        topbar_outer.pack(pady=(30,0))
        topbar_bg = Frame(topbar_outer, bg="#3B4A5A", width=700, height=40)
        topbar_bg.pack()
        topbar_bg.pack_propagate(False)
        top_bar = Frame(topbar_bg, bg="#3B4A5A")
        top_bar.pack(fill="both", expand=True)
        back_btn = Button(top_bar, text="\u2190 Dashboard", bg="#29A8DF", fg="white", font=("Segoe UI", 12, "bold"), relief=RAISED, bd=3, padx=8, pady=1, command=self.show_dashboard)
        back_btn.pack(side="left", padx=(8, 0), pady=8)
        title_lbl = Label(top_bar, text="🗑 Recycle Bin", bg="#3B4A5A", fg="white", font=("Segoe UI", 16, "bold"))
        title_lbl.pack(side="left", padx=(18,0), pady=8, fill="x", expand=True)
        right_spacer = Frame(top_bar, bg="#3B4A5A")
        right_spacer.pack(side="left", fill="x", expand=True)
        content_border = Frame(container, bg="#C0C8D2", highlightbackground="#C0C8D2", highlightthickness=2)
        content_border.pack(pady=(30,0))
        content_frame = Frame(content_border, bg="white", width=700, height=320)
        content_frame.pack(padx=2, pady=2)
        content_frame.pack_propagate(False)
        self.show_recycle_bin(content_frame, show_title=False)
        def center_content(event=None):
            try:
                if container.winfo_exists():
                    container.update_idletasks()
                    canvas_width = self.canvas.winfo_width()
                    content_width = container.winfo_reqwidth()
                    x_offset = max(0, (canvas_width - content_width) // 2)
                    self.canvas.coords(canvas_window, x_offset, 0)
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        self.canvas.bind('<Configure>', center_content)
        container.bind('<Configure>', center_content)
        center_content()

    def show_recycle_bin(self, parent, show_title=True):
        if show_title:
            header = Label(parent, text="Recycle Bin Management", bg="#2E4057", fg="white", font=("Segoe UI", 18, "bold"))
            header.pack(pady=10)
        tab_control = Notebook(parent)
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        inv_tab = Frame(tab_control, bg="#34495E")
        del_tab = Frame(tab_control, bg="#34495E")
        tab_control.add(inv_tab, text="Inventory")
        tab_control.add(del_tab, text="Deliveries")
        # Inventory Tree
        columns = ("ID", "Name", "Category", "Brand", "Quantity")
        inv_tree = Treeview(inv_tab, columns=columns, show="headings")
        for col, w in zip(columns, [60, 180, 120, 120, 80]):
            inv_tree.heading(col, text=col)
            inv_tree.column(col, width=w)
        inv_tree.pack(expand=1, fill="both", padx=10, pady=10)
        self.load_recycle_inventory(inv_tree)
        btn_frame = Frame(inv_tab, bg="#34495E")
        btn_frame.pack(fill=X, padx=10, pady=5)
        Button(btn_frame, text="Restore", width=14, bg="#28A745", fg="white", command=lambda: self.restore_inventory(inv_tree)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Delete Permanently", width=18, bg="#8B0000", fg="white", command=lambda: self.delete_inventory(inv_tree)).pack(side=LEFT, padx=5)
        # Deliveries Tree
        columns_del = ("ID", "Name", "Truck", "Status", "Date")
        del_tree = Treeview(del_tab, columns=columns_del, show="headings")
        for col, w in zip(columns_del, [60, 180, 120, 120, 140]):
            del_tree.heading(col, text=col)
            del_tree.column(col, width=w)
        del_tree.pack(expand=1, fill="both", padx=10, pady=10)
        self.load_recycle_deliveries(del_tree)
        btn_frame_del = Frame(del_tab, bg="#34495E")
        btn_frame_del.pack(fill=X, padx=10, pady=5)
        Button(btn_frame_del, text="Restore", width=14, bg="#28A745", fg="white", command=lambda: self.restore_delivery(del_tree)).pack(side=LEFT, padx=5)
        Button(btn_frame_del, text="Delete Permanently", width=18, bg="#8B0000", fg="white", command=lambda: self.delete_delivery(del_tree)).pack(side=LEFT, padx=5)

    def setup_recycle_inventory_tab(self):
        columns = ("ID", "Name", "Category", "Brand", "Quantity")
        self.inv_tree = Treeview(self.recycle_inventory_tab, columns=columns, show="headings")
        for col, w in zip(columns, [60, 180, 120, 120, 80]):
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=w)
        self.inv_tree.pack(expand=1, fill="both", padx=10, pady=10)
        self.load_recycle_inventory(self.inv_tree)
        btn_frame = Frame(self.recycle_inventory_tab, bg="#34495E")
        btn_frame.pack(fill=X, padx=10, pady=5)
        Button(btn_frame, text="Restore", width=14, bg="#28A745", fg="white", command=lambda: self.restore_inventory(self.inv_tree)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Delete Permanently", width=18, bg="#8B0000", fg="white", command=lambda: self.delete_inventory(self.inv_tree)).pack(side=LEFT, padx=5)

    def setup_recycle_deliveries_tab(self):
        columns = ("ID", "Name", "Truck", "Status", "Date")
        self.del_tree = Treeview(self.recycle_deliveries_tab, columns=columns, show="headings")
        for col, w in zip(columns, [60, 180, 120, 120, 140]):
            self.del_tree.heading(col, text=col)
            self.del_tree.column(col, width=w)
        self.del_tree.pack(expand=1, fill="both", padx=10, pady=10)
        self.load_recycle_deliveries(self.del_tree)
        btn_frame = Frame(self.recycle_deliveries_tab, bg="#34495E")
        btn_frame.pack(fill=X, padx=10, pady=5)
        Button(btn_frame, text="Restore", width=14, bg="#28A745", fg="white", command=lambda: self.restore_delivery(self.del_tree)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Delete Permanently", width=18, bg="#8B0000", fg="white", command=lambda: self.delete_delivery(self.del_tree)).pack(side=LEFT, padx=5)

    def load_recycle_inventory(self, tree):
        tree.delete(*tree.get_children())
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Name, Category, Brand, Quantity FROM inventory WHERE Deleted=1")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading recycled inventory: {e}")

    def restore_inventory(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an inventory item to restore.")
            return
        item_id = tree.item(selected[0], 'values')[0]
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET Deleted=0 WHERE ID=%s", (item_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Restored", "Inventory item restored.")
            self.load_recycle_inventory(tree)
        except Error as e:
            messagebox.showerror("Database Error", f"Error restoring item: {e}")

    def delete_inventory(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an inventory item to delete.")
            return
        item_id = tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("Confirm Delete", "Permanently delete this inventory item?"):
            return
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE ID=%s", (item_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Deleted", "Inventory item permanently deleted.")
            self.load_recycle_inventory(tree)
        except Error as e:
            messagebox.showerror("Database Error", f"Error deleting item: {e}")

    def load_recycle_deliveries(self, tree):
        tree.delete(*tree.get_children())
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.ID, i.Name, t.license_plate, d.Status, d.Delivered_at
                FROM deliveries d
                LEFT JOIN inventory i ON d.inventory_id = i.ID
                LEFT JOIN trucks t ON d.truck_id = t.ID
                WHERE d.Deleted=1
                ORDER BY d.ID DESC
            """)
            for row in cursor.fetchall():
                delivery_id, name, truck, status, date = row
                truck_display = truck if truck else "Not Assigned"
                date_display = date.strftime("%Y-%m-%d %H:%M") if date else "Pending"
                tree.insert("", "end", values=(delivery_id, name or "Unknown Item", truck_display, status or "Pending", date_display))
            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading recycled deliveries: {e}")

    def restore_delivery(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Delivery", "Please select a delivery to restore.")
            return
        delivery_id = tree.item(selected[0], 'values')[0]
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("UPDATE deliveries SET Deleted=0 WHERE ID=%s", (delivery_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Restored", "Delivery restored.")
            self.load_recycle_deliveries(tree)
        except Error as e:
            messagebox.showerror("Database Error", f"Error restoring delivery: {e}")

    def delete_delivery(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Delivery", "Please select a delivery to delete.")
            return
        delivery_id = tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("Confirm Delete", "Permanently delete this delivery?"):
            return
        try:
            conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="inventories")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM deliveries WHERE ID=%s", (delivery_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Deleted", "Delivery permanently deleted.")
            self.load_recycle_deliveries(tree)
        except Error as e:
            messagebox.showerror("Database Error", f"Error deleting delivery: {e}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.window.destroy()
            #Return to login window
            from login import LoginWindow
            new_root = Tk()
            login_app = LoginWindow(new_root)
            login_app.run()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    root = Tk()
    app = MainWindow(root, "test_user")
    app.run()
