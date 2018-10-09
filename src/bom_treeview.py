from tkinter import ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
import csv
import json
import pickplace as pp
from gerber_canvas import GerberCanvas as gc

DEBUG = False


class bomTreeView:
    """
    Setup my BOM Tree view
    """

    def __init__(self, frame, canvas):
        self.my_bom_file = ''
        self.my_bom_saved_file = ''
        self.advance = 0
        self.canvas = canvas
        self.my_bom_list = ttk.Treeview(frame, columns=('Component', 'Description', 'Done'), selectmode='extended')
        self.my_bom_list.column('#2', anchor='center')
        self.my_bom_list.column('#3', anchor='center')
        self.my_bom_list.heading('#0', text='Mfg Part#', anchor='center')
        self.my_bom_list.heading('#1', text='Component', anchor='center')
        self.my_bom_list.heading('#2', text='Description', anchor='center')
        self.my_bom_list.heading('#3', text='Done')
        self.my_bom_list.tag_configure('DNP', background='red')
        self.my_bom_list.tag_configure('done', background='green')
        self.my_bom_list.tag_bind(self.my_bom_list, '<1>', 'click')
        self.my_bom_list.bind('<Key-a>', self.inc)
        self.my_bom_list.bind('<Key-r>', self.dec)
        self.my_bom_list.bind('<<TreeviewSelect>>', self.check_part)
        self.my_bom_list.pack(fill='both')
        self.pnp_loaded = 0
        self.board_qty = 1
        self.board_qty_loop = 1

    def import_csv(self):
        """
        Load the CSV file into my_bom_list
        :return:
        """
        # my_stuff = data
        try:
            self.my_bom_file = askopenfilename(title='Open BOM File', filetypes=[('CSV files', '*.CSV')],
                                               initialdir=' ')
            # chan, cnx = self.connect_to_database()
            if self.my_bom_file:
                with open(self.my_bom_file) as csvfile:
                    global reader

                    reader = csv.reader(csvfile)
                    for row in reader:  # this processes the csv file to populate the grid
                        print(row)
                        # location = self.db_part_lookup(chan, cnx, row[12])
                        self.my_bom_list.insert('', 'end', text=row[12], values=(row[3], row[1]))
                    csvfile.close()
                self.my_bom_list.focus('I001')
                self.my_bom_list.selection_toggle('I001')
        except IOError:
            print('Error msg is: ', IOError.strerror)
        finally:
            # cursor.close()
            # cnx.close()
            pass

    def save(self):
        """
        Saves a BOM file to disk.
        :return:
        """
        self.my_bom_saved_file = asksaveasfile(title='Save BOM File', filetypes=[('BOM files', '*.bom')],
                                               initialdir='')
        if self.my_bom_saved_file:

            save_data = []

            self.my_bom_list.focus('I001')
            start_loop = True
            while start_loop:
                row_id = self.my_bom_list.focus()
                row_data = self.my_bom_list.item(row_id)
                if DEBUG:
                    print(json.dumps(row_data))
                save_data.append(row_data)
                next_id = self.my_bom_list.next(row_id)
                self.my_bom_list.focus(next_id)
                if not next_id:
                    start_loop = False
            #  save file here
            with open(self.my_bom_saved_file.name + '.bom', 'w') as fp:
                json.dump(save_data, fp, indent=1)
            fp.close()

    def load(self):
        """
        load a BOM file from disk
        :return:
        """

        if DEBUG:
            print(self.my_bom_file)
        try:
            self.my_bom_file = askopenfilename(title='Open BOM File', filetypes=[('BOM files', '*.bom')],
                                               initialdir=' ')
            if self.my_bom_file:
                with open(self.my_bom_file) as bomfile:
                    bom_list = json.load(bomfile)
                    bomfile.close()
                    for i in bom_list:
                        self.my_bom_list.insert('', 'end', text=i['text'], values=i['values'])

        except IOError:
            print('Error msg is: ', IOError.strerror)

    def number_of_boards(self, qty):
        self.board_qty = int(qty)
        if DEBUG:
            print('board qty is ' + str(self.board_qty))

    def inc(self, event):
        """
        Try to inc the number of parts placed
        :return:
        """
        print(event.char)
        rowid = self.my_bom_list.focus()
        dictTemp = self.my_bom_list.set(rowid)
        self.__check_done_field(dictTemp, rowid)

        for keys, values in dictTemp.items():
            if keys == 'Done':
                values = int(values) + 1
                self.my_bom_list.set(rowid, 'Done', str(values))

        self.__auto_advance()
        if self.pnp_loaded:
            self.check_part()

    def dec(self, event):
        """
        Try to dec the number of parts placed
        :return:
        """
        rowid = self.my_bom_list.focus()
        dict_temp = self.my_bom_list.set(rowid)

        if 'Done' in dict_temp.keys():
            for keys, values in dict_temp.items():
                if keys == 'Done':
                    if int(values) >= 1:
                        values = int(values) - 1
                        self.my_bom_list.set(rowid, 'Done', str(values))
            if self.pnp_loaded:
                self.check_part()

    def check_part(self, event):
        gc.delete_current_highlight(self.canvas)
        rowid = self.my_bom_list.focus()
        dictTemp = self.my_bom_list.set(rowid)
        if DEBUG:
            print(rowid)
            print(dictTemp)
        if dictTemp['Component']:
            # print(dictTemp['Component'])
            x = pp.get_x(dictTemp['Component'])
            y = pp.get_y(dictTemp['Component'])
            layer = pp.get_layer(dictTemp['Component'])
            if self.pnp_loaded:
                try:
                    self.__current_selelction = gc.high_lite_part(self.canvas, x, y, layer)
                except TypeError:
                    pass

    def auto_advance(self, mode):
        """
        Set the Auto Advanced check box
        :param mode:
        :return:
        """
        self.advance = mode

    def __check_done_field(self, dict_temp, row_id):
        """
        Check to see if he field 'Done' is available
        :param dict_temp:
        :param row_id:
        :return:
        """
        if 'Done' in dict_temp.keys():
            return
        elif 'Done' not in dict_temp.keys():
            # You have to set to one here to add the field
            self.my_bom_list.set(row_id, 'Done', '1')

    def __auto_advance(self, loop_complete=False):
        """
        If the Auto Advanced check box is set move the selection to the next part.
        :return:
        """
        if self.advance:
            current_item = self.my_bom_list.focus(item=None)
            next_item = self.my_bom_list.next(self.my_bom_list.focus(item=None))
            # self.my_bom_list.selection_toggle(current_item)
            self.my_bom_list.focus(next_item)
            self.my_bom_list.selection_set(next_item)
            self.my_bom_list.see(next_item)     # if item is not visible show it
            if DEBUG:
                print(next_item)
            check_value = self.my_bom_list.set(next_item)
            for fields, content in check_value.items():
                if DEBUG:
                    print(fields, ', ', content)
                if fields == 'Component':
                    my_string = str(content)
                    # if i find DNP skip it
                    if 'DNP' in my_string:
                        self.__auto_advance()
                    # if i find a blank line skip it
                    if not my_string:
                        if self.board_qty_loop == self.board_qty:
                            self.__auto_advance()
                            self.board_qty_loop = 1
                            loop_complete = True
                        if self.board_qty > 1 and (self.board_qty_loop <= self.board_qty) and not loop_complete:
                            self.board_qty_loop += 1
                            self.my_bom_list.selection_toggle(next_item)
                            self.__loop_back()
                            loop_complete = False

            if self.pnp_loaded:
                self.check_part(event=None)

    def __loop_back(self):
        current_item = self.my_bom_list.focus(item=None)
        prev_item = self.my_bom_list.prev(item=current_item)
        self.my_bom_list.selection_set(current_item)
        self.my_bom_list.focus(prev_item)
        check_value = self.my_bom_list.set(prev_item)
        for fields, content in check_value.items():
            if fields == 'Component':
                component = str(content)
                if component:
                    self.__loop_back()
                if not component:
                    if self.board_qty_loop >= self.board_qty:
                        self.__auto_advance(loop_complete=True)

