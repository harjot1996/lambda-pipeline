import json
import boto3
import urllib3
import time


#TODO: Fetch head object and extract custom labels from that
#https://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3
def lambda_handler(event, context):
    print("Photo uploaded")
    print("Event:", event)
    REGION = 'us-east-1'
   
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    print("Bucket Name:", bucket_name, " Key:", key_name)
    client = boto3.client('rekognition', region_name=REGION)
   
    # Fetch custom labels from headers
    s3 = boto3.client('s3', region_name=REGION)
    custom_labels = []
    try:
        print("Trying to get head object")
        head_object = s3.head_object(Bucket=bucket_name, Key=key_name)
        print(head_object)
        headers = head_object['ResponseMetadata']['HTTPHeaders']
        if 'x-amz-meta-customlabels' in headers and not headers['x-amz-meta-customlabels'] == '':
            custom_labels = headers['x-amz-meta-customlabels'].split(',')
        print(custom_labels)
    except:
        print("Unable to fetch head object or no custom headers exits")
   
   
   
    pass_object = {'S3Object':{'Bucket':bucket_name,'Name':key_name}}
    resp = client.detect_labels(Image=pass_object)
   
   
    timestamp =time.time()
   
    labels = []
   
    for i in range(len(resp['Labels'])):
        labels.append(resp['Labels'][i]['Name'])
    print('<------------Now label list----------------->')
    labels = labels + custom_labels
    print(labels)
   
    format = {'objectKey':key_name,'bucket':bucket_name,'createdTimestamp':timestamp,'labels':labels}

    url = "https://vpc-photos-zvgzdxzcebvr2rrlzjki5wwchm.us-east-1.es.amazonaws.com/photos/0"
    headers = {"Content-Type": "application/json"}
    awsauth = ('user', 'Pa$$word2020')

    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth='user:Pa$$word2020')
    headers['Content-Type'] = 'application/json'

    r = http.request('POST', url,
                     headers=headers,
                     body=json.dumps(format))
                     
                     
    print("Result:", json.loads(r.data.decode('utf8')))
   
   
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }