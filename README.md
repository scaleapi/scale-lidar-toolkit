# Scale Lidar Toolkit

Welcome to Scale's Lidar Toolkit.

The goal of this repository is to provide you with a set of helper functions, examples, and templates to ease the process of transforming your lidar scenes into the Scale API format.

## Documentation:

**Toolkit Documentation:**

We've documented the [step by step process of using this toolkit with pictures and extensive explations](https://fieldengineering.gitbook.io/lidar-conversion/load-raw-lidar-data/intro), using the file [`lidar_template.py`](https://github.com/scaleapi/scale-lidar-toolkit/blob/master/scale_format/scale-example.py) as a base.

**Scale API Documentation:**

This toolkit aids you in getting your data from it's raw format to submitted Scale Tasks ready to be worked on. We have the [Scale format documented in full in our 3d documentation](https://private-docs.scale.com/#sensor-fusion-lidar-annotation). We'd encourage you to use this as a reference for what's possible and what the different options are.

## Setup

First things first, ensure you have Pip and Python installed.

Next,

- Run `pip3 install -r requirements.txt` (to install all the dependencies; `pip` works equally well to `pip3`)

- Grab your API key from your Scale Dashboard, we'll want to set that as an enviroment variable (`SCALE_API_KEY`) in the command line or in a file

- That's it, to pass in your API key and run any script, it will look something like `SCALE_API_KEY=live_xxxx python3 <script name>`


### Optional Setup:

We recommend using AWS S3 to host your Lidar files.

If you plan to use S3, ensure you have the the AWS CLI installed by doing `aws --version` on the terminal

If you need to install it still, you can check out AWS's guide to [Manual AWS-CLI installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

The Lidar toolkit uses [boto3](https://boto3.amazonaws.com/) to upload files to s3, this will use aws credentials stored in `~/.aws/credentials.json` (profile default). Here's an example of what this file should look like:
```
[default]
aws_access_key_id = XFSERSDFSS...
aws_secret_access_key = Asjwje1A.....
```
Do ensure your AWS credentials have permissions to upload files to the `BUCKET` specified at the top of the [script](https://github.com/scaleapi/scale-lidar-toolkit/blob/master/lidar_template.py#L18).

### New release
## [0.1.0] - 2021-02-04
- Add support for frame radar points (add_radar_point).
- Add support for frame points colors (add_colors).
