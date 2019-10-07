from tkinter import ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter import messagebox
import csv
import json
from pickplace import PickPlace
from gerber_canvas import GerberCanvas as gc
import os

DEBUG = False


class Part:
    """
    Hold information about each component on the board
    """

    def __init__(self, part_number, description, ref):
        """
        Constructor to setup each new part

        :param part_number: this is the OEM part number for the component
        :param description: this is the description of the component
        :param ref: part number reference (eg.  R1,C1)
        """
        self.ref = []
        self.part_number = part_number
        self.description = description
        self.ref.append(ref)

    @staticmethod
    def part_qty(part_list, selected_part):
        """
        count the number of parts per list.
        :param part_list:
        :param selected_part:
        :return:
        """
        print('selected part is ', selected_part)
        print('part list is', part_list)
        for parts in part_list:
            if parts.part_number == selected_part:
                return len(parts.ref)


class bomTreeView:

    """
    Setup my BOM Tree view
    """

    def __init__(self, frame):
        self.my_bom_file = ''
        self.my_bom_saved_file = ''
        self.advance = 0

        self.my_bom_list = ttk.Treeview(frame, columns=('Component', 'Description', 'Done'), selectmode='extended')
        self.my_bom_list.column('#2', anchor='center')
        self.my_bom_list.column('#3', anchor='center')
        self.my_bom_list.heading('#0', text='Mfg Part#', anchor='center')
        self.my_bom_list.heading('#1', text='Component', anchor='center')
        self.my_bom_list.heading('#2', text='Description', anchor='center')
        self.my_bom_list.heading('#3', text='Done')
        self.my_bom_list.bind('<Key-a>', self.inc)
        self.my_bom_list.bind('<Key-r>', self.dec)
        self.my_bom_list.bind('<<TreeviewSelect>>', self.check_part)
        self.my_bom_list.pack(expand=True, fill='both')
        self.pnp_loaded = 0
        self.board_qty = 1
        self.board_qty_loop = 1
        self.selected_part_number = ''
        self.selected_part_qty = ''
        self.part_qty = ''
        # class variables go below.
        self.parts_list = []  # hold the list of parts

    # @property
    # def my_bom_file(self):
    #     return self.my_bom_file
    #
    # @my_bom_file.setter
    # def my_bom_file(self, file_name):
    #     pass
    #     # self.my_bom_file = file_name

    def import_csv(self, frame, parts_list):
        """
        Load the CSV file into my_bom_list
        :return:
        """
        # If My_bom_list is already loaded clear it first
        if parts_list:
            parts_list.clear()
            for i in parts_list.get_children():
                parts_list.delete(i)

        # my_stuff = data
        try:
            self.my_bom_file = askopenfilename(title='Open BOM File', filetypes=[('CSV files', '*.CSV')],
                                               initialdir=' ')
            filename = os.path.split(self.my_bom_file)
            # print('filename = ', filename[1])
            if self.my_bom_file:
                with open(self.my_bom_file) as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:  # this processes the csv file to populate the list of parts
                        # row[1] = description
                        # row[3] = ref
                        # row[12]= Part#
                        try:
                            if row[12]:
                                new_component = Part(row[12], row[1], row[3])
                                # check to see if part is already in my list of parts
                                is_existing_part = self.check_part_number(new_component)
                                if is_existing_part:
                                    is_existing_part.ref.append(new_component.ref)
                                else:
                                    self.parts_list.append(new_component)
                        except IndexError:
                            messagebox.showwarning('Warning', 'This is not a BOM file.\nPlease try again.')
                            break
                    csvfile.close()
        except IOError:
            Message.showinfo(title='this is a test')
            print('Error msg is: ', IOError.strerror)
        finally:
            if parts_list:
                self.write_bom_list(self.parts_list)
                self.my_bom_list.selection_toggle('I001')
                self.my_bom_list.focus('I001')
                return filename[1]

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

    def check_part_number(self, current_part_number):
        """Check to see if part number exist in the current parts list
        :param: current_part_number to search for.
        :return: the matching part record. else false.
        """
        for part in self.parts_list:
            if current_part_number.part_number == part.part_number:
                return part
        return False

    def write_bom_list(self, parts_list):
        """Show the parts list in the bom tree view"""
        for part in parts_list:
            if len(part.ref) <= 1:
                self.my_bom_list.insert('', 'end', text=part.part_number, values=(part.ref, part.description))
            else:
                for each in part.ref:
                    self.my_bom_list.insert('', 'end', text=part.part_number, values=(each, part.description))

    def number_of_boards(self, qty):
        if qty:
            self.board_qty = int(qty)
        else:
            self.board_qty = 0
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

    # fixme this is not working right.  you need to fix
    def check_part(self, event=None):
        rowid = self.my_bom_list.focus()
        current_part = self.my_bom_list.set(rowid)
        print('Current Part item ', self.my_bom_list.item(rowid))
        # app.mfg_part_number.set(current_part)
        dict_temp = (self.my_bom_list.item(rowid))
        qty = Part.part_qty(self.parts_list, dict_temp['text'])
        print('current qty is ', qty)
        self.part_qty = qty
        self.selected_part_qty = qty
        print(self.my_bom_list.set(rowid))

        if PickPlace.is_file_loaded:
            gc.delete_current_highlight(gc.my_canvas)
            # gc.delete_current_highlight(self.canvas)
            try:
                for pnp in PickPlace.pick_n_place_list:
                    if pnp['ref'] == current_part['Component']:
                        gc.high_lite_part(gc.my_canvas, pnp['x'], pnp['y'], pnp['layer'])
                        # gc.high_lite_part(self.canvas, pnp['x'], pnp['y'], pnp['layer'])
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

