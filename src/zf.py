import zipfile
from tkinter.filedialog import askopenfilename
import os


def load_zip_file():

    file_path = askopenfilename(title='Select Gerber zip file', filetypes=[('Zip files', '*.zip'),
                                                                           ('GTO Files', '*.GTO')],
                                initialdir='')
    print(file_path)
    if file_path:
        file_path_os = os.path.split(file_path)
        path = file_path_os[0]
        file = file_path_os[1]

        # end = file_path.rfind('/')
        # # print(end)
        # zip_temp = str(file_path[1:end+1])
        # zip_path = zip_temp.replace(':', 'c:')
        # print('Zip file path = ' + zip_path)
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # print(zf.NameToInfo)
                for key in zf.NameToInfo:
                    if '.GTO' in key:
                        try:
                            zf.extract(key, path=path)
                            return path, key
                        except zipfile.BadZipFile:
                            print('Bad Zip File')
                    if '.GTP' in key:
                        try:
                            zf.extract(key, path=path)
                        except zipfile.BadZipFile:
                            print('Bad Zip File')
        except TypeError:
            pass
