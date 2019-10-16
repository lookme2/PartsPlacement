#!/user/bin/env python3
import tkinter as tk
from tkinter import ttk

import gerber_canvas as gc
from bom_treeview import bomTreeView
from pickplace import PickPlace
import sys
import zf


class Application(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.bom_file_name = tk.StringVar()
        self.gerber_file_name = tk.StringVar()
        self.pick_n_place_file_name = tk.StringVar()
        self.mfg_part_number = tk.StringVar()
        self.description = tk.StringVar()
        self.part_qty = tk.StringVar()
        self.board_qty = tk.StringVar()
        self.checked = tk.IntVar()
        self.create_widgets()
        self.pcb_board = None

    def create_widgets(self):

        top = self.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=3)

        top.rowconfigure(0, weight=0)
        top.rowconfigure(1, weight=2)

        bom_frame = tk.Frame(self.master)
        bom_frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W, padx=3, pady=3)
        current_bom = bomTreeView(bom_frame)

        component_info_frame = tk.LabelFrame(self.master, text='Part/Project Info:', relief=tk.GROOVE, border=3)

        tk.Label(component_info_frame, text='Bom File: ').grid(row=0, column=0, sticky='w')
        tk.Label(component_info_frame, text='Gerber File: ').grid(row=1, column=0, sticky='w')
        tk.Label(component_info_frame, text='Pick and Place File: ').grid(row=2, column=0, sticky='w')
        tk.Label(component_info_frame, text='         ').grid(row=3, column=0, sticky='w')
        tk.Label(component_info_frame, text='MFG Part#: ').grid(row=4, column=0, sticky='w')
        tk.Label(component_info_frame, text='Description: ').grid(row=5, column=0, sticky='w')
        tk.Label(component_info_frame, text='Part Number Qty: ').grid(row=6, column=0, sticky='w')

        bom_file = ttk.Label(component_info_frame, textvariable=self.bom_file_name)
        bom_file.grid(row=0, column=1, sticky='w')
        self.part_qty.set(bomTreeView.selected_part_qty)

        gerber_file = ttk.Label(component_info_frame, textvariable=self.gerber_file_name)
        gerber_file.grid(row=1, column=1, sticky='w')

        pick_n_place_file = ttk.Label(component_info_frame, textvariable=self.pick_n_place_file_name)
        pick_n_place_file.grid(row=2, column=1, sticky='nw')

        lbl_part_number = ttk.Label(component_info_frame, textvariable=self.mfg_part_number)
        lbl_part_number.grid(row=4, column=1, sticky='nw')

        lbl_description = ttk.Label(component_info_frame, textvariable=self.description)
        lbl_description.grid(row=5, column=1, sticky='nw')

        lbl_qty = ttk.Label(component_info_frame, textvariable=self.part_qty)
        lbl_qty.grid(row=4, column=1, sticky='nw')
        self.part_qty.set(bomTreeView.selected_part_qty)

        component_info_frame.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E + tk.W, padx=5, pady=5)

        # End Info Frame Stuff

        canvas_frame = tk.Frame(self.master)
        canvas_frame.grid(row=1, column=0, columnspan=2, sticky=tk.N + tk.S + tk.E + tk.W, padx=10, pady=1)

        pcb_board = gc.GerberCanvas(canvas_frame)
        bomTreeView.my_canvas = pcb_board

        bottom_frame = tk.Frame(self.master, relief='groove')
        btn_load_bom = tk.Button(bottom_frame, text='Import BOM',
                                 command=lambda: self.open_bom_csv(current_bom, current_bom.parts_list))
        btn_load_bom.grid(row=0, column=1, sticky='e', padx='10', pady='5')

        btn_save_bom = tk.Button(bottom_frame, text='Save BOM File', command=lambda: current_bom.save())
        btn_save_bom.grid(row=0, column=2, sticky='e', padx='10', pady='5')

        btn_load_bom = tk.Button(bottom_frame, text='Load BOM File', command=lambda: current_bom.load())
        btn_load_bom.grid(row=0, column=3, sticky='e', padx='10', pady='5')

        ckb_auto_move = tk.Checkbutton(bottom_frame, text='Auto Move', variable=self.checked,
                                       command=lambda: current_bom.auto_advance(current_bom))
        ckb_auto_move.grid(row=0, column=4, padx='10', pady='5')

        tk.Label(bottom_frame, text='Board Qty:').grid(row=0, column=5, padx='10', pady='5')

        usr_board_num = tk.Entry(bottom_frame, textvariable=self.board_qty)
        usr_board_num.grid(row=0, column=6, padx='10', pady='5')
        usr_board_num.bind('<Return>', self.process_boards(self.board_qty))

        ttk.Separator(bottom_frame, orient=tk.VERTICAL).grid(row=0, column=7, sticky='ns')

        btn_load_bom = tk.Button(bottom_frame, text='Load Gerber File',
                                 command=lambda: self.load_gerber_file(pcb_board))
        btn_load_bom.grid(row=0, column=8, sticky='e', padx='10', pady='5')

        btn_load_pp = tk.Button(bottom_frame, text='Load Pick Place File',
                                command=lambda: self.load_pick_place())
        btn_load_pp.grid(row=0, column=9, sticky='e', padx='10', pady='5')
        bottom_frame.grid(row=2, column=0, columnspan=2)

    def open_bom_csv(self, bom, parts_list):
        """ import new bom from csv file
        :param  bom
        :param  parts_list

        """
        returned_name = bom.import_csv(bom, parts_list)
        self.bom_file_name.set(returned_name)

    @property
    def part_number(self):
        return self.mfg_part_number.get

    @part_number.setter
    def part_number(self, value):
        self.mfg_part_number.set(value)

    def set_description(self, string):
        self.description.set(string)

    def set_qty(self, string):
        self.part_qty.set(string)

    def load_pick_place(self):
        status, return_name = PickPlace.load_pick_place()
        self.pick_n_place_file_name.set(return_name)
        PickPlace.pnp_loaded = status

    def load_gerber_file(self, pc_board):
        path, file = zf.load_zip_file()
        self.gerber_file_name.set(file)
        pc_board.load_gerber(path, file)

    # loop through the parts for each board entered
    def process_boards(self, event):
        # print('I left the field ' + board_qty.get())
        board_qty = self.board_qty.get()
        # bt.bomTreeView.number_of_boards(my_bom, board_qty)


if __name__ == '__main__':

    app = Application()
    if sys.platform == 'linux':
        app.master.iconbitmap('icon.png')
    else:
        app.master.iconbitmap('PP.ico')
    app.master.title('Place Parts')
    app.mainloop()
