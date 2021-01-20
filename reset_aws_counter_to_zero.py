# -------------------------------------------------------- Imports
import json     # For saving the nested dictionary to json file, for upload in AWS s3
import logging      # For AWS s3 file upload
import boto3      # For AWS s3 file upload
from botocore.exceptions import ClientError      # For AWS s3 file upload
#=============================================================================================================================== MAIN PROGRAM RUN

def export_dictionary_as_json(data_pulls_dict):
    """
    Args: dictionary
    Returns: saves the dictionary as json file to specified location
    """
    print('Status: Function Start:[export_dictionary_as_json]')
    json_file_output_location = "/tmp/"
    json_file_output_name = 'aws_s3_access_counter.json'
    with open(json_file_output_location + json_file_output_name, "w") as outfile:
        json.dump(data_pulls_dict, outfile)
        print('Status: Function End:[export_dictionary_as_json]. Result: Successfully exported nested dictionary as JSON file')
        return json_file_output_location, json_file_output_name
    print('Status: Function End:[export_dictionary_as_json]. Result: Did not successfully export nested dictionary as JSON file')
    return False, False
def upload_file(s3_client, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    print('Status: Function Start:[upload_file]')
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print('Status: Function End:[upload_file]. Result: Successfully uploaded file to AWS s3')
        return True
    except ClientError as e:
        logging.error(e)
        print('Status: Function End:[upload_file]. Result: Did not upload file to AWS s3')
        return False
    return 'none'

def some_func():
    # Create AWS s3 client
    s3_client = boto3.client('s3')
    # Create dictionary
    data_pulls_dict = {}
    data_pulls_dict['number_of_data_pulls_aws_s3'] = 0
    # Bucket and file information
    s3_bucket_name = 'artistinformation'
    s3_file_name_full = 'aws_s3_access_counter.json'
    # Create as JSON
    json_file_output_location, json_file_output_name = export_dictionary_as_json(data_pulls_dict)
    # Upload information to s3
    upload_to_s3 = upload_file(s3_client, json_file_output_location + json_file_output_name, s3_bucket_name, json_file_output_name)
    print('uploaded')

if __name__ == '__main__':
    some_func()