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

    def __init__(self, part_number, description):
        """
        Constructor to setup each new part

        :param part_number: this is the OEM part number for the component
        :param description: this is the description of the component
        """
        self.ref = []
        self.part_number = part_number
        self.description = description

    @staticmethod
    def get_part_qty(part_list, selected_part):
        """
        count the number of parts per list.
        :param part_list:
        :param selected_part:
        :return: how many parts
        """
        print('selected part is ', selected_part)
        # print('part list is', part_list)
        for parts in part_list:
            if selected_part in parts.ref:
                print(len(parts.ref))
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
            if selected_part in parts.description:
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
            if selected_part in parts.ref:
                return parts.part_number


class Bom:

    """
    Setup my bill of material
    """

    def __init__(self):
        self.bom_saved_file = ''
        self.advance = 0
        self.pnp_loaded = 0
        self.board_qty = 1
        self.board_qty_loop = 1
        self.bom_file_name = None
        self.bom_list = []  # hold the list of parts
        self._canvas = None

    def import_csv(self, widget):
        """
        Load the CSV file into my_bom_list
        :param widget:  the treeview widget that holds the bom
        :return: status and file name
        """
        # If parts list is already loaded clear it first
        if widget.children:
            widget.clear()
            for i in widget.get_children():
                widget.delete(i)

        # my_stuff = data
        try:
            my_bom_file = askopenfilename(title='Open BOM File', filetypes=[('CSV files', '*.CSV')],
                                          initialdir=' ')
            filename = os.path.split(my_bom_file)
            # print('filename = ', filename[1])
            self.bom_file_name = filename[1]
            if my_bom_file:
                with open(my_bom_file) as csv_file:
                    reader = csv.reader(csv_file)
                    for row in reader:  # this processes the csv file to populate the list of parts
                        # row[1] = description
                        # row[3] = ref
                        # row[12]= Part#
                        print(row)
                        try:
                            if row[12]:
                                new_component = Part(row[12], row[1])
                                # check to see if part is already in my list of parts
                                is_existing_part = self.check_part_number(new_component)
                                if is_existing_part:
                                    is_existing_part.ref.append(row[3])
                                else:
                                    new_component.ref.append(row[3])
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
                self.write_bom_list(widget)
                widget.selection_toggle('I001')
                widget.focus('I001')
                return True, self.bom_file_name

    def save(self, my_bom_list):
        """
        Saves a BOM file to disk.
        :return:
        """
        self.bom_saved_file = asksaveasfile(title='Save BOM File', filetypes=[('BOM files', '*.Bom')],
                                            initialdir='')
        if self.bom_saved_file:

            save_data = []

            my_bom_list.focus('I001')
            start_loop = True
            while start_loop:
                row_id = my_bom_list.focus()
                row_data = my_bom_list.item(row_id)
                if DEBUG:
                    print(json.dumps(row_data))
                save_data.append(row_data)
                next_id = my_bom_list.next(row_id)
                my_bom_list.focus(next_id)
                if not next_id:
                    start_loop = False
            #  save file here
            with open(self.bom_saved_file.name + '.Bom', 'w') as fp:
                json.dump(save_data, fp, indent=1)
            fp.close()

    def load(self, my_bom_list):
        """
        load a BOM file from disk
        :parameter my_bom_list
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
                        my_bom_list.insert('', 'end', text=i['text'], values=i['values'])

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
        :param event
        :return: none
        """
        # print(event.widget.focus())
        rowid = event.widget.focus()
        dictTemp = event.widget.set(rowid)
        self.__check_done_field(event.widget, dictTemp, rowid)

        for keys, values in dictTemp.items():
            if keys == 'Done':
                values = int(values) + 1
                event.widget.set(rowid, 'Done', str(values))

        self.__auto_advance(event.widget)
        if self.pnp_loaded:
            self.check_part(event.widget)

    def dec(self, event):
        """
        Try to dec the number of parts placed
        :return:
        """
        rowid = event.widget.focus()
        dict_temp = event.widget.set(rowid)

        if 'Done' in dict_temp.keys():
            for keys, values in dict_temp.items():
                if keys == 'Done':
                    if int(values) >= 1:
                        values = int(values) - 1
                        event.widget.set(rowid, 'Done', str(values))
            if self.pnp_loaded:
                self.check_part(event.widget)

    def bom_item_selected(self, bom_tree):
        """
        when a part is selected in the Bom list

        :param bom_tree:  tree widget holding the data

        :return Selected part number, selected part description, selected part qty
        """
        selected_part_number, selected_part_description, selected_part_qty = self.check_part(bom_tree)
        return selected_part_number, selected_part_description, selected_part_qty

    def check_part(self, bom_tree):
        """

        :param bom_tree: list to use
        :return: selected_part_number, selected_part_qty
        """
        rowid = bom_tree.focus()
        current_part = bom_tree.set(rowid)
        if current_part:
            print('Current Part item ', current_part)
            selected_part_number = Part.get_part_number(self.bom_list, current_part['Component'])
            selected_part_description = current_part['Description']
            selected_part_qty = Part.get_part_qty(self.bom_list, current_part['Component'])

            if PickPlace.is_file_loaded:
                gc.delete_current_highlight(self._canvas)
                try:
                    for pnp in PickPlace.pick_n_place_list:
                        if pnp['ref'] == current_part['Component']:
                            gc.high_lite_part(self._canvas, pnp['x'], pnp['y'], pnp['layer'])
                except TypeError:
                    pass
            return selected_part_number, selected_part_description, selected_part_qty

    def auto_advance(self, mode):
        """
        Set the Auto Advanced check box
        :param mode:
        :return:
        """
        self.advance = mode

    @staticmethod
    def __check_done_field(widget, dict_temp, row_id):
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
            widget.set(row_id, 'Done', '1')

    def __auto_advance(self, widget, loop_complete=False):
        """
        If the Auto Advanced check box is set move the selection to the next part.
        :return:
        """
        if self.advance:
            # current_item = self.my_bom_list.focus(item=None)
            next_item = widget.next(widget.focus(item=None))
            # self.my_bom_list.selection_toggle(current_item)
            widget.focus(next_item)
            widget.selection_set(next_item)
            widget.see(next_item)     # if item is not visible show it
            if DEBUG:
                print(next_item)
            check_value = widget.set(next_item)
            for fields, content in check_value.items():
                if DEBUG:
                    print(fields, ', ', content)
                if fields == 'Component':
                    my_string = str(content)
                    # if i find DNP or ALT skip it
                    if 'DNP' in my_string:
                        self.__auto_advance(widget)
                    if 'ALT' in my_string:
                        self.__auto_advance(widget)
                    # if i find a blank line skip it
                    if not my_string:
                        if self.board_qty_loop == self.board_qty:
                            self.__auto_advance(widget)
                            self.board_qty_loop = 1
                            loop_complete = True
                        if self.board_qty > 1 and (self.board_qty_loop <= self.board_qty) and not loop_complete:
                            self.board_qty_loop += 1
                            widget.selection_toggle(next_item)
                            self.__loop_back(widget)
                            loop_complete = False

            if self.pnp_loaded:
                self.check_part(widget)

    def __loop_back(self, widget):
        current_item = widget.focus(item=None)
        prev_item = widget.prev(item=current_item)
        widget.selection_set(current_item)
        widget.focus(prev_item)
        check_value = widget.set(prev_item)
        for fields, content in check_value.items():
            if fields == 'Component':
                component = str(content)
                if component:
                    self.__loop_back(widget)
                if not component:
                    if self.board_qty_loop >= self.board_qty:
                        self.__auto_advance(widget, loop_complete=True)
