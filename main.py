import tkinter as tk

import gradebook

if __name__ == "__main__":
    root = tk.Tk()
    gradebook.MainWindow(root).login_main()
    root.mainloop()
