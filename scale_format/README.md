# This is a code example of the Lidar Toolkit using a recommended Scale format

Data used for this example code is in `data` folder

### Data structure:
```
- cameras:
		- camera_one:
				- [X].jpg/png (X -> frame number)
				- extrinsics.yaml (heading: [w,x,y,z], position: [x,y,z])
				- intrinsics.yaml (fx,fy,cx,cy)
		- camera_two:
				- [X].jpg/png (X -> frame number)
				- extrinsics.yaml (heading: [w,x,y,z], position: [x,y,z])
				- intrinsics.yaml (fx,fy,cx,cy)
		- ... more cameras
- pointcloud:
		- [X].ply/pcd (X -> frame number)
- poses:
		- [X].yaml (X -> frame number) (heading: [w,x,y,z], position: [x,y,z])
```

Please notice that:
- Camera images, pointcloud files and world poses needs to have the same name. (Recommended name for this files is to use timestamps or a numerical order).
- Extrinsics, intrinsics and poses files could have a different data structure or include more data (like camera distortion cohefficients), this is just a basic suggestion.
