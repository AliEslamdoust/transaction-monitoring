from channels.generic.websocket import AsyncWebsocketConsumer
import json


class AdminTransactionConsumer(AsyncWebsocketConsumer):
    """
    This consumer handles WebSocket connections for admin users to receive real-time transaction updates.
    """
    group_name = "admin_global"

    async def connect(self):
        """
        Accepts the WebSocket connection and adds the user to the admin group.
        """
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Removes the user from the admin group when the connection is closed.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_transaction_update(self, event):
        """
        Sends the transaction update to the connected WebSocket client.
        """
        data = event["details"]
        await self.send(text_data=json.dumps(data))
