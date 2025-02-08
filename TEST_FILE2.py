import json
import boto3
import os
import time

s3 = boto3.client('s3')

def get_metadata(bucket_name, key):
    """
    Fetches the metadata for the object to check if parts are already uploaded.
    """
    try:
        response = s3.head_object(Bucket=bucket_name, Key=key)
        if 'Metadata' in response and 'upload-parts' in response['Metadata']:
            return json.loads(response['Metadata']['upload-parts'])
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NotFound':
            return []  # No metadata available
        else:
            raise e
    return []

def save_metadata(bucket_name, key, metadata):
    """
    Save the upload parts metadata to the object's metadata.
    """
    s3.copy_object(
        Bucket=bucket_name,
        Key=key,
        CopySource={'Bucket': bucket_name, 'Key': key},
        Metadata={'upload-parts': json.dumps(metadata)},
        MetadataDirective='REPLACE'
    )

def initiate_multipart_upload(bucket_name, key):
    """
    Initiates a multipart upload and returns the UploadId.
    """
    print(f"Initiating multipart upload for bucket: {bucket_name}, key: {key}")
    response = s3.create_multipart_upload(Bucket=bucket_name, Key=key)
    return response['UploadId']

def upload_part(bucket_name, key, upload_id, part_number, data):
    """
    Uploads a part of the file to S3 and returns the ETag.
    """
    time.sleep(60)
    print(f"Uploading part {part_number} for bucket: {bucket_name}, key: {key}")
    print("Sleeping for 60 seconds")
    response = s3.upload_part(
        Bucket=bucket_name,
        Key=key,
        UploadId=upload_id,
        PartNumber=part_number,
        Body=data
    )
    return response['ETag']

def complete_multipart_upload(bucket_name, key, upload_id, parts):
    """
    Completes the multipart upload using the parts metadata.
    """
    try:
        print("Completing multipart upload...")
        s3.complete_multipart_upload(
            Bucket=bucket_name,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
    except Exception as e:
        print(f"Error in completing multipart upload: {e}")
        raise

def transfer_data(source_bucket, source_key, destination_bucket, destination_key, upload_id=None, completed_parts=None, current_part_number=1):
    """
    Transfers data from the source bucket to the destination bucket.
    """
    part_size = 5 * 1024 * 1024  # 5 MB
    parts = completed_parts if completed_parts else []
    part_number = current_part_number

    # Get the size of the source file
    response = s3.head_object(Bucket=source_bucket, Key=source_key)
    file_size = response['ContentLength']
    print(f"File size: {file_size} bytes")

    # Initiate multipart upload if not resuming
    if not upload_id:
        upload_id = initiate_multipart_upload(destination_bucket, destination_key)
    else:
        # Fetch existing metadata from destination to resume the upload
        parts = get_metadata(destination_bucket, destination_key)
        part_number = len(parts) + 1

    try:
        # Process file parts
        for start in range((part_number - 1) * part_size, file_size, part_size):
            end = min(start + part_size, file_size)
            byte_range = f"bytes={start}-{end - 1}"

            # Download part using get_object
            print(f"Downloading part {part_number} with range {byte_range}")
            response = s3.get_object(Bucket=source_bucket, Key=source_key, Range=byte_range)
            part_data = response['Body'].read()

            # Upload part
            print(f"Uploading part {part_number}")
            etag = upload_part(
                bucket_name=destination_bucket,
                key=destination_key,
                upload_id=upload_id,
                part_number=part_number,
                data=part_data
            )
            parts.append({'PartNumber': part_number, 'ETag': etag.strip('"')})

            # Save metadata after each part upload
            save_metadata(destination_bucket, destination_key, parts)

            part_number += 1

        # Complete multipart upload
        complete_multipart_upload(destination_bucket, destination_key, upload_id, parts)
        print("File transfer completed successfully!")
        return {
            "status": "SUCCESS",
            "upload_id": upload_id,
            "completed_parts": parts,
            "current_part_number": part_number
        }

    except Exception as e:
        print(f"Error during file transfer: {e}")
        s3.abort_multipart_upload(Bucket=destination_bucket, Key=destination_key, UploadId=upload_id)
        raise

def lambda_handler(event, context):
    """
    AWS Lambda handler.
    """
    source_bucket = event['source_bucket']
    source_key = event['source_key']
    destination_bucket = event['destination_bucket']
    destination_key = event['destination_key']

    # Retrieve state data for resuming uploads
    upload_id = event.get('upload_id')
    completed_parts = event.get('completed_parts', [])
    current_part_number = event.get('current_part_number', 1)

    try:
        # Start or resume the file transfer
        result = transfer_data(
            source_bucket=source_bucket,
            source_key=source_key,
            destination_bucket=destination_bucket,
            destination_key=destination_key,
            upload_id=upload_id,
            completed_parts=completed_parts,
            current_part_number=current_part_number
        )
        return result

    except Exception as e:
        print(f"Exception in Lambda: {e}")
        return {
            "status": "FAILED",
            "error_message": str(e),
            "upload_id": upload_id,
            "completed_parts": completed_parts,
            "current_part_number": current_part_number
        }
