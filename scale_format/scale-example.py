import os
import yaml
import numpy as np
from pyquaternion import Quaternion
import open3d as o3d
from scale_lidar_io_debug import LidarScene, Transform

S3_BUCKET = 'test-bucket'
TEMPLATE = yaml.load(open('template.yml'), Loader=yaml.FullLoader)

def load_radar_points(file):
    Lines = open(file, 'r').readlines()

    points = []
    for line in Lines:
        point = line.split(',')
        points.append([list(map(float, point[0:3])),list(map(float, point[3:6])),list(map(float, [point[6]]))])
    return points


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

            # radar_points = load_radar_points(f"./radar_points/{frame}.txt")
            # scene.get_frame(frame).add_radar_points(radar_points)


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
    - radar_points:
        - [X].txt (X -> frame number) (each line should be a point following this format position_x, position_y, position_z, direction_x, direction_y, direction_z, size)

"""
if __name__ == '__main__':
    scene = create_scene(
            'data/',
            frames=range(1,6)
            )

    # Debugging methods
    #  scene.get_frame(index=1).add_debug_lines()
    #  scene.preview()

    # Upload data to S3 bucket
    scene.s3_upload(S3_BUCKET, path='test-scale')
    # Create tasks/ Scale API request
    scene.create_task(TEMPLATE).publish()
