import requests
import json
import yaml
import slack_sdk



class slack:
    def __init__(self, slackSettingsfile, project='cmtb'):
        self.settings = yaml.safe_load(open(slackSettingsfile, 'r'))
        self.token = self.settings[project]['slackToken']
        self.channel = self.settings[project]['slack_channel']

    def postMessageWithFiles(self, message, fileList):
        """
        postMessageWithFiles(
        message="Here is my message",
        fileList=["1.jpg", "1-Copy1.jpg"],
        channel="myFavoriteChannel",)
    
        https://stackoverflow.com/questions/59939261/send-multiple-files-to-slack-via-api/68106701#68106701"""
        import slack_sdk
        client = slack_sdk.WebClient(token=self.token, timeout=600) #, run_async=True)
        for file in fileList:
            upload = client.files_upload(file=file, filename=file)
            message = message+"<"+upload['file']['permalink']+"| >"
        outP = client.chat_postMessage(
            channel=self.channel,
            text=message)
        
    def post_message_to_slack(self, text, blocks = None):

        return requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.token,
            'channel': self.channel,
            'text': text,
            'icon_emoji': ':zany_face:',
            'username': 'spicer',
            # 'username': slack_user_name,
            'blocks': json.dumps(blocks) if blocks else None}).json()
    
    
    def post_file_to_slack(self, text, file_name, file_type=None, title=None):
        """https://keestalkstech.com/2019/10/simple-python-code-to-send-message-to-slack-channel-without-packages/"""
        file_bytes = open(file_name, 'rb').read()
        packetToSend = {
            'token': self.token,
            'filename': file_name,
            'channels': self.channel,
            'filetype': file_type,
            'initial_comment': text,
            'title': title,
            'username': 'spicer',
            'icon_emoji': ':zany_face:',
            }
        return requests.post(
          'https://slack.com/api/files.upload', packetToSend, files={'file': file_bytes}).json()