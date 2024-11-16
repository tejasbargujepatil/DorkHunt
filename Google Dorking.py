import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from tkinter import messagebox
import re


class GoogleDorkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Dorking Tool")
        self.root.geometry("800x600")

        # Available file extensions
        self.extensions = [
            'mp4', 'pdf', 'csv', 'docx', 'xlsx', 'txt', 'jpg', 'png', 'html', 'xml'
        ]
        self.selected_extensions = {}

        # Search history
        self.search_history = []

        # Predefined dorks
        self.predefined_dorks = {
            "Admin Login": "inurl:admin login",
            "Exposed Passwords": "filetype:txt password",
            "SQL Error Pages": "intext:'sql syntax error'",
            "Sensitive Data in PDFs": "filetype:pdf confidential",
            "Open Index Directories": "intitle:index.of",
        }

        # Dark mode toggle
        self.dark_mode = False

        # Define color schemes
        self.color_scheme = {
            "light": {"bg": "white", "fg": "black"},
            "dark": {"bg": "black", "fg": "white"}
        }

        # Create GUI components
        self.create_menu()
        self.create_notebook()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        # File menu
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Save Queries", command=self.save_queries)
        file_menu.add_command(label="Import Extensions", command=self.import_extensions)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="Contact", command=self.show_contact)
        menu.add_cascade(label="Help", menu=help_menu)

        # View menu
        view_menu = tk.Menu(menu, tearoff=0)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menu.add_cascade(label="View", menu=view_menu)

    def create_notebook(self):
        notebook = ttk.Notebook(self.root)
        self.search_tab = ttk.Frame(notebook)
        self.history_tab = ttk.Frame(notebook)

        notebook.add(self.search_tab, text="Search")
        notebook.add(self.history_tab, text="History")

        notebook.pack(expand=True, fill="both")

        # Create widgets for the search tab
        self.create_search_tab()

        # Create widgets for the history tab
        self.create_history_tab()

    def create_search_tab(self):
        # Search bar
        tk.Label(self.search_tab, text="Search Term:", font=("Arial", 12)).pack(pady=5)
        self.search_entry = tk.Entry(self.search_tab, width=50, font=("Arial", 12))
        self.search_entry.pack(pady=5)

        # Predefined dorks
        tk.Label(self.search_tab, text="Predefined Dorks:", font=("Arial", 12)).pack(pady=5)
        dork_options = list(self.predefined_dorks.keys())
        self.dork_var = tk.StringVar(value=dork_options[0])
        dork_dropdown = ttk.OptionMenu(self.search_tab, self.dork_var, dork_options[0], *dork_options, command=self.apply_predefined_dork)
        dork_dropdown.pack(pady=5)

        # Checkboxes for file extensions
        tk.Label(self.search_tab, text="Select File Extensions:", font=("Arial", 12)).pack(pady=5)
        self.checkbox_frame = tk.Frame(self.search_tab)
        self.checkbox_frame.pack()

        self.update_checkboxes()

        # Additional filters
        tk.Label(self.search_tab, text="Additional Filters:", font=("Arial", 12)).pack(pady=5)
        filter_frame = tk.Frame(self.search_tab)
        filter_frame.pack()

        tk.Label(filter_frame, text="Site:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.site_entry = tk.Entry(filter_frame, width=20, font=("Arial", 10))
        self.site_entry.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Exclude Keywords:", font=("Arial", 10)).grid(row=1, column=0, padx=5)
        self.exclude_entry = tk.Entry(filter_frame, width=20, font=("Arial", 10))
        self.exclude_entry.grid(row=1, column=1, padx=5)

        # Search button
        search_button = tk.Button(self.search_tab, text="Generate Dork Queries", command=self.generate_queries, font=("Arial", 12))
        search_button.pack(pady=10)

        # Output box
        self.output_text = tk.Text(self.search_tab, height=10, wrap="word", font=("Arial", 10))
        self.output_text.pack(pady=10, padx=10, fill="both", expand=True)

    def create_history_tab(self):
        tk.Label(self.history_tab, text="Search History:", font=("Arial", 12)).pack(pady=5)
        self.history_listbox = tk.Listbox(self.history_tab, height=15, font=("Arial", 10))
        self.history_listbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.history_listbox.bind("<Double-1>", self.load_from_history)
        self.history_listbox.bind("<Return>", self.load_from_history)

        # Clear history button
        clear_button = tk.Button(self.history_tab, text="Clear History", command=self.clear_history, font=("Arial", 10))
        clear_button.pack(pady=5)

    def update_checkboxes(self):
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        for ext in self.extensions:
            var = tk.BooleanVar(value=False)
            self.selected_extensions[ext] = var
            cb = tk.Checkbutton(self.checkbox_frame, text=ext, variable=var, font=("Arial", 10))
            cb.pack(side=tk.LEFT, padx=5)

    def apply_predefined_dork(self, dork_name=None):
        if not dork_name:
            dork_name = self.dork_var.get()
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, self.predefined_dorks[dork_name])

    def sanitize_input(self, text):
        return re.sub(r'[^\w\-_.]', '', text)

    def validate_search_term(self, term):
        if not term:
            messagebox.showerror("Error", "Search term cannot be empty!")
            return False
        if not re.match(r"^[a-zA-Z0-9\s\-_.]+$", term):
            messagebox.showerror("Error", "Search term contains invalid characters!")
            return False
        return True

    def generate_queries(self):
        search_term = self.search_entry.get().strip()
        if not self.validate_search_term(search_term):
            return

        # Collect selected extensions
        selected_exts = [ext for ext, var in self.selected_extensions.items() if var.get()]
        if not selected_exts:
            messagebox.showerror("Error", "Please select at least one file extension!")
            return

        # Additional filters
        site_filter = self.sanitize_input(self.site_entry.get().strip())
        exclude_filter = self.sanitize_input(self.exclude_entry.get().strip())

        base_url = "https://www.google.com/search?q="
        queries = []
        for ext in selected_exts:
            query = f'{search_term} filetype:{ext}'
            if site_filter:
                query += f' site:{site_filter}'
            if exclude_filter:
                query += f' -{exclude_filter}'
            queries.append(base_url + query.replace(' ', '+'))

        # Display queries in the output box
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(queries))

        # Add to history
        if search_term not in self.search_history:
            self.search_history.append(search_term)
            self.history_listbox.insert(tk.END, search_term)

        # Prompt to open in browser
        if messagebox.askyesno("Open in Browser", "Do you want to open these queries in your default browser?"):
            for query in queries:
                webbrowser.open(query)

    def save_queries(self):
        queries = self.output_text.get("1.0", tk.END).strip()
        if not queries:
            messagebox.showerror("Error", "No queries to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(queries)
            messagebox.showinfo("Success", f"Queries saved to {file_path}")

    def import_extensions(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                extensions = file.read().splitlines()
                valid_extensions = [ext.strip() for ext in extensions if ext.strip()]
                self.extensions.extend(ext for ext in valid_extensions if ext not in self.extensions)
                self.update_checkboxes()
            messagebox.showinfo("Success", "Extensions imported successfully!")

    def load_from_history(self, event):
        try:
            selected_term = self.history_listbox.get(self.history_listbox.curselection())
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, selected_term)
        except tk.TclError:
            pass

    def clear_history(self):
        self.search_history.clear()
        self.history_listbox.delete(0, tk.END)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        current_scheme = self.color_scheme["dark"] if self.dark_mode else self.color_scheme["light"]
        self.apply_dark_mode(self.root, current_scheme)

    def apply_dark_mode(self, widget, scheme):
        try:
            widget.config(bg=scheme["bg"], fg=scheme["fg"])
            if isinstance(widget, (tk.Text, tk.Listbox)):
                widget.config(insertbackground=scheme["fg"])  # Adjust cursor color
        except tk.TclError:
            pass

        for child in widget.winfo_children():
            self.apply_dark_mode(child, scheme)

    def show_help(self):
        messagebox.showinfo(
        "Help",
        "🔍 **Google Dorking Tool Help**\n\n"
        "This tool helps you generate Google dork queries to find specific content on the web.\n\n"
        "Features:\n"
        "• Quickly create search queries for a variety of content types.\n"
        "• Refine searches to pinpoint specific data.\n"
        "• Easy to use and understand.\n\n"
        "For further assistance, feel free to reach out to support!"
    )


    def show_contact(self):
        # Display the messagebox with contact information
        messagebox.showinfo(
            "Contact",
            "For inquiries, please email us at tejasbarguje9@gmail.com.\nFollow us on Instagram: @Tejas_Barguje_Patil"
        )
        # Open the email and Instagram links when user clicks on the button
        self.open_links()

    def open_links(self):
        # Open the email link (optional)
        webbrowser.open("mailto:hackersdaddy826@gmail.com")
        # Open Instagram link (optional)
        webbrowser.open("https://www.instagram.com/tejas_barguje_patil")


if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleDorkGUI(root)
    root.mainloop()
