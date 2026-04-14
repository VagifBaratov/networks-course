#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ftplib
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from typing import Optional

class FTPClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FTP Client")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.ftp = None
        self.connected = False
        self.current_path = "/"
        
        self.create_widgets()
        
    def create_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        main_container.grid_rowconfigure(0, weight=0)  # хедер
        main_container.grid_rowconfigure(1, weight=0)  # путь
        main_container.grid_rowconfigure(2, weight=3)  # файлы
        main_container.grid_rowconfigure(3, weight=0)  # операции
        main_container.grid_rowconfigure(4, weight=1)  # содержимое
        main_container.grid_columnconfigure(0, weight=1)

        #хедер
        connection_frame = ttk.LabelFrame(main_container, text="Connection Settings", padding=10)
        connection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(connection_frame, text="Server:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.server_entry = ttk.Entry(connection_frame, width=20)
        self.server_entry.grid(row=0, column=1, padx=5)
        self.server_entry.insert(0, "127.0.0.1")
        
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.grid(row=0, column=3, padx=5)
        self.port_entry.insert(0, "21")
        
        ttk.Label(connection_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.username_entry = ttk.Entry(connection_frame, width=20)
        self.username_entry.grid(row=1, column=1, padx=5)
        self.username_entry.insert(0, "TestUser")
        
        ttk.Label(connection_frame, text="Password:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.password_entry = ttk.Entry(connection_frame, width=20, show="*")
        self.password_entry.grid(row=1, column=3, padx=5)
        self.password_entry.insert(0, "")
        
        self.connect_btn = ttk.Button(connection_frame, text="Connect", command=self.connect)
        self.connect_btn.grid(row=0, column=4, rowspan=2, padx=20, sticky=tk.NSEW)
        
        self.status_label = ttk.Label(connection_frame, text="● Disconnected", foreground="red")
        self.status_label.grid(row=0, column=5, rowspan=2, padx=10)
        
        #путь
        path_frame = ttk.Frame(main_container)
        path_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(path_frame, text="Current path:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar(value="/")
        self.path_label = ttk.Label(path_frame, textvariable=self.path_var, 
                                    font=("Courier", 10, "bold"))
        self.path_label.pack(side=tk.LEFT, padx=5)
        
        self.up_btn = ttk.Button(path_frame, text="⬆", command=self.go_up, width=8)
        self.up_btn.pack(side=tk.RIGHT, padx=5)
        
        #файлы
        main_frame = ttk.Frame(main_container)
        main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        columns = ("type", "name", "size", "modified")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="tree headings", height=15)

        self.tree.heading("#0", text="")
        self.tree.heading("type", text="Type")
        self.tree.heading("name", text="Name")
        self.tree.heading("size", text="Size (bytes)")
        self.tree.heading("modified", text="Modified")

        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("type", width=80, minwidth=80)
        self.tree.column("name", width=350, minwidth=200)  # Увеличил для лучшего вида
        self.tree.column("size", width=100, minwidth=80)
        self.tree.column("modified", width=150, minwidth=120)

        # скроллбар
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_item_double_click)

        #операции
        operations_frame = ttk.LabelFrame(main_container, text="File Operations", padding=10)
        operations_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        btn_frame = ttk.Frame(operations_frame)
        btn_frame.pack(fill=tk.X)
        
        self.create_btn = ttk.Button(btn_frame, text="Create", command=self.create_file, width=12)
        self.create_btn.pack(side=tk.LEFT, padx=5)
        
        self.retrieve_btn = ttk.Button(btn_frame, text="Retrieve", command=self.retrieve_file, width=12)
        self.retrieve_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(btn_frame, text="Update", command=self.update_file, width=12)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_file, width=12)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.mkdir_btn = ttk.Button(btn_frame, text="Create Dir", command=self.create_directory, width=10)
        self.mkdir_btn.pack(side=tk.LEFT, padx=2)

        self.rmdir_btn = ttk.Button(btn_frame, text="Remove Dir", command=self.remove_directory, width=12)
        self.rmdir_btn.pack(side=tk.LEFT, padx=2)

        self.refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_file_list, width=12)
        self.refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(operations_frame, text="Filename:").pack(side=tk.LEFT, padx=(10, 5))
        self.filename_entry = ttk.Entry(operations_frame, width=30)
        self.filename_entry.pack(side=tk.LEFT, padx=5)
        
        #содержимое
        output_frame = ttk.LabelFrame(main_container, text="File Content Output", padding=10)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=8)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.set_buttons_state(False)
        
    def set_buttons_state(self, state: bool):
        state = tk.NORMAL if state else tk.DISABLED
        self.create_btn.config(state=state)
        self.retrieve_btn.config(state=state)
        self.update_btn.config(state=state)
        self.delete_btn.config(state=state)
        self.mkdir_btn.config(state=state)
        self.rmdir_btn.config(state=state)
        self.refresh_btn.config(state=state)
        self.up_btn.config(state=state)
    
    def connect(self):
        server = self.server_entry.get().strip()
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not server:
            messagebox.showerror("Error", "Please enter server address")
            return
        
        try:
            port = int(port_str) if port_str else 21
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        try:
            if self.ftp:
                try:
                    self.ftp.quit()
                except:
                    pass
                self.ftp = None
            
            self.ftp = ftplib.FTP()
            self.ftp.connect(server, port)
            self.ftp.login(username, password)
            
            self.connected = True
            self.current_path = "/"
            self.path_var.set("/")

            self.status_label.config(text="● Connected", foreground="green")
            self.connect_btn.config(text="Disconnect", command=self.disconnect)
            
            self.set_buttons_state(True)

            self.refresh_file_list()
            
        except ftplib.all_errors as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
            self.connected = False
            self.status_label.config(text="● Disconnected", foreground="red")
            self.connect_btn.config(text="Connect")
            self.set_buttons_state(False)
    
    def disconnect(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
        
        self.connected = False
        self.status_label.config(text="● Disconnected", foreground="red")
        self.connect_btn.config(text="Connect", command=self.connect)
        
        self.set_buttons_state(False)

    def refresh_file_list(self):
        if not self.connected or not self.ftp:
            return
        
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            files = []
            self.ftp.dir(self.current_path, lambda line: files.append(line))
            
            for line in files:
                if not line.strip():
                    continue
                
                #drwxr-xr-x 1 user group 4096 Dec 10 12:34 name
                parts = line.split()
                if len(parts) < 9:
                    continue
                
                is_dir = line.startswith('d')
                file_type = "Directory" if is_dir else "File"
                
                name = ' '.join(parts[8:])
                size = parts[4] if not is_dir else "-"
                modified = ' '.join(parts[5:8])
                
                item_id = self.tree.insert("", tk.END, values=(file_type, name, size, modified))

                self.tree.set(item_id, "type", file_type)
                
        except ftplib.error_perm as e:
            messagebox.showerror("Error", f"Failed to list directory:\n{str(e)}")
    
    def on_item_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_type = self.tree.item(item, "values")[0]
        item_name = self.tree.item(item, "values")[1]
        
 
        if "Directory" in item_type:
            self.change_directory(item_name)
        else:
            self.retrieve_file()
    
    def change_directory(self, directory: str):
        if not self.connected or not self.ftp:
            return
        
        try:
            self.ftp.cwd(directory)
            self.current_path = self.ftp.pwd()
            self.path_var.set(self.current_path)
            self.refresh_file_list()
        except ftplib.error_perm as e:
            messagebox.showerror("Error", f"Failed to change directory:\n{str(e)}")
    
    def go_up(self):
        if not self.connected or not self.ftp:
            return
        
        if self.current_path == "/":
            return
        
        self.change_directory("..")
    
    def get_selected_filename(self) -> Optional[str]:
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        item_type = self.tree.item(item, "values")[0]
        
        if "Directory" in item_type:
            return simpledialog.askstring("Filename", "Enter filename:")
        
        return self.tree.item(item, "values")[1]
    
    def create_file(self):
        if not self.connected or not self.ftp:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        filename = self.filename_entry.get().strip()
        if not filename:
            filename = simpledialog.askstring("Create File", "Enter filename:")
        
        if not filename:
            return

        try:
            self.ftp.size(f"{self.current_path}/{filename}")
            if not messagebox.askyesno("Warning", f"File '{filename}' already exists. Overwrite?"):
                return
        except:
            pass
        
        self.open_file_editor(filename, is_new=True)
        self.filename_entry.delete(0, tk.END)
    
    def retrieve_file(self):
        if not self.connected or not self.ftp:
            messagebox.showwarning("Warning", "Not connected to server")
            return

        filename = self.filename_entry.get().strip()
        if not filename:
            filename = self.get_selected_filename()
        
        if not filename:
            messagebox.showinfo("Info", "Please select a file or enter filename")
            return
        
        try:
            temp_file = f"_temp_{filename}"
            
            with open(temp_file, 'wb') as f:
                self.ftp.retrbinary(f"RETR {self.current_path}/{filename}", f.write)
            
            with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, content)
            
            os.remove(temp_file)
        except ftplib.error_perm as e:
            if "550" in str(e):
                messagebox.showerror("Error", f"File '{filename}' not found or is a directory")
            else:
                messagebox.showerror("Error", f"Failed to retrieve file:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")
    
    def update_file(self):
        if not self.connected or not self.ftp:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        filename = self.filename_entry.get().strip()
        if not filename:
            filename = self.get_selected_filename()
        
        if not filename:
            messagebox.showinfo("Info", "Please select a file or enter filename")
            return

        try:
            self.ftp.size(f"{self.current_path}/{filename}")
        except:
            if not messagebox.askyesno("Warning", f"File '{filename}' does not exist. Create it?"):
                return
        
        self.open_file_editor(filename, is_new=False)
    
    def delete_file(self):
        if not self.connected or not self.ftp:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        filename = self.filename_entry.get().strip()
        if not filename:
            filename = self.get_selected_filename()
        
        if not filename:
            messagebox.showinfo("Info", "Please select a file or enter filename")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
            return
        
        try:
            self.ftp.delete(f"{self.current_path}/{filename}")
            self.refresh_file_list()
            self.filename_entry.delete(0, tk.END)
        except ftplib.error_perm as e:
            if "550" in str(e):
                messagebox.showerror("Error", f"File '{filename}' not found or is a directory")
            else:
                messagebox.showerror("Error", f"Failed to delete file:\n{str(e)}")
    
    def open_file_editor(self, filename: str, is_new: bool = True):
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Edit File: {filename}")
        editor_window.geometry("600x500")
        
        initial_content = ""
        if not is_new:
            try:
                temp_file = f"_temp_{filename}"
                with open(temp_file, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {self.current_path}/{filename}", f.write)
                
                with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    initial_content = f.read()
                
                os.remove(temp_file)
            except:
                pass
  
        text_area = scrolledtext.ScrolledText(editor_window, wrap=tk.WORD, font=("Courier", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(1.0, initial_content)
     
        def save_content():
            content = text_area.get(1.0, tk.END).rstrip()
            
            try:
                temp_file = f"_temp_{filename}"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                with open(temp_file, 'rb') as f:
                    self.ftp.storbinary(f"STOR {self.current_path}/{filename}", f)
            
                os.remove(temp_file)
                
                self.refresh_file_list()
                editor_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
     
        save_btn = ttk.Button(editor_window, text="Save", command=save_content)
        save_btn.pack(pady=10)
        
        editor_window.transient(self.root)
        editor_window.grab_set()
    
    def create_directory(self):
        if not self.connected or not self.ftp:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        dirname = self.filename_entry.get().strip()
        if not dirname:
            dirname = simpledialog.askstring("Create Directory", "Enter directory name:")

        if not dirname:
            return

        dirname = dirname.strip()
        if not dirname:
            messagebox.showerror("Error", "Directory name cannot be empty")
            return

        try:
            full_path = f"{self.current_path}/{dirname}"
            self.ftp.mkd(full_path)

            self.refresh_file_list()
        except ftplib.error_perm as e:
            if "550" in str(e):
                messagebox.showerror("Error", f"Directory '{dirname}' already exists or invalid name")
            else:
                messagebox.showerror("Error", f"Failed to create directory:\n{str(e)}")

    def get_selected_dirname(self) -> Optional[str]:
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        item_type = self.tree.item(item, "values")[0]
        
        if "Directory" not in item_type:
            return simpledialog.askstring("Dirname", "Enter directory name:")
        
        return self.tree.item(item, "values")[1]
    
    def remove_directory(self):
        if not self.connected or not self.ftp:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        name = self.filename_entry.get().strip()
        if not name:
            name = self.get_selected_dirname()
        
        if not name:
            messagebox.showinfo("Info", "Please select a directory or enter name")
            return
        
        try:
            if not self._is_directory_empty(name):
                messagebox.showinfo("Info", "The directory must be empty!")
                return
        
            if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
                return

            self.ftp.rmd(name)
            self.refresh_file_list()
        except ftplib.error_perm as e:
            messagebox.showerror("Error", f"Failed to delete directory:\n{str(e)}")

    def _is_directory_empty(self, dirname: str) -> bool:
        if not self.connected or not self.ftp:
            return False

        current_dir = self.ftp.pwd()

        full_path = f"{self.current_path}/{dirname}"
        self.ftp.cwd(full_path)

        items = self.ftp.nlst()
        filtered_items = [item for item in items if item not in ('.', '..')]

        self.ftp.cwd(current_dir)
        return len(filtered_items) == 0


    def run(self):
        self.root.mainloop()

def main():
    app = FTPClientGUI()
    app.run()

if __name__ == "__main__":
    main()