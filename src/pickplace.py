import csv
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os


class PickPlace:

    scaled = None
    is_file_loaded = False
    pick_n_place_list = []
    pick_n_place_filename = ''
    pcb = object

    @staticmethod
    def load_pick_place():
        try:
            my_pnp_file = askopenfilename(title='Open Pick and Place File', filetypes=[('CSV files', '*.CSV'),
                                                                                       ('csv Files', '*.csv')],
                                          initialdir='')
            path = os.path.split(my_pnp_file)
            if my_pnp_file:
                with open(my_pnp_file) as csvfile:
                    dialect = csv.Sniffer().sniff(csvfile.read(1024))
                    csvfile.seek(0)
                    reader = csv.reader(csvfile, dialect)
                    for row in reader:
                        # print(row)
                        if len(row) > 6:
                            if row[0] != 'Designator':
                                new_part = {'ref': row[0], 'x': row[4], 'y': row[5], 'layer': row[2]}
                                PickPlace.pick_n_place_list.append(new_part)
                    csvfile.close()
                    PickPlace.is_file_loaded = True
                    # check for canvas resizing before loading pick and place file
                    if PickPlace.scaled:
                        messagebox.showwarning('Scaled Image', 'The Gerber image has been scaled.  Please Reload image')
                    return 1, path[1]
        except IOError:
            messagebox.showerror('File Error', 'Loading Pick and Place file did not work!!!')
            return 0, None

    @staticmethod
    def get_x(ref):
        for each in PickPlace.pick_n_place_list:
            if each['ref'] == ref:
                # print('x = ', each['x'])
                return each['x']

    @staticmethod
    def get_y(ref):
        for each in PickPlace.pick_n_place_list:
            if each['ref'] == ref:
                # print('y = ', each['y'])
                return each['y']

    @staticmethod
    def get_layer(ref):
        for each in PickPlace.pick_n_place_list:
            if each['ref'] == ref:
                # print('layer = ', each['layer'])
                return each['layer']

    @staticmethod
    def adjust_pic_n_place(value):
        for each in PickPlace.pick_n_place_list:
            try:
                each['x'] = str(float(each['x']) * value)
                each['y'] = str(float(each['y']) * value)
            except ValueError:
                messagebox.showerror('ValueError', ValueError)



