import json
import requests

def slack_notification_content(title= 'Test title', message='Test message'):
     
     slack_data = {
         "username": "NotificationBot",
         "icon_emoji": ":bulb:",
         "channel": "#kobo",
         "attachments": [
             {
                 "color": "#9733EE",
                 "fields": [
                     {
                         "title": title,
                         "value": message,
                         "short": "false",
                     }
                  ]
             }
         ]
     }
     return slack_data

def slack_webhook(title, message):
    f = open('webh.txt','r')
    webhook_url=f.read()
    f.close()
    slack_data = slack_notification_content(title, message)
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers=headers
    )

    '''
    if response.status_code == 200:
        print("Notification Sent....")
    '''


