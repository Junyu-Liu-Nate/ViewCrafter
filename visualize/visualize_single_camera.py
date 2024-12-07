import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

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

def plot_cameras(camera_params):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for params in camera_params:
        w2c = params['w2c']
        c2w = np.linalg.inv(w2c)

        # Camera position in world space
        camera_position = c2w[:3, 3]

        # Camera orientation vector (Z-axis)
        z_axis = c2w[:3, 2]

        # Plot camera position
        ax.scatter(camera_position[0], camera_position[1], camera_position[2], c='r', marker='o')

        # Plot camera orientation vector (Z-axis)
        ax.quiver(camera_position[0], camera_position[1], camera_position[2], z_axis[0], z_axis[1], z_axis[2], color='b', length=0.1)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Camera Positions and Orientations')
    output_file = os.path.join(data_dir, run_name, 'camera_plot.png')
    plt.savefig(output_file)

if __name__ == '__main__':
    data_dir = '/users/ljunyu/data/ljunyu/code/csci2951i/ViewCrafter/output/debug'
    run_name = '20241205_1934_frame_0000'

    camera_params_file = os.path.join(data_dir, run_name, 'camera_params.txt')
    camera_params = load_camera_params(camera_params_file)
    plot_cameras(camera_params)