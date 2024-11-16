import os 

def get_file_path(filename):
    """Return the correct file path for local or cloud environments."""
    # Current directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # print(base_dir) 
    # rpgpt\app\utils\path_utils.py

    # Check local "assets/samples" directory
    local_path = os.path.join(base_dir, '..', 'assets', 'samples', filename)
    if os.path.exists(local_path):
        return local_path

    # Alternative path for cloud environments
    cloud_path = os.path.join('../app/assets/samples', filename)
    if os.path.exists(cloud_path):
        return cloud_path

    # Raise an error if file is not found
    raise FileNotFoundError(f"File {filename} not found in any known paths.")
