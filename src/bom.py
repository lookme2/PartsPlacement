# from tkinter import ttk as ttk
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
    def get_part_qty(part_list, selected_part):
        """
        count the number of parts per list.
        :param part_list:
        :param selected_part:
        :return: how many parts
        """
        print('selected part is ', selected_part)
        print('part list is', part_list)
        for parts in part_list:
            if parts.get_part_number == selected_part:
                return len(parts.ref)

    @staticmethod
    def get_part_description(part_list, selected_part):
        """
        get the selected part number description.
        :param part_list:
        :param selected_part:
        :return: part description
        """
        for parts in part_list:
            if parts.get_part_number == selected_part:
                return parts.description

    @staticmethod
    def get_part_number(part_list, selected_part):
        """
        get the selected part number
        :param part_list:
        :param selected_part:
        :return: OEM part number
        """
        for parts in part_list:
            if parts.get_part_number == selected_part:
                return parts.part_number


class Bom:

    """
    Setup my bill of material
    """

    def __init__(self):
        # self.bom_file_name = ''
        self.bom_saved_file = ''
        self.advance = 0
        self.pnp_loaded = 0
        self.board_qty = 1
        self.board_qty_loop = 1
        self.selected_part_number = ''
        self.selected_part_qty = ''
        self.__bom_file_name = None

        self.bom_list = []  # hold the list of parts
        self._canvas = None
        self._tree_view_list = None

    # @property
    # def my_bom_tree_list(self):
    #     return self._tree_view_list
    #
    # @my_bom_tree_list.setter
    # def my_bom_tree_list(self, which_list):
    #     self._tree_view_list = which_list
    #
    # @property
    # def my_canvas(self):
    #     return self._canvas
    #
    # @my_canvas.setter
    # def my_canvas(self, canvas):
    #     self._canvas = canvas
    #
    # @property
    # def bom_file_name(self):
    #     return self.__bom_file_name
    #
    # @bom_file_name.setter
    # def bom_file_name(self, name):
    #     self.__bom_file_name = name

    def import_csv(self, my_bom_list):
        """
        Load the CSV file into my_bom_list
        :return: status and file name
        """
        # If parts list is already loaded clear it first
        if self.bom_list:
            self.bom_list.clear()
            for i in self.bom_list.get_children():
                self.bom_list.delete(i)

        # my_stuff = data
        try:
            my_bom_file = askopenfilename(title='Open BOM File', filetypes=[('CSV files', '*.CSV')],
                                          initialdir=' ')
            filename = os.path.split(my_bom_file)
            print('filename = ', filename[1])
            self.bom_file_name = filename[1]
            if my_bom_file:
                with open(my_bom_file) as csv_file:
                    reader = csv.reader(csv_file)
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
                                    self.bom_list.append(new_component)
                        except IndexError:
                            messagebox.showwarning('Warning', 'This is not a BOM file.\nPlease try again.')
                            break
                    csv_file.close()
        except IOError:
            messagebox.showinfo(title='this is a test')
            print('Error msg is: ', IOError.strerror)
            return False, self.bom_file_name
        finally:
            if self.bom_list:
                self.write_bom_list(my_bom_list)
                my_bom_list.selection_toggle('I001')
                my_bom_list.focus('I001')
                return True, self.bom_file_name

    def save(self):
        """
        Saves a BOM file to disk.
        :return:
        """
        self.bom_saved_file = asksaveasfile(title='Save BOM File', filetypes=[('BOM files', '*.Bom')],
                                            initialdir='')
        if self.bom_saved_file:

            save_data = []

            self._tree_view_list.focus('I001')
            start_loop = True
            while start_loop:
                row_id = self._tree_view_list.focus()
                row_data = self._tree_view_list.item(row_id)
                if DEBUG:
                    print(json.dumps(row_data))
                save_data.append(row_data)
                next_id = self._tree_view_list.next(row_id)
                self._tree_view_list.focus(next_id)
                if not next_id:
                    start_loop = False
            #  save file here
            with open(self.bom_saved_file.name + '.Bom', 'w') as fp:
                json.dump(save_data, fp, indent=1)
            fp.close()

    def load(self):
        """
        load a BOM file from disk
        :return:
        """
        try:
            load_bom_file = askopenfilename(title='Open BOM File', filetypes=[('BOM files', '*.Bom')],
                                            initialdir=' ')
            file_name = os.path.split(load_bom_file)
            if file_name:
                self.bom_file_name = file_name[1]
                with open(file_name) as bomfile:
                    bom_list = json.load(bomfile)
                    bomfile.close()
                    for i in bom_list:
                        self._tree_view_list.insert('', 'end', text=i['text'], values=i['values'])

        except IOError:
            print('Error msg is: ', IOError.strerror)

    def check_part_number(self, current_part_number):
        """Check to see if part number exist in the current parts list
        :param: current_part_number to search for.
        :return: the matching part record. else false.
        """
        for part in self.bom_list:
            if current_part_number.part_number == part.part_number:
                return part
        return False

    def write_bom_list(self, my_bom_list):
        """Show the parts list in the Bom tree view
        :param: my_bom_list: parts list to show
        """
        for part in self.bom_list:
            if len(part.ref) <= 1:
                my_bom_list.insert('', 'end', text=part.part_number, values=(part.ref, part.description))
            else:
                for each in part.ref:
                    my_bom_list.insert('', 'end', text=part.part_number, values=(each, part.description))

    def number_of_boards(self, qty):
        """
        Set the number of boards to build
        :param qty: from 1 to 10
        :return: none
        """
        if qty:
            self.board_qty = int(qty)
        else:
            self.board_qty = 1
        if DEBUG:
            print('board qty is ' + str(self.board_qty))

    def inc(self, event):
        """
        Try to inc the number of parts placed
        :return: none
        """
        print(event.char)
        rowid = self._tree_view_list.focus()
        dictTemp = self._tree_view_list.set(rowid)
        self.__check_done_field(dictTemp, rowid)

        for keys, values in dictTemp.items():
            if keys == 'Done':
                values = int(values) + 1
                self._tree_view_list.set(rowid, 'Done', str(values))

        self.__auto_advance()
        if self.pnp_loaded:
            self.check_part()

    def dec(self, event):
        """
        Try to dec the number of parts placed
        :return:
        """
        rowid = self._tree_view_list.focus()
        dict_temp = self._tree_view_list.set(rowid)

        if 'Done' in dict_temp.keys():
            for keys, values in dict_temp.items():
                if keys == 'Done':
                    if int(values) >= 1:
                        values = int(values) - 1
                        self._tree_view_list.set(rowid, 'Done', str(values))
            if self.pnp_loaded:
                self.check_part()

    def bom_item_selected(self, bom_list, iid):
        """
        when a part is selected in the Bom do something
        """
        part_number, part_qty = self.check_part(bom_list, iid)
        return part_number, part_qty

    def check_part(self, bom_list, iid):
        """

        :param bom_list: list to use
        :param iid : the current selected row
        :return: selected_part_number, selected_part_qty
        """
        if bom_list:
            rowid = bom_list.focus(iid)
            current_part = bom_list.set(rowid)
            print('Current Part item ', current_part)
            dict_temp = (bom_list.item(rowid))
            qty = Part.get_part_qty(bom_list, dict_temp['text'])
            print('current qty is ', qty)
            # todo:  how to get the dang number back to the forum?
            self.selected_part_number = current_part
            self.selected_part_qty = qty

            print(bom_list.set(rowid))

            # if PickPlace.is_file_loaded:
            #     gc.delete_current_highlight(self.my_canvas)
            #     try:
            #         for pnp in PickPlace.pick_n_place_list:
            #             if pnp['ref'] == current_part['Component']:
            #                 gc.high_lite_part(self.my_canvas, pnp['x'], pnp['y'], pnp['layer'])
            #     except TypeError:
            #         pass
            return self.selected_part_number, self.selected_part_qty

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
            self._tree_view_list.set(row_id, 'Done', '1')

    def __auto_advance(self, loop_complete=False):
        """
        If the Auto Advanced check box is set move the selection to the next part.
        :return:
        """
        if self.advance:
            # current_item = self.my_bom_list.focus(item=None)
            next_item = self._tree_view_list.next(self._tree_view_list.focus(item=None))
            # self.my_bom_list.selection_toggle(current_item)
            self._tree_view_list.focus(next_item)
            self._tree_view_list.selection_set(next_item)
            self._tree_view_list.see(next_item)     # if item is not visible show it
            if DEBUG:
                print(next_item)
            check_value = self._tree_view_list.set(next_item)
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
                            self._tree_view_list.selection_toggle(next_item)
                            self.__loop_back()
                            loop_complete = False

            if self.pnp_loaded:
                self.check_part(event=None)

    def __loop_back(self):
        current_item = self._tree_view_list.focus(item=None)
        prev_item = self._tree_view_list.prev(item=current_item)
        self._tree_view_list.selection_set(current_item)
        self._tree_view_list.focus(prev_item)
        check_value = self._tree_view_list.set(prev_item)
        for fields, content in check_value.items():
            if fields == 'Component':
                component = str(content)
                if component:
                    self.__loop_back()
                if not component:
                    if self.board_qty_loop >= self.board_qty:
                        self.__auto_advance(loop_complete=True)


