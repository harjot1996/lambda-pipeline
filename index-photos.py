import json
import boto3
import urllib3
import time

def lambda_handler(event, context):

    REGION = 'us-east-1'
    reko = boto3.client('rekognition', region_name=REGION)
    s3 = boto3.client('s3', region_name=REGION)
   
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    
    custom_labels = []
    try:
        head_object = s3.head_object(Bucket=bucket_name, Key=key_name)
        headers = head_object['ResponseMetadata']['HTTPHeaders']
        if 'x-amz-meta-customlabels' in headers and not headers['x-amz-meta-customlabels'] == '':
            custom_labels = headers['x-amz-meta-customlabels'].split(',')
    except:
        print("Exception occured while fetching custom labels")
   
    image_link = {'S3Object':{'Bucket':bucket_name,'Name':key_name}}
    r = reko.detect_labels(Image=image_link)
    timestamp =time.time()
    labels = [label['Name'] for label in r['Labels']]
    labels = labels + custom_labels 

    url = "https://vpc-photos-zvgzdxzcebvr2rrlzjki5wwchm.us-east-1.es.amazonaws.com/photos/0"
    headers = {"Content-Type": "application/json"}
    awsauth = ('user', 'Pa$$word2020')
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth='user:Pa$$word2020')
    headers['Content-Type'] = 'application/json'

    format = {'objectKey':key_name,'bucket':bucket_name,'createdTimestamp':timestamp,'labels':labels}
    r = http.request('POST', url, headers=headers, body=json.dumps(format))  
    #print("Post Response: ", json.loads(r.data.decode('utf8')))
   
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }