import os
import pickle
import shutil
from tkinter import messagebox
import numpy as np


def show_warning(text):
    messagebox.showwarning("time taking", text)


def sec_to_hms(seconds):
    # Calculate hours, minutes, and seconds
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return hours, minutes, seconds


def back_up_data(data, version):
    with open(f'{version}.pkl', 'wb') as fin:
        pickle.dump(data, fin)
        print('dictionary saved successfully to file')


def create_folder(folder):
    import os
    current_path = os.getcwd()
    # print(current_path)
    current_path = os.path.join(current_path, folder)
    print(current_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
        print('create folder success')


def get_identical_colors(colormap, num_colors):
    # Create a normalized array of indices
    indices = np.linspace(0, 1, num_colors)
    # Get the same color for all indices
    cmap_colors = colormap(indices)[:, :3]  # Extract RGB values
    return cmap_colors


def save_file_direction(save_folder, name_text, saveing_data=None):  # find from current file
    if saveing_data is None:
        saveing_data = list()
    import os
    current_path = os.getcwd()
    current_path = os.path.join(current_path, save_folder)
    if not os.path.exists(current_path):
        os.makedirs(current_path)
        print(f'create {current_path} folder ')
    complete_Name = os.path.join(current_path, name_text + ".txt")
    with open(complete_Name, 'w') as fin:
        for item in saveing_data:
            try:
                fin.write(str(item["note"]) + '\n')
            except:pass
                # print('this file have not note')
            try:
                for layer in item['list_structure']:
                    fin.write(str(layer) + '\n')
            except:
                # print('this file have not list_structure')
                pass
            try:
                for i in item:
                    try:
                        fin.write(str(i["note"]) + '\n')
                    except:
                        # print('this file have not note')
                        pass
                    try:
                        for layer in i['list_structure']:
                            fin.write(str(layer) + '\n')
                    except:
                        # print('this file have not list_structure')
                        pass
            except:pass
    print('save success')

def movefile(file, direction):
    current_path = os.getcwd()
    save_path = os.path.join(current_path, direction)
    fig1_loc = os.path.join(current_path, file)
    fig1_loc_new = os.path.join(save_path, file)
    shutil.move(fig1_loc, fig1_loc_new)
