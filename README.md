# Scale Lidar toolkit
Repository with Scale lidar toolkit examples

## Lidar toolkit documentation:
In depth documentation could be found [here](https://fieldengineering.gitbook.io/lidar-conversion/load-raw-lidar-data/intro). This documentation uses the file `lidar_template.py` as a base.

## Setup
### OSX
- `brew install python` (this will install python 3.7 you can use it running pythong 3 and pip3)
- run `pip3 install -r requirements.txt` (to install all the dependencies)
- create an env var with your API key called `SCALE_API_KEY`, like this `SCALE_API_KEY=live_xxxx`
- Done, now you can run any script with `python3 [script name]`

### Linux (python >3.6 required)
- run `pip install -r requirements` (to install all the dependencies)
- create an env var with your API key called `SCALE_API_KEY`, like this `SCALE_API_KEY=live_xxxx`
- Done, now you can run any script with `python3 [script name]`

### Extra requirements:
If not installed already (validate doing `aws --version` on the terminal), AWS-CLI installed  - [Manual AWS-CLI installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
The Lidar toolkit uses boto3 to upload files to s3, this will use aws credentials stored in `~/.aws/credentials.json` (profile default), example of this file:
```
[default]
aws_access_key_id = XFSERSDFSS...
aws_secret_access_key = Asjwje1A.....
```
AWS credentials needs to have permissions to upload files to the `BUCKET` specified on the script.
