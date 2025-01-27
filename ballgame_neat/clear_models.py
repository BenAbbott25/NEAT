import os
import glob

def clear_models_and_csvs(directory: str) -> None:
    # Clear .pth files
    for pth_file in glob.glob(os.path.join(directory, '**', '*.pth'), recursive=True):
        os.remove(pth_file)
    
    # Clear .csv files
    for csv_file in glob.glob(os.path.join(directory, '**', '*.csv'), recursive=True):
        os.remove(csv_file)

# Define the directory to clear
directory = 'saves/active_run_models'

# Clear the models and csv files
clear_models_and_csvs(directory)
