# bbuploadmanager

**bbuploadmanager** is python library which manages all uploading, downloading, state management functionality and multiple scenarios of our Uploads & Processing of you project. 

## Features
- Uploading file to AWS S3
- Downloading file from AWS S3
- Upload Processing state management
- Upload Manager Dashboard 
- Upload tracking

## Installation

pip install https://github.com/Bigbasket/bbuploadmanager

### Prerequisite

- Python3 and above 
- Django2 and above

#### Environment
AWS_STORAGE_BUCKET_NAME
- variable need to be present in environment to specify aws bucket.

S3_OBJECT_LIFECYCLE_DAYS 
- variable need to be present in environment to specify life cycle of a object in s3 bucket.

## Sample Code

```
# Library Plugin code to be added in settings.py
INSTALLED_APPS = ["upload_manager.apps.UploadManagerConfig"]

# Below code to be implementation in your application.py\
# imports
from upload_manager.service import UploadManagerService
from upload_manager.utils import get_upload_id_s3_url
from upload_manager.s3 import S3FileManager

# file upload example
upload_service = UploadManagerService(<upload_name>, <username>, <S3_bucket_path>, files=[<file_obj>,])
upload_obj = upload_service.start_upload()

# reading file data example
s3_url = get_upload_id_s3_url(upload_obj.id)
file_data = S3FileManager().read_file_from_s3(s3_url)

# writing response file example
upload_service.file_content = [("OrderId", "Status", "Message"),(11020304, "Success", "")]
upload_service.update_response_for_upload(upload_obj_id)

# updating upload status example
UploadManagerService.change_upload_status_to_inprocess(upload_obj.id)
UploadManagerService.change_upload_status_to_complete(upload_obj.id)
UploadManagerService.change_upload_status_to_failed(upload_obj.id)`