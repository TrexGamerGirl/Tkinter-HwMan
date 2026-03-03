import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "tasks.csv"
CSV_FIELDS = ["id", "subject", "description", "due_date", "status"]

def ensure_csv_exists():

    if CSV_PATH.exists() is True:
        return

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

def is_valid_date(date_text):
    try:
        datetime.date.fromisoformat(date_text)
        return True
    except ValueError:
        return False

def to_date(date_text):
    return datetime.date.fromisoformat(date_text)

def load_tasks():
    ensure_csv_exists()

    tasks = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id", "").isdigit() is False:
                continue

            tasks.append(
                {
                    "id": int(row["id"]),
                    "subject": row.get("subject", ""),
                    "description": row.get("description", ""),
                    "due_date": row.get("due_date", ""),
                    "status": row.get("status", "Pending"),
                }
            )
    return tasks

def save_tasks(tasks):
    ensure_csv_exists()

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for task in tasks:
            writer.writerow(
                {
                    "id": str(task["id"]),
                    "subject": task["subject"],
                    "description": task["description"],
                    "due_date": task["due_date"],
                    "status": task["status"],
                }
            )

def get_next_id(tasks):
    if len(tasks) > 0:
        return int(tasks[-1]["id"]) + 1
    else:
        return 1

def find_task_index(tasks, task_id):
    for i in range(len(tasks)):
        if tasks[i]["id"] == task_id:
            return i
    return None

def apply_filter(tasks, filter_mode):
    if filter_mode == "All":
        return list(tasks)

    if filter_mode == "Pending":
        return [t for t in tasks if t["status"] == "Pending"]

    if filter_mode == "Done":
        return [t for t in tasks if t["status"] == "Done"]

    if filter_mode == "Overdue":
        today = datetime.date.today()
        overdue = []
        for t in tasks:
            if t["status"] == "Done":
                continue
            if is_valid_date(t["due_date"]) is False:
                continue
            if to_date(t["due_date"]) < today:
                overdue.append(t)
        return overdue

    return list(tasks)

def sort_by_due_date(tasks):
    def key_func(t):
        if is_valid_date(t["due_date"]) is False:
            return datetime.date.max
        return to_date(t["due_date"])

    return sorted(tasks, key=key_func)

class TasksScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.id_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.due_date_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pending")
        self.filter_var = tk.StringVar(value="All")

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=2)
        self.rowconfigure(10, weight=1)

        ttk.Label(self, text="Tasks", font=("Segoe UI", 12, "bold")).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=tk.W,
            pady=(0, 10),
        )

        ttk.Label(self, text="ID").grid(row=1, column=0, sticky=tk.W, pady=6)
        ttk.Label(self, text="Subject").grid(row=2, column=0, sticky=tk.W, pady=6)
        ttk.Label(self, text="Description").grid(row=3, column=0, sticky=tk.W, pady=6)
        ttk.Label(self, text="Due date (YYYY-MM-DD)").grid(row=4, column=0, sticky=tk.W, pady=6)
        ttk.Label(self, text="Status").grid(row=5, column=0, sticky=tk.W, pady=6)
        ttk.Label(self, text="View").grid(row=7, column=0, sticky=tk.W, pady=(18, 6))

        self.entry_id = ttk.Entry(self, textvariable=self.id_var, state="readonly")
        self.entry_id.grid(row=1, column=1, sticky=tk.EW, pady=6)

        ttk.Entry(self, textvariable=self.subject_var).grid(row=2, column=1, sticky=tk.EW, pady=6)

        self.entry_desc = ttk.Entry(self, textvariable=self.desc_var)
        self.entry_desc.grid(row=3, column=1, sticky=tk.EW, pady=6)

        ttk.Entry(self, textvariable=self.due_date_var).grid(row=4, column=1, sticky=tk.EW, pady=6)

        self.combo_status = ttk.Combobox(
            self,
            textvariable=self.status_var,
            values=["Pending", "Done"],
            state="readonly",
        )
        self.combo_status.grid(row=5, column=1, sticky=tk.EW, pady=6)

        self.filter_combo = ttk.Combobox(
            self,
            textvariable=self.filter_var,
            values=["All", "Pending", "Done", "Overdue"],
            state="readonly",
        )
        self.filter_combo.grid(row=7, column=1, sticky=tk.EW, pady=(18, 6))

        self.tree = ttk.Treeview(
            self,
            columns=("id", "subject", "due", "status"),
            show="headings",
            height=16,
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("due", text="Due Date")
        self.tree.heading("status", text="Status")
        self.tree.grid(row=0, column=3, rowspan=11, sticky=tk.NSEW, padx=(12, 0))

        ttk.Button(self, text="Add", command=self.add_task).grid(
            row=8,
            column=0,
            sticky=tk.EW,
            pady=(10, 0),
        )
        ttk.Button(self, text="Update", command=self.update_task).grid(
            row=8,
            column=1,
            sticky=tk.EW,
            pady=(10, 0),
        )
        ttk.Button(self, text="Delete", command=self.delete_task).grid(
            row=9,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=6,
        )

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        self.refresh_view()
        self.clear_form()

    def refresh_tree(self, visible_tasks):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in visible_tasks:
            self.tree.insert(
                "",
                tk.END,
                values=(task["id"], task["subject"], task["due_date"], task["status"]),
            )

    def refresh_view(self):
        visible = apply_filter(self.app.tasks, self.filter_var.get())
        visible = sort_by_due_date(visible)
        self.refresh_tree(visible)

    def validate_form_common(self):
        raw_subject = self.subject_var.get().strip()
        raw_desc = self.desc_var.get().strip()
        raw_due = self.due_date_var.get().strip()

        if raw_subject == "":
            messagebox.showerror("Invalid", "Subject is required.")
            return False

        if raw_desc == "":
            messagebox.showerror("Invalid", "Description is required.")
            return False

        if is_valid_date(raw_due) is False:
            messagebox.showerror("Invalid", "Due date must be YYYY-MM-DD.")
            return False

        return True

    def clear_form(self):
        next_id = get_next_id(self.app.tasks)
        self.id_var.set(next_id)
        self.subject_var.set("")
        self.desc_var.set("")
        self.due_date_var.set("")
        self.status_var.set("Pending")

    def add_task(self):
        ok = self.validate_form_common()
        if ok is False:
            return

        task_id = int(self.id_var.get())

        self.app.tasks.append(
            {
                "id": task_id,
                "subject": self.subject_var.get().strip(),
                "description": self.desc_var.get().strip(),
                "due_date": self.due_date_var.get().strip(),
                "status": self.status_var.get().strip(),
            }
        )

        save_tasks(self.app.tasks)
        self.refresh_view()
        self.clear_form()
        self.app.refresh_dashboard()

    def update_task(self):
        selected = self.tree.selection()
        if len(selected) == 0:
            messagebox.showinfo("Select", "Select a task in the table first.")
            return

        ok = self.validate_form_common()
        if ok is False:
            return

        values = self.tree.item(selected[0], "values")
        task_id = int(values[0])

        index = find_task_index(self.app.tasks, task_id)
        if index is None:
            messagebox.showinfo("Not found", "No matching task to update.")
            return

        self.app.tasks[index]["subject"] = self.subject_var.get().strip()
        self.app.tasks[index]["description"] = self.desc_var.get().strip()
        self.app.tasks[index]["due_date"] = self.due_date_var.get().strip()
        self.app.tasks[index]["status"] = self.status_var.get().strip()

        save_tasks(self.app.tasks)
        self.refresh_view()
        self.app.refresh_dashboard()

    def delete_task(self):
        selected = self.tree.selection()
        if len(selected) == 0:
            messagebox.showinfo("Select", "Select a task in the table first.")
            return

        values = self.tree.item(selected[0], "values")
        task_id = int(values[0])

        index = find_task_index(self.app.tasks, task_id)
        if index is None:
            return

        del self.app.tasks[index]

        save_tasks(self.app.tasks)
        self.refresh_view()
        self.clear_form()
        self.app.refresh_dashboard()

    def on_select(self, event=None):
        selected = self.tree.selection()
        if len(selected) == 0:
            return

        values = self.tree.item(selected[0], "values")

        self.id_var.set(values[0])
        self.subject_var.set(values[1])
        self.due_date_var.set(values[2])
        self.status_var.set(values[3])

        self.desc_var.set("")
        for task in self.app.tasks:
            if task["id"] == int(values[0]):
                self.desc_var.set(task["description"])
                return

    def on_filter_change(self, event=None):
        self.refresh_view()

class DashboardScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Dashboard", font=("Segoe UI", 12, "bold")).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 12),
        )

        self.lbl_total = ttk.Label(self, text="")
        self.lbl_total.grid(row=1, column=0, sticky=tk.W, pady=6)

        self.lbl_pending = ttk.Label(self, text="")
        self.lbl_pending.grid(row=2, column=0, sticky=tk.W, pady=6)

        self.lbl_done = ttk.Label(self, text="")
        self.lbl_done.grid(row=3, column=0, sticky=tk.W, pady=6)

        self.lbl_overdue = ttk.Label(self, text="")
        self.lbl_overdue.grid(row=4, column=0, sticky=tk.W, pady=6)

        self.lbl_next_due = ttk.Label(self, text="")
        self.lbl_next_due.grid(row=5, column=0, sticky=tk.W, pady=6)

        self.refresh()

    def refresh(self):
        total = len(self.app.tasks)
        pending = len([t for t in self.app.tasks if t["status"] == "Pending"])
        done = len([t for t in self.app.tasks if t["status"] == "Done"])
        overdue = len(apply_filter(self.app.tasks, "Overdue"))

        next_due_text = "Next due: (none)"
        pending_tasks = []
        for t in self.app.tasks:
            if t["status"] != "Pending":
                continue
            if is_valid_date(t["due_date"]) is False:
                continue
            pending_tasks.append(t)

        pending_tasks = sort_by_due_date(pending_tasks)

        if len(pending_tasks) > 0:
            t = pending_tasks[0]
            next_due_text = f'Next due: {t["due_date"]} ({t["subject"]})'

        self.lbl_total.config(text=f"Total tasks: {total}")
        self.lbl_pending.config(text=f"Pending: {pending}")
        self.lbl_done.config(text=f"Done: {done}")
        self.lbl_overdue.config(text=f"Overdue (pending only): {overdue}")
        self.lbl_next_due.config(text=next_due_text)

class App:
    def __init__(self):
        self.tasks = load_tasks()

        self.root = tk.Tk()
        self.root.title("Homework Tracker")
        self.root.geometry("1150x560")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        outer = ttk.Frame(self.root, padding=12)
        outer.grid(row=0, column=0, sticky=tk.NSEW)

        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        nav = ttk.Frame(outer)
        nav.grid(row=0, column=0, sticky=tk.EW, pady=(0, 10))

        ttk.Button(nav, text="Tasks", command=lambda: self.show_screen("tasks")).grid(
            row=0,
            column=0,
            padx=(0, 8),
        )
        ttk.Button(nav, text="Dashboard", command=lambda: self.show_screen("dashboard")).grid(
            row=0,
            column=1,
            padx=(0, 8),
        )

        content = ttk.Frame(outer)
        content.grid(row=1, column=0, sticky=tk.NSEW)

        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.screens = {}

        self.screens["tasks"] = TasksScreen(content, self)
        self.screens["tasks"].grid(row=0, column=0, sticky=tk.NSEW)

        self.screens["dashboard"] = DashboardScreen(content, self)
        self.screens["dashboard"].grid(row=0, column=0, sticky=tk.NSEW)

        self.show_screen("tasks")

    def show_screen(self, name):
        frame = self.screens.get(name)
        if frame is None:
            return

        frame.tkraise()

        if name == "dashboard":
            self.refresh_dashboard()

    def refresh_dashboard(self):
        dash = self.screens.get("dashboard")
        if dash is None:
            return
        dash.refresh()

    def run(self):
        self.root.mainloop()

def main():
    app = App()
    app.run()

if __name__ == "__main__":  
    main()