import json
import boto3
import re
import time
import base64
import email
from pprint import pprint
from datetime import datetime

s3 = boto3.client('s3')
ses = boto3.client("ses")

errorMsg = '<html><head><title>Error</title><style> body { background-image: url(\'https://fileuploading1.s3.ap-southeast-2.amazonaws.com/hospital_bg.jpg\'); background-repeat: no-repeat;background-attachment: fixed; background-size: cover; }.center {display: flex;justify-content: center;align-items: center;}.div1 {font-size: xx-large; } </style> </head> <body> <div class=\'center div1\'> <h1>Audio File Connect</h1> </div> <hr> <div class=\'center\'><h2>Invalid Email ID</h2></div></body></html>'
errorAudio = '<html><head><title>Error</title><style> body { background-image: url(\'https://fileuploading1.s3.ap-southeast-2.amazonaws.com/hospital_bg.jpg\'); background-repeat: no-repeat;background-attachment: fixed; background-size: cover; }.center {display: flex;justify-content: center;align-items: center;}.div1 {font-size: xx-large; } </style> </head> <body> <div class=\'center div1\'> <h1>Audio File Connect</h1> </div> <hr> <div class=\'center\'><h2>Upload Audio Files Only</h2> </div></body></html>'
success = '<html><head><title>Error</title><style> body { background-image: url(\'https://fileuploading1.s3.ap-southeast-2.amazonaws.com/hospital_bg.jpg\'); background-repeat: no-repeat;background-attachment: fixed; background-size: cover; }.center {display: flex;justify-content: center;align-items: center;}.div1 {font-size: xx-large; } </style> </head> <body> <div class=\'center div1\'> <h1>Audio File Connect</h1> </div> <hr> <div class=\'center\'><h2>File is being processed. Mail will be sent soon.</h2> </div></body></html>'

def handler(event, context):
    data = base64.b64decode(event['body'])
    content_type = event["headers"]['content-type']
    ct = "Content-Type: "+content_type+"\n"

    # parsing message from bytes
    msg = email.message_from_bytes(ct.encode()+data)

    # if message is multipart
    if msg.is_multipart():
        multipart_content = {}
        # retrieving form-data
        for part in msg.get_payload():
            if part.get_filename():
                file_name = part.get_filename()
            multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)

    audio = multipart_content['file']
    key = datetime.now().strftime("%m%d%Y%H%M%S")
    ext = file_name.split('.')[1]
    fileName = key+'.'+ext
    
    emailid = multipart_content['mailid'].decode("utf-8") 
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(not re.search(regex,emailid)):  
        return {
            'statusCode': 200,
            'body': errorMsg,
            'headers': {
                'Content-Type': 'text/html'
            }
        }
    
    if(ext!='mp3' and ext!='mp4' and ext!='wav' and ext!='flac' and ext!='ogg' and ext!='amr' and ext!='webm'):
        return {
            'statusCode': 200,
            'body': errorAudio,
            'headers': {
                'Content-Type': 'text/html'
            }
        }

    data = s3.put_object(
        Bucket="medappaudio",
        Key=fileName,
        Body=audio,
        Metadata={'email':emailid}
    )   
    time.sleep(20)
    
    return {
        'statusCode': 200,
        'body': success,
        'headers': {
                'Content-Type': 'text/html'
            }
    }