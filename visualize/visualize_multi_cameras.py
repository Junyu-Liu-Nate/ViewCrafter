import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob

def load_camera_params(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    camera_params = []
    current_frame = {}
    for line in lines:
        if line.startswith('Frame'):
            if current_frame:
                camera_params.append(current_frame)
            current_frame = {'w2c': [], 'intrinsics': []}
        elif line.startswith('w2c:'):
            current_frame['mode'] = 'w2c'
        elif line.startswith('intrinsics:'):
            current_frame['mode'] = 'intrinsics'
        else:
            values = list(map(float, line.strip().split()))
            if current_frame['mode'] == 'w2c':
                current_frame['w2c'].append(values)
            elif current_frame['mode'] == 'intrinsics':
                current_frame['intrinsics'].append(values)
    if current_frame:
        camera_params.append(current_frame)

    for params in camera_params:
        params['w2c'] = np.array(params['w2c'])
        params['intrinsics'] = np.array(params['intrinsics'])

    return camera_params

def plot_cameras(camera_params_list, colors, labels):
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    for camera_params, color, label in zip(camera_params_list, colors, labels):
        for params in camera_params:
            w2c = params['w2c']
            c2w = np.linalg.inv(w2c)

            # Camera position in world space
            camera_position = c2w[:3, 3]

            # Camera orientation vector (Z-axis)
            z_axis = c2w[:3, 2]

            # Plot camera position
            ax.scatter(camera_position[0], camera_position[1], camera_position[2], c=color, marker='o', label=label)

            # Plot camera orientation vector (Z-axis)
            ax.quiver(camera_position[0], camera_position[1], camera_position[2], z_axis[0], z_axis[1], z_axis[2], color=color, length=0.1, linewidth=0.5, alpha=0.5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Camera Positions and Orientations')
    # ax.legend()

    output_file = os.path.join(data_dir, 'camera_plot.png')
    plt.savefig(output_file, dpi=300)

def find_camera_files(data_dir, frame_nums):
    camera_files = []
    for frame_num in frame_nums:
        pattern = os.path.join(data_dir, f'*frame_{frame_num:04d}*', 'camera_params.txt')
        found_files = glob.glob(pattern)
        if found_files:
            camera_files.append(found_files[0])
    return camera_files

if __name__ == '__main__':
    data_dir = '/users/ljunyu/data/ljunyu/code/csci2951i/ViewCrafter/output/debug'
    frame_nums = [0, 30, 40]

    camera_files = find_camera_files(data_dir, frame_nums)
    camera_params_list = [load_camera_params(file) for file in camera_files]

    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']  # Add more colors if needed
    labels = [f'Frame {num}' for num in frame_nums]
    plot_cameras(camera_params_list, colors[:len(camera_params_list)], labels)