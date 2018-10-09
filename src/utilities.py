def load_BOM_file(data):
    my_stuff = data
    try:
        filename = askopenfilename(title='Open BOM File', filetypes=[('CSV files', '*.csv')], initialdir=' ')

        with open(filename) as csvfile:
            global reader
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)
                my_stuff.insert('', 'end', text=row[12], values=(row[1], row[3]))
    except IOError:
        print('Error msg is: ', IOError.errno)
    finally:
        csvfile.close()


def load_txt_file():
    try:
        filename = askopenfilename(title='Open File', filetypes=[('Txt files', '*.txt')], initialdir=' ')

        text_file = open(filename, 'r')
        lines = text_file.readlines()
        for a in lines:
            print(a)
        text_file.close()
    except IOError:
        print('Error msg is: ', IOError.errno)