import torch
import trimesh
import numpy as np
import glob
from PIL import Image
import os

class CustomScene:
    def __init__(self, data_dir, frame_num, device):
        self.device = device
        self.data_dir = data_dir
        self.frame_num = frame_num
        # Load all components
        self.load_point_cloud()
        self.load_camera_pose()
        self.load_intrinsics()
        self.load_depth_map()
        self.load_image()

    def load_point_cloud(self):
        # Load the point cloud using trimesh
        pcd_mesh = trimesh.load(os.path.join(self.data_dir, 'static_combined.ply'))

        # Get vertices
        pcd_vertices = pcd_mesh.vertices  # numpy array of shape (N, 3)
        pcd_vertices = torch.from_numpy(pcd_vertices).float().to(self.device)

        # Get per-vertex colors
        # In trimesh, colors are stored in pcd_mesh.visual.vertex_colors
        # This is an array of shape (N, 4), with RGBA values in uint8
        pcd_colors = pcd_mesh.visual.vertex_colors  # numpy array of shape (N, 4)
        # Convert to float and normalize to [0,1]
        pcd_colors = pcd_colors[:, :3].astype(np.float32) / 255.0  # Exclude alpha channel
        pcd_colors = torch.from_numpy(pcd_colors).float().to(self.device)

        # Store the point cloud and colors
        self.pcd = [pcd_vertices]
        self.pcd_colors = [pcd_colors]

    def load_camera_pose(self):
        # Load camera poses from the file "pred_traj"
        pose_path = os.path.join(self.data_dir, 'pred_traj.txt')
        # Each line starts with a frame number followed by pose data
        with open(pose_path, 'r') as f:
            lines = f.readlines()

        # Find the line corresponding to the specified frame_num
        for line in lines:
            values = line.strip().split()
            if int(float(values[0])) == self.frame_num:
                pose_data = [float(v) for v in values[1:]]  # Skip the frame number
                break
        else:
            raise ValueError(f"Frame number {self.frame_num} not found in {pose_path}")

        # Assuming the pose data represents a 7-element [x, y, z, qx, qy, qz, qw]
        # Convert to a 4x4 transformation matrix
        position = np.array(pose_data[:3])
        quaternion = np.array(pose_data[3:7])  # qx, qy, qz, qw
        # Convert quaternion to rotation matrix
        rotation = self.quaternion_to_rotation_matrix(quaternion)
        # Construct the transformation matrix
        T = np.eye(4)
        T[:3, :3] = rotation
        T[:3, 3] = position
        self.c2ws = torch.from_numpy(T).float().unsqueeze(0).to(self.device)  # [1, 4, 4]

    def quaternion_to_rotation_matrix(self, q):
        # Convert quaternion [qx, qy, qz, qw] to rotation matrix
        qx, qy, qz, qw = q
        R = np.array([
            [1 - 2*(qy**2 + qz**2),     2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw)],
            [    2*(qx*qy + qz*qw), 1 - 2*(qx**2 + qz**2),     2*(qy*qz - qx*qw)],
            [    2*(qx*qz - qy*qw),     2*(qy*qz + qx*qw), 1 - 2*(qx**2 + qy**2)]
        ])
        return R

    def load_intrinsics(self):
        # Load intrinsics from "pred_intrinsics.txt"
        intrinsics_path = os.path.join(self.data_dir, 'pred_intrinsics.txt')
        # Each line corresponds to a frame
        with open(intrinsics_path, 'r') as f:
            lines = f.readlines()

        if self.frame_num >= len(lines):
            raise ValueError(f"Frame number {self.frame_num} out of range in {intrinsics_path}")

        intrinsics_line = lines[self.frame_num]
        intrinsics_values = [float(v) for v in intrinsics_line.strip().split()]
        # Assuming the intrinsics are given as a 3x3 matrix in row-major order
        K = np.array(intrinsics_values).reshape(3, 3)
        fx = K[0, 0]
        fy = K[1, 1]
        cx = K[0, 2]
        cy = K[1, 2]
        self.focals = torch.tensor([fx, fy]).unsqueeze(0).to(self.device)  # [1, 2]
        self.principal_points = torch.tensor([cx, cy]).unsqueeze(0).to(self.device)  # [1, 2]

    def load_depth_map(self):
        # Load the depth map for the specified frame from the GIF file
        depth_gif_path = os.path.join(self.data_dir, '_depth_maps.gif')
        if not os.path.isfile(depth_gif_path):
            raise FileNotFoundError(f"Depth GIF not found at {depth_gif_path}")

        # Open the GIF file
        depth_gif = Image.open(depth_gif_path)

        # Seek to the frame corresponding to frame_num
        try:
            depth_gif.seek(self.frame_num)
        except EOFError:
            raise ValueError(f"Frame number {self.frame_num} is out of range in {depth_gif_path}")

        # Extract the frame as an image
        depth_frame = depth_gif.copy()

        # Convert the depth frame to a numpy array
        depth_array = np.array(depth_frame).astype(np.float32)

        # Adjust depth scale if necessary (e.g., divide by 1000 if depth is in millimeters)
        # For example:
        # depth_array = depth_array / 1000.0  # Uncomment if needed

        depth_tensor = torch.from_numpy(depth_array).to(self.device)

        self.depth_maps = [depth_tensor]

    def load_image(self):
        # Load the image for the specified frame
        # Assuming images are stored with filenames matching frame numbers
        image_file = os.path.join(self.data_dir, f"frame_{self.frame_num:04d}.png")  # Adjust the filename format if necessary
        if not os.path.isfile(image_file):
            raise FileNotFoundError(f"Image for frame {self.frame_num} not found at {image_file}")

        img = Image.open(image_file).convert('RGB')
        img_array = np.array(img).astype(np.float32) / 255.0  # Normalize to [0,1]
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).to(self.device)  # [C, H, W]
        self.imgs = [img_tensor]

    def get_im_poses(self):
        return self.c2ws

    def get_principal_points(self):
        return self.principal_points

    def get_focals(self):
        return self.focals

    def get_pts3d(self, clip_thred=None):
        return self.pcd

    def get_depthmaps(self):
        return self.depth_maps

    def get_imgs(self):
        return self.imgs
    
    def get_pcd_colors(self):
        return self.pcd_colors