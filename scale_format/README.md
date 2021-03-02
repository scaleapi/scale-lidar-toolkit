# This is a code example of the Lidar Toolkit using a recommended Scale format

Data used for this example code is in `data` folder

### Data structure:
```
- cameras:
		- camera_one:
				- [X].jpg/png (X -> frame number)
				- extrinsics.json (heading: [w,x,y,z], position: [x,y,z])
				- intrinsics.json (fx,fy,cx,cy)
		- camera_two:
				- [X].jpg/png (X -> frame number)
				- extrinsics.json (heading: [w,x,y,z], position: [x,y,z])
				- intrinsics.json (fx,fy,cx,cy)
		- ... more cameras
- pointcloud:
		- [X].ply/pcd (X -> frame number)
- poses:
		- [X].json (X -> frame number) (heading: [w,x,y,z], position: [x,y,z])
- radar_points:
		- [X].txt (X -> frame number) (each line should be a point following this format position_x, position_y, position_z, direction_x, direction_y, direction_z, size)

```

Please notice that:
- Camera images, pointcloud files and world poses needs to have the same name. (Recommended name for this files is to use timestamps or a numerical order).
- Extrinsics, intrinsics and poses files could have a different data structure or include more data (like camera distortion cohefficients), this is just a basic suggestion.
