from inventory_image_select_gui import DisplayImage
import pdftotext
import re
from PIL import Image, ImageTk, ImageChops
from tkinter import ttk, filedialog
# from tkinter.messagebox import showinfo
from tkinter import *
import tkinter as tk
import pandas as pd
import numpy as np

# sys.path.append(".")


class Tab:
    def __init__(self, notebook: ttk.Notebook):
        self.filename = None
        self.notebook = notebook

        self.text_widget = tk.Text(self.notebook)
        self.text_widget.bind("<Control-o>", self.open)
        self.text_widget.bind("<Control-s>", self.save)
        self.text_widget.bind("<Control-Shift-S>", self.saveas)
        self.notebook.add(self.text_widget, text="The tab name")

    def open(self, _=None):
        filename = filedialog.askopenfilename()
        if filename != "":
            with open(filename, "r") as file:
                data = file.read()
            self.text_widget.delete("0.0", "end")
            self.text_widget.insert("end", data)
            self.filename = filename
        return "break"

    def save(self, _=None):
        if self.filename is None:
            self.saveas()
        else:
            self._save()
        return "break"

    def saveas(self, _=None):
        filename = filedialog.asksaveasfilename()
        if filename == "":
            return "break"
        self.filename = filename
        self._save()

    def _save(self):
        assert self.filename is not None, "self.filename shouldn't be None"
        data = self.text_widget.get("0.0", "end")
        with open(self.filename, "w") as file:
            file.write(data)


class AppGui():
    def __init__(self, parent):
        self.parent = parent
        self.options = []
        self.df = pd.DataFrame()

        # ***Set up tabFrame***
        self.tabFrame = tk.Frame(self.parent, highlightbackground="#ccd7d9",
                                 highlightcolor="#ccd7d9", width=root.winfo_width(), highlightthickness=1, bg="#eaeeef")

        # Tab menu
        self.tabMenu = ttk.Notebook(self.tabFrame)
        self.tab1 = ttk.Frame(self.tabMenu)
        self.fileSelect = ttk.Button(self.tab1)
        self.tab2 = ttk.Frame(self.tabMenu)
        self.detailView = ttk.Button(self.tab2)
        self.tabMenu.add(self.tab1, text="PDF Functions", sticky="ew")
        self.tabMenu.add(self.tab2, text="Inventory Functions", sticky="ew")

        # ***PDF function display area***
        self.displayList = tk.Listbox(
            self.tabMenu, selectmode="multiple", selectbackground="#72808D", bg="#eaeeef", bd=1)

        # ***PDF function footer***
        self.fileInteractFrame = tk.Frame(self.tabMenu, highlightbackground="#ccd7d9",
                                          highlightcolor="#ccd7d9", width=root.winfo_width()-10, highlightthickness=1, bg="#eaeeef")

        # ***Buttons***
        # Launch filebrowser window to find PDF files
        self.getPdfButton = tk.Button(self.fileInteractFrame, text="Get PDFs", command=self.getPdf)

        # Clear all loaded files
        self.clearButton = tk.Button(self.fileInteractFrame, text="Clear",
                                     command=self.clear, state="disabled")

        # Delete highlighted files from selection
        self.deleteButton = tk.Button(
            self.fileInteractFrame, text="Delete selected", command=self.option_delete, state="disabled")

        # Create a Treeview widget nested within a tab-able notebook
        self.inventoryTabs = ttk.Notebook(self.tabMenu)
        self.tree = ttk.Treeview(self.inventoryTabs)

        # ***Inventory functions footer***
        self.inventoryInteractFrame = tk.Frame(self.tabMenu, highlightbackground="#ccd7d9",
                                               highlightcolor="#ccd7d9", width=root.winfo_width()-10, highlightthickness=1, bg="#eaeeef")

        # ***Buttons***
        # Select inventory source
        self.inventorySelectButton = tk.Button(
            self.inventoryInteractFrame, text="Get Inventory List", command=self.getInventory)

        # View selection in context
        self.inventoryDetailView = tk.Button(
            self.inventoryInteractFrame, text="View Selection In Context", command=self.inventory_context, state="disabled",)

        # Add a Menu
        self.m = Menu(root)
        root.config(menu=self.m)

        # Add Menu Dropdown
        self.file_menu = Menu(self.m, tearoff=False)
        self.m.add_cascade(label="Menu", menu=self.file_menu)
        self.file_menu.add_command(label="Get PDFs", command=self.getPdf)
        self.file_menu.add_command(label="Open Inventory Sheet", command=self.getInventory)

        # Add a Label widget to display the file content
        self.treeViewLabel = Label(self.tabMenu, text='', background="#eaeeef")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        # ***Footer bar***
        self.footer = tk.Frame(self.parent, highlightbackground="#ccd7d9",
                               highlightcolor="#ccd7d9", width=root.winfo_width()-10, height=50, highlightthickness=1, bg="#eaeeef", bd=0)

        # Quit button - exit program
        self.quitButton = tk.Button(self.footer, text='Quit', command=self.parent.destroy)

        # ***Positioning***
        # Tab frame is positioned last in order to avoid a disappearing footer issue
        self.getPdfButton.grid(row=0, column=0, sticky=N+W, padx=5)
        self.clearButton.grid(row=0, column=2, sticky=N+W, padx=5)
        self.deleteButton.grid(row=0, column=1, sticky=N+W, padx=5)
        self.inventorySelectButton.grid(row=0, column=0, sticky=N+W, padx=5)
        self.inventoryDetailView.grid(row=0, column=1, sticky=N+W, padx=5)
        self.footer.pack(side=BOTTOM, expand=True, fill=X)
        self.quitButton.grid(row=0, column=0, sticky=N+E, padx=5, pady=5)
        self.tabFrame.pack(side=TOP, expand=True, fill=BOTH, padx=(5, 5))
        self.tabMenu.pack(side=TOP, expand=True, fill=BOTH)
        self.fileInteractFrame.pack(in_=self.tab1, side=BOTTOM, expand=True, fill=X)
        self.displayList.pack(in_=self.tab1, side=TOP, expand=True, fill=BOTH)
        self.inventoryInteractFrame.pack(in_=self.tab2, side=BOTTOM, expand=True, fill=BOTH)
        self.inventoryTabs.pack(in_=self.tab2, side=BOTTOM, expand=True, fill=BOTH)
        self.tree.pack(side=TOP, expand=True, fill=BOTH)
        self.scrollbar.pack(side=RIGHT, expand=True, fill=Y)

        # Solve resizing issue for display area
        self.tree.bind("<<TreeviewSelect>>", self.inventory_select)
        root.bind("<Configure>", self.displayList.config(
            height=root.winfo_height()))
        root.bind("<Configure>", self.fileInteractFrame.config(
            height=root.winfo_height()))
        root.bind("<Configure>", self.tree.config(height=root.winfo_height()))
        root.bind("<Configure>", self.inventoryInteractFrame.config(
            height=root.winfo_height()))

    # Display items
    def listbox_options(self):
        menu = self.displayList
        menu.delete(0, "end")
        for item in range(len(self.options)):
            menu.insert(END, self.options[item])
            menu.itemconfig(item, bg="#eaeeef" if item % 2 == 0 else "#ccd7d9")
        self.button_status_check_pdf()

    # Load pdf files through dialog box
    def getPdf(self):
        if "" in self.options:
            self.options.pop(self.options.index(""))
        self.FILE_PATH = filedialog.askopenfilenames(title="Select Files", filetypes=(("pdf files", ".*pdf"),
                                                                                      ("All Files", "*.")))  # Get pdfs for conversion
        self.dirs = list(self.FILE_PATH)
        self.options.extend(re.sub(expr, '', i) for i in self.dirs if i not in self.options)
        self.listbox_options()

    # Open the inventory file
    def getInventory(self):
        self.inventorySheet = filedialog.askopenfilename(title="Open Inventory Sheet", filetypes=(("xlxs files", ".*xlsx"),
                                                                                                  ("All Files", "*.")))
        self.df = pd.DataFrame()

        if self.inventorySheet:
            try:
                self.inventorySheet = r"{}".format(self.inventorySheet)
                # self.inventorySheets = pd.ExcelFile(self.inventorySheet).sheet_names
                self.df = pd.read_excel(self.inventorySheet, sheet_name=None)
                print(f"\n{self.inventorySheet}\n")
                self.displayMode = "xlsx"
            except ValueError:
                self.treeViewLabel.config(text="File could not be opened")
                self.displayMode = "alert"
            except FileNotFoundError:
                self.treeViewLabel.config(text="File Not Found")
                self.displayMode = "alert"

        # Clear all the previous data in tree
        self.clear_treeview()

        # Start indexing after no. of sheets in spreadsheet
        self.item = 0
        self.sheetIids = {}

        if len(list(self.df.keys())) == 0:
            print("This will never print")
        elif len(list(self.df.keys())) >= 1:
            self.inventory_display_tabs()

        # Display all parent sheets
        for i in self.df:
            self.tree.insert("", "end", text=i, iid=self.item, open=False)
            self.sheetIids[i] = self.item
            self.item += 1
            # print(f"\n\n Current sheet columns: {list(self.df[i])}\n\n")

            # Add new data in Treeview widget
            for j in self.df[i]:
                self.tree.insert(self.sheetIids[i], "end", text=j, iid=self.item, open=False)
                self.tree.move(self.item, self.sheetIids[i], "end")
                self.child1 = self.item
                self.item += 1
                for k in self.df[i][j]:
                    self.tree.insert(self.child1, "end", text=k, iid=self.item, open=False)
                    self.tree.move(self.item, self.child1, "end")
                    self.item += 1

        if self.displayMode == "xlsx":
            self.tree.pack(side=TOP, expand=True, fill=BOTH)
            root.bind("<Configure>", self.tree.config(height=root.winfo_height()))
        elif self.displayMode == "alert" or self.displayMode == "":
            self.treeViewLabel.pack(side=TOP, pady=20, expand=True, fill=BOTH)
            root.bind("<Configure>", self.treeViewLabel.config(height=root.winfo_height()))

    # Clear the Treeview Widget
    def clear_treeview(self):
        self.tree.delete(*self.tree.get_children())

    # Get selection from Inventory sheet
    def inventory_select(self, event):
        for selected_item in self.tree.selection():
            self.itemSelect = self.tree.item(selected_item)
            self.record = self.itemSelect["text"]
            print(self.itemSelect)
        self.button_status_check_inventory()

    # Show selected item in context of sheet
    def inventory_context(self):
        print(self.record)

    # Clear the PDF display area
    def clear(self, event=None):
        self.options = []
        self.listbox_options()

    # Need to finish this
    def option_select(self, *args):
        print(self.om_variable.get())

    # Delete selected items
    def option_delete(self, *args):
        deleteList = self.displayList.curselection()
        reversedDeleteList = deleteList[::-1]
        if len(reversedDeleteList) > 0:
            for i in reversedDeleteList:
                self.options.pop(i)
                self.displayList.delete(i)
        self.listbox_options()

    # Check PDF section button action status
    def button_status_check_pdf(self):
        if len(self.options) == 0:
            self.clearButton["state"] = "disabled"
            self.deleteButton["state"] = "disabled"
        else:
            self.clearButton["state"] = "normal"
            self.deleteButton["state"] = "normal"

    def inventory_display_tabs(self):
        self.invTabs = {}
        for key in self.df:
            self.invTabs["".join([key, "Tab"])] = Tab(self.inventoryTabs)
        print(self.invTabs)

    # Check Inventory section button action status
    def button_status_check_inventory(self):
        if len(self.record) == 0:
            self.inventoryDetailView["state"] = "disabled"
        else:
            self.inventoryDetailView["state"] = "normal"


# Global variables
expr = r"[\'\[\]]|\bname\b"
root = tk.Tk()
root.title("Principia CompAVTech Functions")
root.geometry('1200x900')
root.update()
gui = AppGui(root)

root.bind('<Return>', gui.clear())
root.mainloop()
