import os
import yaml
import numpy as np
from pyquaternion import Quaternion
import open3d as o3d
from scale_lidar_io_debug import LidarScene, Transform

PUBLIC_URL = "[YOUR PUBLIC HOST URL]"
SAVE_PATH = "[PATH TO STORE ZIP FILE]"
TEMPLATE = yaml.load(open('template.yml'), Loader=yaml.FullLoader)

def create_scene(base_path, frames):
    os.chdir(base_path)

    scene = LidarScene()
    cameras = [name for name in os.listdir("./cameras/") if os.path.isdir(os.path.join("./cameras/", name))]  # get cameras names

    for camera in cameras:
        with open(f"./cameras/{camera}/extrinsics.yaml", 'r') as extrinsic_file:
            camera_extrinsic = yaml.safe_load(extrinsic_file)
        with open(f"./cameras/{camera}/intrinsics.yaml", 'r') as intrinsic_file:
            camera_intrinsic = yaml.safe_load(intrinsic_file)

        scene.get_camera(camera).calibrate(
                pose=Transform().from_Rt(
                    R=Quaternion(np.array(camera_extrinsic['heading'])),
                    t=np.array(camera_extrinsic['position'])
                    ),
                K=np.array([
                    [camera_intrinsic['fx'][0], 0, camera_intrinsic['cx'][0]],
                    [0,camera_intrinsic['fy'][0], camera_intrinsic['cy'][0]],
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
        with open(f"./poses/{frame}.yaml", 'r') as pose_file:   # load frame pose
            device_pose = yaml.safe_load(pose_file)
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
            - extrinsics.yaml (heading: [w,x,y,z], position: [x,y,z])
            - intrinsics.yaml (fx,fy,cx,cy)
        - camera_two:
            - [X].jpg/png (X -> frame number)
            - extrinsics.yaml (heading: [w,x,y,z], position: [x,y,z])
            - intrinsics.yaml (fx,fy,cx,cy)
    - pointcloud:
        - [X].ply/pcd (X -> frame number)
    - poses:
        - [X].yaml (X -> frame number) (heading: [w,x,y,z], position: [x,y,z])
"""
if __name__ == '__main__':
    scene = create_scene(
            'data/',
            frames=range(1,6)
            )

    # Debugging methods
    #  scene.get_frame(index=1).add_debug_lines()
    #  scene.preview()

    scene.public_url = PUBLIC_URL     # this will set all the attachment using this url as public url source path ( eg. http://test.com will generate http://test.com/images_one.jpg)
    """
    First round:
        Generate the data
        **IMPORTANT** comment this on the second round
    """
    scene.save_task(SAVE_PATH)       # this will generate a zip file with all the data require for the scene, unzip this on [YOUR PUBLIC HOST URL]

    """
    Second round:
        Create the tasks after the data is on the public host url
        **IMPORTANT** uncomment this on the second round
    """
    #  # Create tasks/ Scale API request
    #  scene.create_task(TEMPLATE).publish()       # this will create the task on Scale system using the same data as before but it will reference it to the public host url
