import tkinter as tk
from pickplace import PickPlace
import sys
import math
from tkinter import messagebox
import os

DEBUG = False


class GerberCanvas:

    file_gto = False
    file_gtp = False
    units = 0
    units_string = ('i', 'm')

    """
    my canvas
    """
    def __init__(self, frame):
        self.x_format = ''
        self.y_format = ''
        self.units = ''
        self.quadrant_mode = 0
        self.file_commands = ''
        self.file_gtp_commands = ''
        self.gerber_file_name = ''
        self.AD_commands = {}   # dict to hold aperture commands
        self.current_aperture = ''
        self.x = '0'
        self.y = '0'
        self.i = '0'
        self.j = '0'
        self.last_x = ''
        self.last_y = ''
        self.start_x = ''
        self.start_y = ''
        self.direction = 0
        self.graphics_mode = 0
        self.scaled = False
        self.bounding_box_size = ()

        self.my_canvas = tk.Canvas(frame, bg='white', bd='1')
        self.my_canvas.pack(expand=True, fill='both')
        if sys.platform == 'linux':
            self.my_canvas.bind('<Button-4>', self.__scale_image_up)
            self.my_canvas.bind('<Button-5>', self.__scale_image_down)
        else:
            self.my_canvas.bind('<MouseWheel>', self.__scale_image)

        # fixme fix the scrollbars so that they work correctly
        self.y_scrollbar = tk.Scrollbar(self.my_canvas, command=self.my_canvas.yview)
        self.y_scrollbar.pack(expand=True, fill='y', anchor='e')

        self.x_scrollbar = tk.Scrollbar(self.my_canvas, orient=tk.HORIZONTAL, command=self.my_canvas.xview)
        self.x_scrollbar.pack(fill='x', anchor='s')

        # Set this only if using in Linux
        if sys.platform == 'linux':
            self.my_canvas.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)

        self.__part_selected = 0

    def load_gerber(self, path, file):
        """load gerber file
        :param path:  path to the file
        :param file:  file name to use
        """

        try:
            # file_path = askopenfilename(title='Open Top Silk Screen File', filetypes=[('GTO files', '*.GTO')],
            #                             initialdir='')

            all_ids = self.my_canvas.find_all()
            # delete the current image if one exist.
            if all_ids:
                try:
                    for item in all_ids:
                        print(item)
                        self.my_canvas.delete(item)
                except tk.TclError:
                    messagebox.showerror('Error', tk.TclError)

            if path:
                self.file_gto = True
                try:
                    with open(os.path.join(path, file), 'r') as gerber_file:
                        self.file_commands = gerber_file.read().splitlines()
                except TypeError:
                    messagebox.showerror('Type Error', 'Invalid File Type')
                    # self._parse_file(gerber_file.read())
            self.__parse_file(self.file_commands)
            self.my_canvas.create_oval('0i', '0i', '.1i', '.1i', outline='red')
            self.gerber_file_name = file
            self.scaled = False
            # self.bounding_box_size = self.my_canvas.bbox('all')
            if DEBUG:
                print('Scroll region is : ', self.bounding_box_size)
        except IOError:
            messagebox.showerror('File Error', 'File did not open, GTO')
        finally:
            self.file_gto = False
            # load top pads into image
            self.load_gerber_gtp(os.path.join(path, file))
            self.my_canvas.config(scrollregion=self.my_canvas.bbox('all'))
            # self.my_canvas.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)

    def load_gerber_gtp(self, file_path):
        self.file_gtp = True
        try:
            print(file_path)
            new_file = 'c' + file_path[1:len(file_path)-3]+'GTP'
            print('final name =', new_file)
            if file_path:
                try:
                    with open(new_file, 'r') as gerber_file:
                        self.file_gtp_commands = gerber_file.read().splitlines()
                except TypeError:
                    messagebox.showerror('Type Error', 'Invalid File Type')
            self.__parse_file(self.file_gtp_commands)
            # self.scaled = False
        except IOError:
            messagebox.showerror('File Error', 'File did not open, GTP')

    def __parse_file(self, commands):
        if DEBUG:
            print(self.file_commands)
        temp_list = commands
        for item in temp_list:
            if DEBUG:
                print(item)
            if '%FSLA' in item:
                self.x_format = item[6:8]
                self.y_format = item[9:11]
            if '%MO' in item:
                self.units = item[3:5]
                if 'IN' in item:
                    GerberCanvas.units = 0
                if 'MM' in item:
                    GerberCanvas.units = 1
                # print('units is ', self.units)
            if 'G01' in item:
                self.graphics_mode = 1  # sets Interpolation mode graphics state parameter to linear
            if 'G03' in item:
                self.direction = 270  # CounterClockWise
            if 'G02' in item:
                self.direction = 90  # ClockWise
            if 'G74' in item:
                self.quadrant_mode = 0  # single Quadrant mode
            if 'G75' in item:
                self.quadrant_mode = 1  # Multi quadrant mode
            if '%AD' in item:   # define the aperture
                name = item[3:item.find(',')-1]
                if DEBUG:
                    print(name)
                start = item.find(',')
                stop = item.find('*', start)
                value = item[start-1:stop]
                if DEBUG:
                    print(value)
                self.AD_commands[name] = value
            if item[0:1] == 'D':    # set the current aperture
                item = item[0:item.find('*')]
                if DEBUG:
                    print('I found a ', item)
                for key, value in self.AD_commands.items():
                    self.current_ad_command = key
                    if item in key:
                        if 'R,' in value:   # for a rectangle
                            print(value)
                            x, y = self.__get_rectangle_size(value)
                            self.rect_x = x
                            self.rect_y = y
                            print('Half of x is: ', float(self.rect_x)/2)
                            # todo send this to a function to get size
                        elif 'C,' in value:     # for a circle
                            print(value)
                            self.current_aperture = self.__get_circle_diameter(value)
                        elif 'O,' in value:     # for a ob-round
                            pass
                        elif 'P,' in value:     # for a polygon
                            pass
                        elif 'TARGET' in value:
                            pass
                        elif 'THERMAL' in value:
                            pass

            # This is the Flash command. Create a flash of the object.
            if 'D03' in item:
                if DEBUG:
                    print('current key is = ', self.current_ad_command)
                    print(self.AD_commands[self.current_ad_command])
                if 'R,' in self.AD_commands[self.current_ad_command]:
                    if DEBUG:
                        print('draw a rectangle')
                    x0 = float(self.start_x) - float(self.rect_x) / 2
                    y0 = float(self.start_y) + float(self.rect_y) / 2
                    x1 = float(self.start_x) + float(self.rect_x) / 2
                    y1 = float(self.start_y) - float(self.rect_y) / 2
                    self.my_canvas.create_rectangle(str(x0) + GerberCanvas.units_string[GerberCanvas.units],
                                                    str(y0) + GerberCanvas.units_string[GerberCanvas.units],
                                                    str(x1) + GerberCanvas.units_string[GerberCanvas.units],
                                                    str(y1) + GerberCanvas.units_string[GerberCanvas.units],
                                                    outline='white', fill='black')
                if 'C,' in self.AD_commands[self.current_ad_command]:
                    print('draw a circle')

            # the D02 command is the move to command.
            if 'D02' in item:
                self.__get_numbers(item)
                if 'X' in item and 'Y' not in item:
                    self.start_x = self.x
                if 'Y' in item and 'X' not in item:
                    self.start_y = self.y
                if 'X' in item and 'Y' in item:
                    self.start_x = self.x
                    self.start_y = self.y
            # if ('D01' in item) and (('I' not in item) and ('J' not in item)):   # draw a line
            if ('D01' in item) and (('I' not in item) and ('J' not in item)):
                if self.file_gto:   # draw a line
                    self.__get_numbers(item)
                    if DEBUG:
                        print(self.start_x, ',', self.start_y, ',', self.x, ',', self.y)
                    self.my_canvas.create_line(self.start_x+'i', self.start_y+'i', self.x+'i', self.y+'i',
                                               width=self.current_aperture+'i')
                    self.start_x = self.x
                    self.start_y = self.y

            #  this Draws a circle.
            if 'D01' and 'I' and 'J' in item:  # draw a circle/arc
                if self.file_gto:
                    self.start_x = self.x
                    self.start_y = self.y
                    self.__get_numbers(item)    # test

                    if self.quadrant_mode:  # This draws circles or arcs
                        if (self.start_x == self.x) and (self.start_y == self.y):   # This draws circles
                            cp_x = float(self.start_x) + float(self.i)
                            cp_y = float(self.start_y) + float(self.j)
                            if self.i != 0:
                                radius = float(self.i)
                            elif self.j != 0:
                                radius = float(self.j)
                            try:
                                self.my_canvas.create_oval(str(cp_x - radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                           str(cp_y - radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                           str(cp_x + radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                           str(cp_y + radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                           outline='black', width=self.current_aperture)
                            except UnboundLocalError():
                                messagebox.showwarning('Warning', 'Something went wrong.')
                                break
                        else:   # This draws arcs
                            # self.evaluate_arc_command(item)
                            cp_x = float(self.start_x) + float(self.i)
                            cp_y = float(self.start_y) + float(self.j)

                            if DEBUG:
                                print(str(cp_x) + ' ' + str(cp_y))
                            if float(self.i) > 0:
                                radius = float(self.i)
                            elif float(self.j) > 0:
                                radius = float(self.j)
                            else:
                                radius = 0.0
                            self.__set_direction()
                            start_angle = math.degrees(math.atan2(float(self.start_y) - cp_y, float(self.start_x) - cp_x))
                            end_angle = math.degrees(math.atan2(float(self.y) - cp_y, float(self.x) - cp_x))
                            # radius = math.degrees(self.__get_extent(radius))
                            try:
                                self.my_canvas.create_arc(str(cp_x + radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                          str(cp_y + radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                          str(cp_x - radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                          str(cp_y - radius) + GerberCanvas.units_string[GerberCanvas.units],
                                                          style=tk.ARC, width=self.current_aperture, start=start_angle,
                                                          extent=end_angle-start_angle, outline='black')
                                # self.my_canvas.create_arc('0', '0', '100', '100', style='arc', start=90, extent=180,
                                #                           outline='purple')
                            except UnboundLocalError():
                                messagebox.showwarning('Warning', 'Something went wrong.')

    @staticmethod
    def __get_circle_diameter(value):
        return value[3:len(value)]

    @staticmethod
    def __get_rectangle_size(value):
        print(value)
        find_x = value.find('X'[0:len(value)])
        width = value[2:find_x]
        length = value[find_x+1:len(value)]
        print(width, length)
        return width, length

    def __get_extent(self, radius):
        distance = self.__distance(float(self.start_x), float(self.start_y), float(self.x), float(self.y))
        if DEBUG:
            print('distance = ', distance)
        number = (1-((distance**2) / (2*(radius**2))))
        result = number - int(number)
        return math.acos(result)

    @staticmethod
    def __distance(start_x, start_y, end_x, end_y):
        """calculate distance between two points"""
        distance = math.sqrt((start_x - end_x) ** 2 + (start_y - end_y) ** 2)
        return distance

    def __set_direction(self):
        if self.x == self.start_x:
            if self.y < self.start_y:
                self.direction = 90
            else:
                self.direction = 270
        if self.y == self.start_y:
            if self.x < self.start_x:
                self.direction = 0
            else:
                self.direction = 180

    def __get_numbers(self, item):
        found = 0

        if 'I' in item and 'J' in item and found == 0:
            found = 1
            i_start = item.find('I')
            j_start = item.find('J')
            d_start = item.find('D')

            i_temp = item[i_start+1:j_start]
            j_temp = item[j_start+1:d_start]
            j_temp = str(int(j_temp) * -1)

            self.i = self.__format_number(i_temp)
            self.j = self.__format_number(j_temp)

            if 'X' and 'Y' in item:
                found = 0

        if 'X' in item and 'Y' in item and found == 0:
            found = 1
            x_start = item.find('X')
            y_start = item.find('Y')
            d_start = item.find('D')

            x_temp = item[x_start+1:y_start]
            y_temp = item[y_start+1:d_start]
            if ('I' or 'J') in y_temp:
                for i in range(1, len(y_temp)):
                    if y_temp[i] == 'I':
                        y_temp = y_temp[0:i]
                        break
            y_temp = str(int(y_temp) * -1)

            self.x = self.__format_number(x_temp)
            self.y = self.__format_number(y_temp)

        if 'X' in item and found == 0:
            found = 1
            x_start = item.find('X')
            d_start = item.find('D')

            x_temp = item[x_start+1:d_start]

            self.x = self.__format_number(x_temp)

        if 'Y' in item and found == 0:
            found = 1
            y_start = item.find('Y')
            d_start = item.find('D')

            y_temp = item[y_start + 1:d_start]
            # flip my y axis
            y_temp = str(int(y_temp) * -1)

            self.y = self.__format_number(y_temp)

    def __format_number(self, number):
        how_long = len(number)

        if how_long <= int(self.x_format[1]):
            if '-' in number:
                temp = number[1:len(number)]
                return '-.' + temp.zfill(int(self.x_format[1]))
            else:
                return '.' + number.zfill(int(self.x_format[1]))
        elif how_long > int(self.x_format[1]):
            last = number[-5:len(number)]
            first = number[0:len(number)-5]
            if '-' in number:
                return first + '.' + last
                # return '-' + first + '.' + last
            else:
                return first + '.' + last

    def high_lite_part(self, x, y, layer):
        x1 = self.__format_pnp(x)
        y1 = self.__format_pnp(y) * -1
        last_x = float(x1) + .1
        last_y = float(y1) + .1
        if layer == 'TopLayer':
            self.__part_selected = self.my_canvas.create_oval(str(x1) + 'i', str(y1) + 'i', str(last_x) + 'i',
                                                              str(last_y) + 'i', outline='red', fill='red')
        elif layer == 'BottomLayer':
            self.__part_selected = self.my_canvas.create_oval(str(x1) + 'i', str(y1) + 'i', str(last_x) + 'i',
                                                              str(last_y) + 'i', outline='blue', fill='blue')

    def delete_current_highlight(self):
        self.my_canvas.delete(self.my_canvas, self.__part_selected)

    def __scale_image_up(self, event=None):
        self.scale_factor = 1
        self.scale_factor += .1
        self.my_canvas.scale('all', 0, 0, self.scale_factor, self.scale_factor)
        PickPlace.adjust_pic_n_place(self.scale_factor)
        self.scaled = True

    def __scale_image_down(self, event=None):
        self.scale_factor = 1
        self.scale_factor -= .1
        self.my_canvas.scale('all', 0, 0, self.scale_factor, self.scale_factor)
        if PickPlace.is_file_loaded:
            PickPlace.adjust_pic_n_place(self.scale_factor)
        self.scaled = True

    def __scale_image(self, event=None):
        if event.delta >= 120:
            self.__scale_image_up()
        elif event.delta <= -120:
            self.__scale_image_down()

    @staticmethod
    def __format_pnp(number):
        move1 = float(number) / 10
        move2 = move1 / 10
        final = move2 / 10
        return final

    def __parse_file_gtp(self):
        # print(self.file_commands)
        temp_list = self.file_commands
        for item in temp_list:
            # print(item)
            if '%FSLA' in item:
                self.x_format = item[6:8]
                self.y_format = item[9:11]
            if '%MO' in item:
                self.units = item[3:5]
                if 'IN' in item:
                    self.__inch = 1
                    self.__mm = 0
                if 'MM' in item:
                    self.__inch = 0
                    self.__mm = 1
                # print('units is ', self.units)
            if 'G01' in item:
                self.graphics_mode = 1  # sets Interpolation mode graphics state parameter to linear
            if 'G03' in item:
                self.direction = 270  # CounterClockWise
            if 'G02' in item:
                self.direction = 90  # ClockWise
            if 'G74' in item:
                self.quadrant_mode = 0  # single Quadrant mode
            if 'G75' in item:
                self.quadrant_mode = 1  # Multi quadrant mode
            if '%AD' in item:  # diameter of the circle
                name = item[3:item.find(',') - 1]
                # print(name)
                start = item.find(',')
                stop = item.find('*', start)
                value = item[start - 1:stop]
                # print(value)
                self.AD_commands[name] = value[2:len(value)]
            if item[0:1] == 'D':
                item = item[0:item.find('*')]
                # print('I found a ', item)
                for key, value in self.AD_commands.items():
                    if item in key:
                        self.current_aperture = value
            if 'D02' in item:
                self.__get_numbers(item)
                if 'X' in item and 'Y' not in item:
                    self.start_x = self.x
                if 'Y' in item and 'X' not in item:
                    self.start_y = self.y
                if 'X' in item and 'Y' in item:
                    self.start_x = self.x
                    self.start_y = self.y
            if ('D01' in item) and (('I' not in item) and ('J' not in item)):  # draw a line
                self.__get_numbers(item)
                # print(self.start_x, ',', self.start_y, ',', self.x, ',', self.y)
                self.my_canvas.create_line(self.start_x + 'i', self.start_y + 'i', self.x + 'i', self.y + 'i',
                                           width=self.current_aperture + 'i')
                self.start_x = self.x
                self.start_y = self.y
            #  this Draws a circle.
            if 'D01' and 'I' and 'J' in item:  # draw a circle
                self.start_x = self.x
                self.start_y = self.y
                self.__get_numbers(item)

                if self.quadrant_mode:  # This draws circles or arcs
                    if (self.start_x == self.x) and (self.start_y == self.y):  # This draws circles
                        cp_x = float(self.start_x) + float(self.i)
                        cp_y = float(self.start_y) + float(self.j)
                        if self.i != 0:
                            radius = float(self.i)
                        elif self.j != 0:
                            radius = float(self.j)
                        self.my_canvas.create_oval(str(cp_x - radius) + 'i', str(cp_y - radius) + 'i',
                                                   str(cp_x + radius) + 'i', str(cp_y + radius) + 'i',
                                                   outline='black', width=self.current_aperture)

                    else:  # This draws arcs
                        cp_x = float(self.start_x) + float(self.i)
                        cp_y = float(self.start_y) + float(self.j)
                        # print(str(cp_x) + ' ' + str(cp_y))
                        if float(self.i) > 0:
                            radius = float(self.i)
                        elif float(self.j) > 0:
                            radius = float(self.j)
                        self.__set_direction()
                        start_angle = math.degrees(math.atan2(float(self.start_y) - cp_y, float(self.start_x) - cp_x))
                        end_angle = math.degrees(math.atan2(float(self.y) - cp_y, float(self.x) - cp_x))
                        ext = math.degrees(self.__get_extent(radius))
                        self.my_canvas.create_arc(str(cp_x + radius) + 'i', str(cp_y + radius) + 'i',
                                                  str(cp_x - radius) + 'i', str(cp_y - radius) + 'i', style=tk.ARC,
                                                  width=self.current_aperture, start=start_angle,
                                                  extent=end_angle - start_angle, outline='black')
                        # self.my_canvas.create_arc('0', '0', '100', '100', style='arc', start=90, extent=180,
                        #                           outline='purple')

