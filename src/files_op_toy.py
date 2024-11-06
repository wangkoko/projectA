import os
import shutil

def split_files(source_folder, target_folder, x=2200):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    total_files = len(files)
    num_folders = 0
    
    for i in range(0, total_files, x):
        subfolder_name = f"{os.path.basename(target_folder)}_{i // x + 1}"
        subfolder_path = os.path.join(target_folder, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        
        for file in files[i:i + x]:
            shutil.move(os.path.join(source_folder, file), subfolder_path)

        num_folders += 1

    print(f"Split {total_files} files into {num_folders} folders.")

def merge_files(source_folder, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    moved_files_count = 0

    # Get all files from the source folder and its subfolders
    for root, _, files in os.walk(source_folder):
        for file in files:
            source_file_path = os.path.join(root, file)
            shutil.move(source_file_path, target_folder)
            moved_files_count += 1

    print(f"Merged {moved_files_count} files into '{target_folder}'.")

# User input for operation
operation = input("Enter 'split' to split files or 'merge' to merge files: ").strip().lower()

if operation == 'split':
    source_folder = input("Enter the path to the source folder: ")
    target_folder = input("Enter the path to the target folder: ")
    x = int(input("Enter the number of files per folder: "))  # Convert input to an integer
    split_files(source_folder, target_folder, x)
elif operation == 'merge':
    source_folder = input("Enter the path to the source folder (with subfolders): ")
    target_folder = input("Enter the path to the target folder: ")
    merge_files(source_folder, target_folder)
else:
    print("Invalid operation. Please enter 'split' or 'merge'.")

