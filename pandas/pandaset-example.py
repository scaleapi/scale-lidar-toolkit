from pandaset import DataSet
import os
import sys
from io import BytesIO

import tensorflow as tf
import numpy as np
import json
import glob
from pyquaternion import Quaternion
from PIL import Image

from scale_lidar_io_debug import LidarScene, Transform

###############
## CHANGE ME ##
###############
S3_BUCKET = 'test-bucket'

def create_scene(seq, frames):
    scene = LidarScene()

    # used to remove the global values from the cameras extrinsics
    initial_pose = Transform().from_Rt(
            R=Quaternion(np.array(list(seq.lidar.poses[0]['heading'].values()))),
            t=list(seq.lidar.poses[0]['position'].values())
            )

    print(seq.camera.keys())
    for camera in seq.camera.keys():
        # create the camera extrinsics using the quaternion as rotation value and the position as translation value
        camera_extrinsics = Transform().from_Rt(
                    R=Quaternion(np.array(list(seq.camera[camera].poses[frames[0]]['heading'].values()))),
                    t=list(seq.camera[camera].poses[frames[0]]['position'].values())
                    )
        scene.get_camera(camera).calibrate(
                pose= initial_pose.inverse @ camera_extrinsics, # remove world component from camera extrinsics
                K=np.array([
                    [seq.camera[camera].intrinsics.fx, 0, seq.camera[camera].intrinsics.cx],
                    [0,seq.camera[camera].intrinsics.fy, seq.camera[camera].intrinsics.cy],
                    [0,0,1],
                    ])
                )

    # Add points to scene
    for frame in frames:
        points = seq.lidar[frame].values
        points = np.array(points[:,:4]) # keep x,y,z,i values for each point
        pose = Transform().from_Rt(
                    R=Quaternion(np.array(list(seq.lidar.poses[frame]['heading'].values()))),
                    t=list(seq.lidar.poses[frame]['position'].values())
                    )

        # Why we remove the world component from cameras and points:
        #     The lidar toolkit will apply the pose to cameras and points when it generates the output jsons,
        #     so we add all the data in ego coords + the poses in each frame
        #     and leave the ego2world conversion to the lidar toolkit
        scene.get_frame(frame).add_points(points, transform=pose.inverse)   # remove the world component from the points
        scene.get_frame(frame).transform = pose # set the pose as frame pose
        for camera in seq.camera.keys():
           scene.get_frame(frame).get_image(camera).load_pil_image(seq.camera[camera].data[frame])  # load each camera image

    scene.make_transforms_relative()    # make all frame poses relative to the first frame, this will set the first frame as position 0,0,0

    return scene

if __name__ == '__main__':
    dataset = DataSet('/data/src/pandaset')
    print(dataset.sequences())
    seq001 = dataset['001'] # load only the first sequence
    seq001.load()
    print(f"Number of frames {len(seq001.lidar[:])}")
    scene = create_scene(
        seq=seq001,
        frames=range(0,5)
    )

    # Debugging methods
    #  scene.get_projected_image("front_camera").save(f'/data/pandas.png')
    #  scene.get_frame(index=1).add_debug_lines()
    #  scene.preview()

    # Upload data to S3 bucket
    scene.s3_upload(S3_BUCKET, path='test-pandaset')
    # Create tasks/ Scale API request
    scene.create_task().publish()
