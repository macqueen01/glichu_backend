import json
from channels.generic.websocket import AsyncWebsocketConsumer
from main.BusinessLogics.Scrolls import post_scrolls

class WebsocketCallback:
    def __init__(self, status, websocket_consumer):
        self.status = status
        self.websocket_consumer = websocket_consumer

    def callback(self, message):
        callback_message = message.__setitem('status', self.status)
        self.websocket_consumer.send(json.dumps(callback_message))
        return callback_message

class ScrollsUploadConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        # Set scrollify callbacks for Websocket connection

        self.scrollify_success_callback = WebsocketCallback(200, self)
        self.scrollify_fail_callback = WebsocketCallback(500, self)
    
    async def connect(self):
        # Need Authentication logic
        self.accept()
    
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        scrollify_result = await post_scrolls.scrollify_video(
            data, 
            self.scrollify_success_callback, 
            self.scrollify_fail_callback,
            wait=True
        )

        if scrollify_result['status'] == 500:
            await self.close()
        
        upload_data = {}
        upload_data['scrolls_directory'] = scrollify_result['scrolls_directory']
        upload_data['scrolls_id'] = scrollify_result['scrolls_id']

        upload_result = await post_scrolls.upload_scrolls(
            upload_data,
            self.scrollify_success_callback,
            self.scrollify_fail_callback
        )

        await self.close()

    
    

    


