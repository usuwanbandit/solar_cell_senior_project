import os
from solcore.config_tools import add_source
import solcore

print(solcore.config)

home_folder = os.path.expanduser('~')
custom_nk_path = os.path.join(home_folder, 'Solcore/custommats')
nk_db_path = os.path.join(home_folder, 'Solcore/NK.db')
param_path = os.path.join(home_folder, 'Solcore/custom_params.txt')

add_source('Others', 'custom_mats', custom_nk_path)
add_source('Others', 'nk', nk_db_path)
add_source('Parameters', 'custom', param_path)