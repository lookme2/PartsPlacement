import tkinter as tk


def set_bom_file_name(frame, bom_file_name):
    tk.Label(frame, text='BOM File: ').grid()
    bom_file = tk.Label(frame, text=bom_file_name)
    bom_file.grid(row=1, column=2, sticky='nw')


def set_gerber_file_name(frame, gerber_file_name):
    tk.Label(frame, text='Gerber File: ').grid(row=2, column=1)
    bom_file = tk.Label(frame, text=gerber_file_name)
    bom_file.grid(row=2, column=2, sticky='nw')


def set_pick_n_place_file_name(frame, pick_n_place_file_name):
    tk.Label(frame, text='Pic N Place: ').grid(row=3, column=1)
    bom_file = tk.Label(frame, text=pick_n_place_file_name)
    bom_file.grid(row=3, column=2, sticky='nw')


