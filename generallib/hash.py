import os
import uuid
import shutil
import get_base_dir as gbd
import generallib.general as gg
import configlib.config as cc

def generate_random_hash():
    return uuid.uuid4().hex

def generate_folder_path_list_by_hash_value(hash_value, levels=cc.DEFAULT_DATA_INFO_LEVELS):
    """
    Generate a list of folder path components based on the hash_value and specified levels.
    
    Parameters:
        hash_value (str): The hash value used to determine the folder path components.
        levels (int): The number of levels (folders) to create based on the hash_value.
        
    Returns:
        list: A list of folder path components.
    """
    # Ensure levels do not exceed the length of the hash_value
    levels = min(levels, len(hash_value))
    
    # Create a list of path components based on the first `levels` characters of the hash_value
    folder_path_list = [hash_value[i].lower() for i in range(levels)]
    
    return folder_path_list


def change_folder_hierarchy(target_dir, target_levels=cc.DEFAULT_DATA_INFO_LEVELS):
    """
    Change the folder hierarchy of files within a directory.
    
    Parameters:
        target_dir (str): The directory containing the files.
        current_level (int): The current level of folder hierarchy.
        target_levels (int): The target level of folder hierarchy.
        
    Returns:
        None
    """
    if not os.path.exists(target_dir):
        raise ValueError(f"The target directory '{target_dir}' does not exist.")
        
    for root, _, files in os.walk(target_dir):
        for file in files:
            # Get the full current path
            current_full_path = os.path.join(root, file)

            # Generate the new path based on the target level
            hash_value = file.split('.')[0]  # Assuming the file name starts with the hash value
            new_path_parts = [hash_value[i] for i in range(target_levels)]
            new_full_dir = os.path.join(target_dir, *new_path_parts)
            os.makedirs(new_full_dir, exist_ok=True)

            new_full_path = os.path.join(new_full_dir, file)

            # Move the file to the new location
            shutil.move(current_full_path, new_full_path)

            # Remove empty directories
            try:
                os.removedirs(root)
            except OSError:
                pass  # Directory not empty, skip removing

def find_file_by_hash_value(target_dir, hash_value, levels=cc.DEFAULT_DATA_INFO_LEVELS):
    """
    Find a file by its hash value in the target directory using the first few characters
    of the hash to navigate the directory structure.

    Parameters:
        target_dir (str): The base directory where the files are stored.
        hash_value (str): The hash value used to find the corresponding file.
        levels (int): The number of levels to use from the hash value for directory navigation.

    Returns:
        str: The full path to the file if found, otherwise None.
    """
    if not os.path.exists(target_dir):
        raise ValueError(f"The target directory '{target_dir}' does not exist.")
    
    search_path_parts = [hash_value[i].lower() for i in range(min(levels, len(hash_value)))]
    search_dir = os.path.join(target_dir, *search_path_parts)

    if not os.path.exists(search_dir):
        raise ValueError(f'levels:{levels} might be larger than hash_value file level')
    
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.startswith(hash_value):
                return os.path.join(root, file)
    
def delete_file_by_hash_value(target_dir, hash_value, levels=cc.DEFAULT_DATA_INFO_LEVELS):
    """
    Delete a file by its hash value in the target directory using the first few characters
    of the hash to navigate the directory structure.

    Parameters:
        target_dir (str): The base directory where the files are stored.
        hash_value (str): The hash value used to find and delete the corresponding file.
        levels (int): The number of levels to use from the hash value for directory navigation.

    Returns:
        bool: True if the file was found and deleted, False if the file was not found.
    """
    if not os.path.exists(target_dir):
        raise ValueError(f"The target directory '{target_dir}' does not exist.")
    
    search_path_parts = [hash_value[i].lower() for i in range(min(levels, len(hash_value)))]
    search_dir = os.path.join(target_dir, *search_path_parts)
    
    if not os.path.exists(search_dir):
        raise ValueError(f'levels:{levels} might be larger than hash_value file level or just no file')
    
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.startswith(hash_value):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                # Check if the directory is empty after deleting the file
                delete_empty_directories(target_dir)

                return True
    
    return False  

def delete_empty_directories(target_dir):
    """
    Delete all empty directories within the target directory.

    Parameters:
        target_dir (str): The path of the target directory.

    Returns:
        None
    """
    # Traverse the directory tree from bottom to top
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # Check if the directory is empty
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                

# Example usage
# sample_data = {
#     "hash_value": generate_random_hash(),
#     "commodity": "Gold",
#     "interval": "1d",
#     "data": [100, 101, 102, 103, 104],
#     }
# hash_value = generate_random_hash()
# levels = 2
# json_list = generate_folder_path_list_by_hash_value(hash_value, levels)
# script_dir = gbd.get_base_dir()
# dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries','data_info',*json_list, f"{hash_value}.json")
# gg.save_to_json_overwrite(sample_data,dir_path )


# test change_folder_hierarchy
# script_dir = gbd.get_base_dir()
# target_dir=os.path.join(script_dir, 'backtest_result', 'saved_equityseries','data_info')
# change_folder_hierarchy(target_dir, target_levels=2)

# test find_file_by_hash_value
# script_dir = gbd.get_base_dir()
# target_dir=os.path.join(script_dir, 'backtest_result', 'saved_equityseries','data_info')
# hash_value_to_find ='bb7d6e092cb741ffa40ed610685924b1'
# file_path = find_file_by_hash_value(target_dir, hash_value_to_find)


# test delete_file_by_hash_value
# script_dir = gbd.get_base_dir()
# target_dir = os.path.join(script_dir, 'backtest_result', 'saved_equityseries', 'data_info')
# hash_value_to_delete = '37913d9a47a04bc8bc7b87520aa9e58a'
# success = delete_file_by_hash_value(target_dir, hash_value_to_delete)

# test delete_empty_directories(target_dir)
# script_dir = gbd.get_base_dir()
# target_dir = os.path.join(script_dir, 'backtest_result', 'saved_equityseries', 'data_info')
# delete_empty_directories(target_dir)