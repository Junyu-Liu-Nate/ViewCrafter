#!/bin/bash
# Request a GPU partition node and access to GPU
#SBATCH --partition=3090-gcondo
#SBATCH -p gpu --gres=gpu:1

#SBATCH -n 1
#SBATCH --mem=32G
#SBATCH -t 24:00:00

nvidia-smi

cd ../../../venv/
source viewcrafter/bin/activate
cd ../code/csci2951i/ViewCrafter/

for i in $(seq -w 0 60); do
    python inference.py \
        --image_dir test/rhino/frame_00$i.png \
        --out_dir ./output/rhino/wave1/ \
        --traj_txt test/trajs/wave1.txt \
        --mode 'single_view_txt' \
        --center_scale 1. \
        --elevation=5 \
        --seed 123 \
        --d_theta -30  \
        --d_phi 45 \
        --d_r -.2   \
        --d_x 50   \
        --d_y 25   \
        --ckpt_path ./checkpoints/model.ckpt \
        --config configs/inference_pvd_1024.yaml \
        --ddim_steps 50 \
        --video_length 25 \
        --device 'cuda:0' \
        --height 576 --width 1024 \
        --model_path ./checkpoints/DUSt3R_ViTLarge_BaseDecoder_512_dpt.pth
done