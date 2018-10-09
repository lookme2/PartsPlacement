import zipfile
from tkinter.filedialog import askopenfilename


def load_zip_file():
    # file = 'C:\\Users\\frank.brewer\\PycharmProjects\\PartsPlacement\\example files\\PCB00058B_2.zip'
    file_path = askopenfilename(title='Select Gerber zip file', filetypes=[('Zip files', '*.zip'),
                                                                           ('GTO Files', '*.GTO')],
                                initialdir='')
    print(file_path)
    if file_path:
        end = file_path.rfind('/')
        # print(end)
        zip_temp = str(file_path[1:end+1])
        zip_path = zip_temp.replace(':', 'c:')
        # print('Zip file path = ' + zip_path)
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # print(zf.NameToInfo)
                for key in zf.NameToInfo:
                    if '.GTO' in key:
                        try:
                            zf.extract(key, path=zip_path)
                            return zip_path + key
                        except zipfile.BadZipFile:
                            print('Bad Zip File')
                    if '.GTP' in key:
                        try:
                            zf.extract(key, path=zip_path)
                        except zipfile.BadZipFile:
                            print('Bad Zip File')
        except TypeError:
            pass

