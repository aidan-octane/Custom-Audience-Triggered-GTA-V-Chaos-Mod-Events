# This file is a copy of the 'chatget' library that I've written, modified to grab channel point redemption events instead of chat messages.

import websockets
import asyncio
import json
import requests
from queue import Queue
import threading
import time
import logging

redemption_queue = Queue(maxsize=0)

logger = logging.getLogger(__name__)

def handle_message(message):
    message_type = message['metadata']['message_type']
    if message_type == 'notification':
        redeemer_username = f"{message['payload']['event']['user_name']}"
        redeemed_item = f"{message['payload']['event']['reward']['title']}"
        redeemed_item_id = f"{message['payload']['event']['reward']['id']}"
        payload = {
           "redeemer_username": redeemer_username,
           "redeemed_item": redeemed_item,
           "redeemed_item_id": redeemed_item_id
        }
        redemption_queue.put(payload)
    elif message_type == 'session_reconnect':
      print("Received reconnect message - aborting. Please restart the connection.")
      logger.error("Received reconnect message - aborting. Please restart the connection.")
      exit()
    elif message_type == 'session_keepalive':
      print("Keepalive message received!")
      logger.info("Keepalive message received!")
    elif message_type == 'revocation':
      print(f"Subscription revoked by Twitch: {message['payload']['subscription']['status']}")
      logger.error(f"Subscription revoked by Twitch: {message['payload']['subscription']['status']}")
      exit()


def subscribe_to_event(session_id, broadcaster_id, auth_token, reward_id, client_id):
     url = "https://api.twitch.tv/helix/eventsub/subscriptions"
     subscription_data = {
        "type": "channel.channel_points_custom_reward_redemption.add",
        "version": "1",
        "condition": {
        "broadcaster_user_id": f"{broadcaster_id}", 
        },
        "transport": {
            "method": "websocket",
            "session_id": session_id  
        }
     }
     headers = {
          "Client-ID": f"{client_id}",
          "Authorization": f"Bearer {auth_token}",
          "Content-Type": "application/json"
     }

     response = requests.post(url, headers=headers, json=subscription_data)

     if response.status_code == 202:
        response_json = response.json()
     else:  
        # print(f"Failed to create subscription: {response.status_code}")
        logger.error(f"Failed to create subscription: {response.status_code}")
        logger.error("Response json from subscription endpoint: " + response.json())
        exit()


async def connect(broadcaster_id, auth_token, reward_id, client_id):
     async with websockets.connect('wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30') as websocket:
          response = await websocket.recv()
          response_data  = json.loads(response)
          session_id = response_data['payload']['session']['id']
          # print("Status: " + response_data['payload']['session']['status'])
          logger.info("Status: " + response_data['payload']['session']['status'])
          subscribe_to_event(session_id, broadcaster_id, auth_token, reward_id, client_id)
          # print("Listening for chat messages!")
          logger.info("Listening for chat messages!")
          while True:
            response = await websocket.recv()
            message_data = json.loads(response)
            handle_message(message_data)
            time.sleep(1)


def connect_thread_start(broadcaster_id, auth_token, reward_id, client_id):
  asyncio.run(connect(broadcaster_id, auth_token, reward_id, client_id))

def run_channel_point_server(broadcaster_id, auth_token, reward_id, client_id):
    """
    Connect to the Twitch channel point redemption subscription websocket.

    This function starts the websocket connection to the Twitch API using asyncio.
    It handles the connection internally and should be called before attempting
    to retrieve chat messages. Once called, the websocket will be connected until the 
    caller process finishes execution.

    After this function is called, a queue will be populated with every chat message that 
    is sent in the channel of the specified broadcaster while the server is running.

    Parameters (in order):
        broadcaster_id: The ID of the broadcaster to get the chat from.
        auth_token: Your authentication token, received from Twitch. Please see the Twitch documentation for more information.
        reward_id: The ID of the reward to specifically subscribe to - currently unused.
        client_id: The Client ID of the application that will be using the Twitch chat, registered in the console of Twitch for Developers. 

    Returns:
        None: This function does not return any value.
    """
    websocket_thread = threading.Thread(target = connect_thread_start, args = [broadcaster_id, auth_token, reward_id, client_id])
    websocket_thread.daemon = True
    websocket_thread.start()
    

def get_next_redemption():
    """
    Gets the next reward redemption from a queue datastructure that stores every redemption since the run_channel_point_server function was invoked.

    If you place this function in 'while True' loop, and print the result of calling this function (if not None), then you will have a live-updating reward log in your terminal! 

    Returns:
        str: The next reward redemption if available, as a dictionary with keys \"redeemer_username\", \"redeemed_item\", and \"redeemed_item_id\", or None if no next chat message is available. 
    """
    if(redemption_queue.empty()):
        return None
    else:
        return redemption_queue.get()
