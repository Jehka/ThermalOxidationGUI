import tkinter as tk
from gui import App
from results import print_validation

if __name__ == "__main__":
    print_validation()
    root = tk.Tk()
    app = App(root)
    root.mainloop()