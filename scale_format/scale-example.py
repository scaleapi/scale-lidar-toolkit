import os
import numpy as np
from pyquaternion import Quaternion
import open3d as o3d
from scale_lidar_io_debug import LidarScene, Transform
import json


S3_BUCKET = 'test-bucket'
with open('template.json') as json_file:
    TEMPLATE = json.load(json_file)

def create_scene(base_path, frames):
    os.chdir(base_path)

    scene = LidarScene()
    cameras = [name for name in os.listdir("./cameras/") if os.path.isdir(os.path.join("./cameras/", name))]  # get cameras names

    for camera in cameras:
        with open(f"./cameras/{camera}/extrinsics.json") as extrinsic_file:
            camera_extrinsic = json.load(extrinsic_file)
        with open(f"./cameras/{camera}/intrinsics.json") as intrinsic_file:
            camera_intrinsic = json.load(intrinsic_file)

        scene.get_camera(camera).calibrate(
                pose=Transform().from_Rt(
                    R=Quaternion(np.array(camera_extrinsic['heading'])),
                    t=np.array(camera_extrinsic['position'])
                    ),
                K=np.array([
                    [camera_intrinsic['fx'], 0, camera_intrinsic['cx']],
                    [0,camera_intrinsic['fy'], camera_intrinsic['cy']],
                    [0,0,1],
                    ])
                # you can set here camera model if it's not 'brown_conrady' model
                # model='fisheye',
                # D= [k1, k2, p1, p2, k3],
                )

    # Add points to scene
    for frame in frames:
        # read pointcloud data in ego coordinates
        # point can be a [x,3] or [x,4] shape (intensityj)
        pcd = o3d.io.read_point_cloud(f"./pointcloud/{frame}.ply")
        with open(f"./poses/{frame}.json", 'r') as pose_file:   # load frame pose
            device_pose = json.load(pose_file)
            pose = Transform().from_Rt(
                        R=Quaternion(np.array(device_pose['heading'])),
                        t=device_pose['position']
                        )
            points = np.asarray(pcd.points)
            scene.get_frame(frame).add_points(points)
            # if points are in world coordinates you should do this
            #  scene.get_frame(frame).add_points(np.asarray(pcd.points), transform=pose.inverse)

            scene.get_frame(frame).apply_transform(pose)    # set the pose as frame pose
            for camera in cameras:  # load camera images
                scene.get_frame(frame).get_image(camera).load_file(f"./cameras/{camera}/{frame}.jpg")

    scene.make_transforms_relative()    # make all frame poses relative to the first frame, this will set the first frame as position 0,0,0

    return scene

"""
Data structure:
    - cameras:
        - camera_one:
            - [X].jpg/png (X -> frame number)
            - extrinsics.json (heading: [w,x,y,z], position: [x,y,z])
            - intrinsics.json (fx,fy,cx,cy)
        - camera_two:
            - [X].jpg/png (X -> frame number)
            - extrinsics.json (heading: [w,x,y,z], position: [x,y,z])
            - intrinsics.json (fx,fy,cx,cy)
    - pointcloud:
        - [X].ply/pcd (X -> frame number)
    - poses:
        - [X].json (X -> frame number) (heading: [w,x,y,z], position: [x,y,z])


"""
if __name__ == '__main__':
    scene = create_scene(
            'data/',
            frames=range(1,6)
            )

    # Debugging methods
    # scene.get_frame(index=1).add_debug_lines()
    # scene.preview()

    # Upload data to S3 bucket
    scene.s3_upload(S3_BUCKET, path='test-scale')
    # Create tasks/ Scale API request
    scene.create_task(TEMPLATE).publish()
