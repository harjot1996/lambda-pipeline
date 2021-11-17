import json
import boto3
import urllib3

def get_image_urls(images):
    base_url = 'https://b2-foto.s3.us-east-1.amazonaws.com/'
    results = []
    for name, labels in images:
        results.append({
            "url": base_url+name,
            "labels": labels
        })
    return {"results": results}

def fetch_elastic_tags(keyword):
    url = "https://vpc-photos-zvgzdxzcebvr2rrlzjki5wwchm.us-east-1.es.amazonaws.com/photos/_search?q="+keyword
    awsauth = 'user:Pa$$word2020'
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth=awsauth)
    r = http.request('GET', url, headers=headers)
    return json.loads(r.data.decode('utf8'))

def search_labels(one, two, three):
    results = []
    results.append(fetch_elastic_tags(one))
    if two is not None:
        results.append(fetch_elastic_tags(two))
    if three is not None:
        results.append(fetch_elastic_tags(three))
   
    output = []
    unique_keys = set()
    for r in results:
        if 'hits' not in r:
            continue
        for val in r['hits']['hits']:
            key = val['_source']['objectKey']
            if key in unique_keys:
                continue
            labels = val['_source']['labels']
            output.append((key, labels))
            unique_keys.add(key)
    return output
   


def lambda_handler(event, context):
    client = boto3.client('lex-runtime', region_name='us-east-1')

    lex_response = client.post_text(
    botName='photo_bot',
    botAlias="bot",
    userId="rand_str",
    inputText = event["search_query"])
   
    dialog_state = lex_response["dialogState"]
   
    if dialog_state == 'ReadyForFulfillment' and 'slots' in lex_response:
        pass
    else:
        return {
        'statusCode': 404,
        'body': json.dumps({"message": "Try again"})
    }
   
    one = lex_response["slots"]["one"]
    two = lex_response["slots"]["two"]
    three = lex_response["slots"]["three"]
    image_links = search_labels(one, two, three)
    return get_image_urls(image_links)