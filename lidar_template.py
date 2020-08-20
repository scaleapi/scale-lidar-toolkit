from scale_lidar_io_debug import LidarScene, Transform
import os
import json
import yaml
import numpy as np
from glob import glob

"""
Documentation for this file is in :
https://fieldengineering.gitbook.io/lidar-conversion/load-raw-lidar-data/intro
"""

###############
## CHANGE ME ##
###############
LOCAL_INPUT_PATH = ''
DATA_PATH = ''
S3_BUCKET = ''
S3_BUCKET_PATH = ''

CAMERAS = [
        'fisheye_camera',
        'front_camera'
        ]
"""
Read poses files, this will be different depending on the poses file format
"""
def read_pose(frames):
    poses = []
    for line in open('poses.txt'):
        poses.append(np.array(list(map(float, line.rstrip("\n").split(" ")))).reshape(3,4))
    if frames:
        poses = [poses[idx] for idx in frames]
    transforms = []
    for pose in poses:
        transforms.append(Transform(pose))
    return transforms

"""
Read point cloud file, with .bin extension, usually this is contains a list of points, that's why we need to reshape to -1,4 (this includes intensity)
"""
def read_lidar(frame_id):
    return np.fromfile(f'lidar:vls128/{frame_id}.bin', dtype=np.float32).reshape(-1, 4)

def load_scene(base_path, frames=None):
    os.chdir(base_path)

    """
    Definition Stage: Limit the data by frames + get source files
    """
    # read files
    files = glob('lidar:vls128/*.*', recursive=True)    # lidar files path
    frames_ids = sorted([int(frame.split("/")[-1].split(".")[0]) for frame in files])   # sort frames - this may change depending of the file names
    if frames:   # limit the number of frames
        frames_ids = [frames_ids[idx] for idx in frames]

    # New empty scene!
    scene = LidarScene()

    """
    Calibration Stage: Load global data, like poses or camera calibration
    """

    """
    Load poses.
    This will change depending on the data. You may need to just read the poses files or "normalize" it by the first frame
    """
    # Read poses
    poses = read_pose(frames)

    # Normalize poses by first frame
    offset = poses[0].inverse
    poses = [offset @ pose for pose in poses]

    # example with imu
    #  calib_imu_to_lidar = read_calib_file('calib_imu_to_lidar.txt')
    #  offset = poses[0].inverse
    #  poses = [offset @ pose for pose in poses]
    #  poses = [pose @ imu_to_lidar.inverse for pose in poses]

    """
    Add and calibrate each camera (there are multiple options to calibrate the camera, check this method on the camera class)
    """
    for camera_id in CAMERAS:
        calib = json.load(open(f'{camera_id}/camera_{camera_id}_transforms_small.txt'))
        scene.get_camera(camera_id).calibrate(
            K=np.array(calib['intrinsics']),
            pose=Transform(np.array(calib['transform'])),
        )

    #  # First example: hardcoded values
    #  scene.get_camera('rgb').calibrate(
            #  pose=Transform.from_Rt(
                #  R=np.array([
                    #  [9.99390321e-01, -2.67558875e-02, -2.24300785e-02],
                    #  [-2.24194359e-02, 6.97716781e-04, -9.99748409e-01],
                    #  [2.67648058e-02, 9.99641754e-01, 9.74394928e-05],
                    #  ]),
                #  t=np.array([-0.2319779, -0.22076198, 1.51180312])
                #  ).inverse,
            #  D=np.array([-0.15703, 0.08176, -0.00007, 0.00039, 0.00000]),
            #  K=np.array([
                #  [1882.60447, 0.0, 1230.666],
                #  [0.0, 1880.14865, 1045.725],
                #  [0.0, 0.0, 1.0]
                #  ])
            #  )

    #  # Second example: lidar to cam transformation
    #  calib_cam_to_cam = read_calib_file('calib_cam_to_cam.txt')
    #  calib_lidar_to_cam = read_calib_file('calib_lidar_to_cam.txt')
    #  lidar_to_cam = Transform.from_Rt(
            #  calib_lidar_to_cam['R'].reshape(3, 3),
            #  calib_lidar_to_cam['T'],
            #  )
    #  scene.get_camera(0).calibrate(
            #  pose=lidar_to_cam.inverse,
            #  K=calib_cam_to_cam['K_00'].reshape(3, 3) / (calib_cam_to_cam['S_00'][0] / 2896),
            #  D=calib_cam_to_cam['D_00'],
            #  )

    #  # Third example: extrinsics matrix + intrinsic focal lengths & principal point
    #  scene.get_camera(camera.name).calibrate(
            #  world_transform=Transform(camera.extrinsic.transform),
            #  fx=camera.intrinsic[0],
            #  fy=camera.intrinsic[1],
            #  cx=camera.intrinsic[2],
            #  cy=camera.intrinsic[3],
            #  )

    """
    Iteration Stage: Iterate over each frame.
    Changes made by frame should be done here
    """
    for index, frame_id in enumerate(frames_ids):
        print(f"Loading frame {frame_id}")

        # you can apply each pose in here or on the final stage
        # scene.get_frame(frame_id).apply_transform(pose)
        points = read_lidar(frame_id)
        scene.get_frame(frame_id).add_points(points)    # add points to the frame, you can also do `add_points(points, transform=[new_transform])`

        #  # alternative
        #  # if points are already in world coordinates but the cameras are not, you will need to apply the inverse of the pose to the points (turning them into ego),
        #  # so, when we create the scene, we will apply the pose to everything and points will get back to world coordinates
        #  scene.get_frame(frame_id).add_points(points, transform=pose[index].inverse)

        # Load frame image per camera
        scene.get_frame(frame_id).get_image(0).load_file(f'image_rgb/{frame_id}.png')


    """
    Final stage: Apply transformation to the full scene
    """
    # Apply poses to scene
    scene.apply_transforms(poses.values)
    # if you didn't normalize the poses by the first frame you can run this
    # scene.make_transforms_relative()

    return scene


if __name__ == '__main__':
    s = load_scene(LOCAL_INPUT_PATH, frames=range(0,20)) # load data and limit the frames to load
    s.get_frame(0).add_debug_lines()    # add lines using the camera position and heading
    #  s.get_frame(0).get_projected_image(CAMERAS_ONE).save(f'{DATA_PATH}/debug_{frame_id}.png')
    #  s.get_frame(0).save(f'{DATA_PATH}/')

    s.preview() # preview task

    #  s.s3_upload(bucket=S3_BUCKET, path=S3_BUCKET_PATH)   # store the jsons and images on s3 bucket
    #  s.create_task().publish()    # publish the task using a template payload
