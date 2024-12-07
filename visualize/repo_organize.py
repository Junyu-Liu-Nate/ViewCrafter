import os
import shutil

def organize_data():
    data_dir = '/users/ljunyu/data/ljunyu/code/csci2951i/ViewCrafter/output'
    dir1 = os.path.join(data_dir, 'rhino')
    dir2 = os.path.join(data_dir, 'rhino_traj')
    merged_dir = os.path.join(data_dir, 'rhino_data')

    # Create the merged directory if it doesn't exist
    os.makedirs(merged_dir, exist_ok=True)

    # Get the list of subdirectories from dir1
    subdirs = [d for d in os.listdir(dir1) if os.path.isdir(os.path.join(dir1, d))]

    for subdir in subdirs:
        dir1_sub = os.path.join(dir1, subdir)
        dir2_sub = os.path.join(dir2, subdir)
        merged_sub = os.path.join(merged_dir, subdir)

        # Create the subdirectory in the merged directory if it doesn't exist
        os.makedirs(merged_sub, exist_ok=True)

        # Iterate over source directories (dir1_sub and dir2_sub)
        for source_subdir in [dir1_sub, dir2_sub]:
            if os.path.exists(source_subdir):
                # Get all the frame folders in the current source subdirectory
                frame_folders = [d for d in os.listdir(source_subdir) if os.path.isdir(os.path.join(source_subdir, d))]

                for folder in frame_folders:
                    if 'frame_' in folder:
                        frame_num = 'frame_' + folder.split('frame_')[-1]
                        source_path = os.path.join(source_subdir, folder)
                        dest_path = os.path.join(merged_sub, frame_num)

                        # Copy the entire directory if it doesn't exist
                        if not os.path.exists(dest_path):
                            shutil.copytree(source_path, dest_path)
                        else:
                            # Copy individual files from source to destination if the folder exists
                            for file_name in os.listdir(source_path):
                                source_file = os.path.join(source_path, file_name)
                                dest_file = os.path.join(dest_path, file_name)
                                if os.path.isfile(source_file) and not os.path.exists(dest_file):
                                    shutil.copy2(source_file, dest_file)

if __name__ == '__main__':
    organize_data()