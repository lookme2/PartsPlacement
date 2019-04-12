#!/user/bin/env python

import tkinter as tk
from tkinter import ttk
import gerber_canvas as gc
import bom_treeview as bt
from pickplace import PickPlace
import zf as zip
import sys


def load_pick_place(canvas):
    status = PickPlace.load_pick_place(canvas)
    my_bom.pnp_loaded = status
    # fi.set_pick_n_place_file_name(frame, pp.pick_n_place_filename)


def bom_import_csv(frame):
    my_bom.import_csv()
    # fi.set_bom_file_name(frame, my_bom.my_bom_file)


def load_gerber_file(frame, canvas):
    file_path_name = zip.load_zip_file()
    gc.GerberCanvas.load_gerber(canvas, file_path_name)
    # fi.set_gerber_file_name(frame, my_canvas.gerber_file_name)


# loop through the parts for each board entered
def process_boards(event):
    # print('I left the field ' + board_qty.get())
    qty = board_qty.get()
    my_bom.number_of_boards(qty)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Place Parts')
    if sys.platform == 'linux':
        root.iconbitmap('icon.png')
    else:
        root.iconbitmap('pp.ico')

    bom_frame = tk.Frame(root)
    bom_frame.configure(height='50')
    bom_frame.pack(fill='both', anchor='n', padx=10, pady=10)

    component_info_frame = tk.Frame(root)
    component_info_frame.pack(fill='both', anchor='n', padx=5, pady=5)

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(expand=True, fill='both', anchor='center', padx=10, pady=1)

    bottom_frame = tk.Frame(root, relief='groove')
    bottom_frame.pack()

    my_canvas = gc.GerberCanvas(canvas_frame)

    my_bom = bt.bomTreeView(bom_frame, my_canvas)

    # this is the bottom frame with buttons

    btn_load_bom = tk.Button(bottom_frame, text='Import BOM', command=lambda: bom_import_csv(my_bom))
    btn_load_bom.grid(row=0, column=1, sticky='e', padx='10', pady='5')

    btn_save_bom = tk.Button(bottom_frame, text='Save BOM File', command=lambda: bt.self.save(my_bom))
    btn_save_bom.grid(row=0, column=2, sticky='e', padx='10', pady='5')

    btn_load_bom = tk.Button(bottom_frame, text='Load BOM File', command=lambda: bt.self.load(my_bom))
    btn_load_bom.grid(row=0, column=3, sticky='e', padx='10', pady='5')

    checked = tk.IntVar()
    ckb_auto_move = tk.Checkbutton(bottom_frame, text='Auto Move', variable=checked,
                                   command=lambda: bt.self.auto_advance(my_bom, checked.get()))
    ckb_auto_move.grid(row=0, column=4, padx='10', pady='5')

    tk.Label(bottom_frame, text='Board Qty:').grid(row=0, column=5, padx='10', pady='5')

    board_qty = tk.StringVar(value=my_bom.board_qty)
    usr_board_num = tk.Entry(bottom_frame, textvariable=board_qty)
    usr_board_num.grid(row=0, column=6, padx='10', pady='5')
    usr_board_num.bind('<Return>', process_boards)

    ttk.Separator(bottom_frame, orient=tk.HORIZONTAL).grid(row=0, column=7, sticky='ns')

    btn_load_bom = tk.Button(bottom_frame, text='Load Gerber File',
                             command=lambda: load_gerber_file(bom_frame, my_canvas))
    btn_load_bom.grid(row=0, column=8, sticky='e', padx='10', pady='5')

    btn_load_pp = tk.Button(bottom_frame, text='Load Pick Place File',
                            command=lambda: load_pick_place(my_canvas))
    btn_load_pp.grid(row=0, column=9, sticky='e', padx='10', pady='5')

    root.mainloop()
