#!/user/bin/env python3
import tkinter as tk
from tkinter import ttk

import gerber_canvas as gc
from bom import Bom
from pickplace import PickPlace
import sys
import zf
import dbrequest


class Application(tk.Frame):

    my_bom = Bom()
    # my_canvas = gc.GerberCanvas(Application.can)

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.grid()
        self.bom_file_name = tk.StringVar()
        self.gerber_file_name = tk.StringVar()
        self.pick_n_place_file_name = tk.StringVar()
        self._mfg_part_number = tk.StringVar()
        self._description = tk.StringVar()
        self._part_qty = tk.StringVar()
        self._inv_location = tk.StringVar()
        self._board_location = tk.StringVar()

        self.board_qty = tk.StringVar()
        self.checked = tk.IntVar()

        self.pcb_board = None
        self.create_widgets()

    def create_widgets(self):

        top = self.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=3)

        top.rowconfigure(0, weight=0)
        top.rowconfigure(1, weight=2)

        bom_frame = tk.Frame(self.master)

        bom_frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W, padx=3, pady=3)
        bom_tree = ttk.Treeview(bom_frame, columns=('Component', 'Description', 'Done'), selectmode='browse')
        bom_tree.column('#2', anchor='center')
        bom_tree.column('#3', anchor='center')
        bom_tree.heading('#0', text='Mfg Part#', anchor='center')
        bom_tree.heading('#1', text='Component', anchor='center')
        bom_tree.heading('#2', text='Description', anchor='center')
        bom_tree.heading('#3', text='Done')
        bom_tree.pack(expand=True, fill='both')

        bom_tree.bind('<Key-a>', self.my_bom.inc)
        bom_tree.bind('<Key-r>', self.my_bom.dec)
        bom_tree.bind('<<TreeviewSelect>>', self.item_selected)

        #######################################################################################
        # this start the info frame.
        component_info_frame = tk.LabelFrame(self.master, text='Part/Project Info:', relief=tk.GROOVE, border=3)

        tk.Label(component_info_frame, text='Bom File: ').grid(row=0, column=0, sticky='w')
        tk.Label(component_info_frame, text='Gerber File: ').grid(row=1, column=0, sticky='w')
        tk.Label(component_info_frame, text='Pick and Place File: ').grid(row=2, column=0, sticky='w')
        tk.Label(component_info_frame, text='         ').grid(row=3, column=0, sticky='w')
        tk.Label(component_info_frame, text='MFG Part#: ').grid(row=4, column=0, sticky='w')
        tk.Label(component_info_frame, text='Description: ').grid(row=5, column=0, sticky='w')
        tk.Label(component_info_frame, text='Part Number Qty: ').grid(row=6, column=0, sticky='w')
        tk.Label(component_info_frame, text='Inv Location: ').grid(row=7, column=0, sticky='w')
        tk.Label(component_info_frame, text='Top/Bottom Location').grid(row=8, column=0, sticky='w')

        bom_file = ttk.Label(component_info_frame,
                             textvariable=self.bom_file_name)
        bom_file.grid(row=0, column=1, sticky='w')
        # self.part_qty.set(bomTreeView.selected_part_qty)

        gerber_file = ttk.Label(component_info_frame,
                                textvariable=self.gerber_file_name)
        gerber_file.grid(row=1, column=1, sticky='w')

        pick_n_place_file = ttk.Label(component_info_frame,
                                      textvariable=self.pick_n_place_file_name)
        pick_n_place_file.grid(row=2, column=1, sticky='nw')

        lbl_part_number = ttk.Label(component_info_frame,
                                    textvariable=self._mfg_part_number)
        lbl_part_number.grid(row=4, column=1, sticky='nw')

        lbl_description = ttk.Label(component_info_frame,
                                    textvariable=self._description)
        lbl_description.grid(row=5, column=1, sticky='nw')

        lbl_qty = ttk.Label(component_info_frame,
                            textvariable=self._part_qty)
        lbl_qty.grid(row=6, column=1, sticky='nw')

        lbl_inv_location = ttk.Label(component_info_frame,
                                     textvariable=self._inv_location)
        lbl_inv_location.grid(row=7, column=1, sticky='nw')

        lbl_board_location = ttk.Label(component_info_frame,
                                       textvariable=self._board_location)
        lbl_board_location.grid(row=8, column=1, sticky='nw')

        component_info_frame.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E + tk.W, padx=5, pady=5)
        component_info_frame.grid_propagate(0)

        # End Info Frame Stuff
        ##############################################################################################

        canvas_frame = tk.Frame(self.master)
        canvas_frame.grid(row=1, column=0, columnspan=2, sticky=tk.N + tk.S + tk.E + tk.W, padx=10, pady=1)

        pcb_board = gc.GerberCanvas(canvas_frame)
        Application.my_bom._canvas = pcb_board

        bottom_frame = tk.Frame(self.master, relief='groove')
        btn_load_bom = tk.Button(bottom_frame, text='Import BOM',
                                 command=lambda: self.open_bom_csv(bom_tree))
        btn_load_bom.grid(row=0, column=1, sticky='e', padx='10', pady='5')

        btn_save_bom = tk.Button(bottom_frame, text='Save BOM File', command=lambda: Application.my_bom.save(bom_tree))
        btn_save_bom.grid(row=0, column=2, sticky='e', padx='10', pady='5')

        btn_load_bom = tk.Button(bottom_frame, text='Load BOM File', command=lambda: Application.my_bom.load(bom_tree))
        btn_load_bom.grid(row=0, column=3, sticky='e', padx='10', pady='5')

        ckb_auto_move = tk.Checkbutton(bottom_frame, text='Auto Move', variable=self.checked,
                                       command=lambda: Application.my_bom.auto_advance(Application.my_bom))
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

    def open_bom_csv(self, bom_tree):
        """ import new Bom from csv file
        :param bom_tree
        """
        status, file_name = Application.my_bom.import_csv(bom_tree)
        if status:
            self.bom_file_name.set(file_name)

    def load_pick_place(self):
        status, file_name = PickPlace.load_pick_place()
        self.pick_n_place_file_name.set(file_name)
        PickPlace.pnp_loaded = status

    def load_gerber_file(self, pc_board):
        path, file = zf.load_zip_file()
        self.gerber_file_name.set(file)
        pc_board.load_gerber(path, file)

    # loop through the parts for each board entered
    def process_boards(self, event):
        event.get()
        board_qty = self.board_qty.get
        print(board_qty)

    def item_selected(self, event):
        tree_widget = event.widget
        if Application.my_bom:               # if the bom tree is not empty
            part_number, part_desc, part_qty, part_layer = self.my_bom.check_part(tree_widget)
            self._inv_location.set(dbrequest.find_part_location(part_number))
            self._mfg_part_number.set(part_number)
            self._description.set(part_desc)
            self._part_qty.set(part_qty)
            self._board_location.set(part_layer)


if __name__ == '__main__':

    root = tk.Tk()
    app = Application(root)

    if sys.platform == 'linux':
        app.master.iconbitmap('icon.png')
    else:
        app.master.iconbitmap('pp.ico')

    app.master.title('Place Parts')
    app.mainloop()
