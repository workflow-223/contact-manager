import tkinter as tk
from tkinter import messagebox, ttk
from contact_manager import load_contacts, save_contacts, next_id


class ContactManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("700x500")

        top = ttk.Frame(root, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.refresh_list())
        ttk.Entry(top, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text="Add Contact", command=self.add_dialog).pack(side=tk.RIGHT)

        cols = ("id", "name", "phone", "email")
        self.tree = ttk.Treeview(root, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("name", width=200)
        self.tree.column("phone", width=150)
        self.tree.column("email", width=250)

        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 42))

        btn_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)

        self.refresh_list()

    def get_contacts(self):
        query = self.search_var.get().strip().lower()
        if not query:
            return load_contacts()
        return [
            c
            for c in load_contacts()
            if query in c["name"].lower()
            or query in c.get("phone", "").lower()
            or query in c.get("email", "").lower()
        ]

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in self.get_contacts():
            self.tree.insert("", tk.END, values=(c["id"], c["name"], c.get("phone", ""), c.get("email", "")))

    def add_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Contact")
        win.geometry("380x200")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        frame = ttk.Frame(win, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=35)
        name_entry.grid(row=0, column=1, pady=5)
        name_entry.focus()

        ttk.Label(frame, text="Phone:").grid(row=1, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame, width=35)
        phone_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=35)
        email_entry.grid(row=2, column=1, pady=5)

        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Name is required.", parent=win)
                return
            contacts = load_contacts()
            contacts.append({
                "id": next_id(contacts),
                "name": name,
                "phone": phone_entry.get().strip(),
                "email": email_entry.get().strip(),
            })
            save_contacts(contacts)
            self.refresh_list()
            win.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side=tk.LEFT, padx=5)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a contact to delete.")
            return
        item = self.tree.item(sel[0])
        cid = item["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete contact ID {cid}?"):
            contacts = load_contacts()
            contacts = [c for c in contacts if c["id"] != cid]
            save_contacts(contacts)
            self.refresh_list()


def main():
    root = tk.Tk()
    ContactManagerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
