from flask import Flask, request
from flask_socketio import SocketIO
import os 
from pyngrok import ngrok
import obsws_python as obs 
from onscreen_popup import enable_popup, disable_popup
import time
import threading
from channel_point_websocket import get_next_redemption, run_channel_point_server
import queue
from update_html import update_html_file
import keyboard
from keys import broadcaster_id, auth_token, user_id, client_id, print_ngrok_instructions

print_ngrok_instructions()

# Steps - 
#       1. Start OBS
#       2. Run NGROK using the command above in a terminal
#       3. Run this

# TODO: 
#       Add all requests (from both channel points and POSTs) to a blocking queue
#       Process queue one by one to enable pop ups

redemption_queue = queue.Queue()

secret_key = os.urandom(16)
app = Flask(__name__)
app.config['SECRET_KEY'] = str(secret_key)
socketio = SocketIO(app)



def popup(next_redeemer):
    # Updates HTML file that populates with username of redeemer - this is a browser source in OBS and how viewers see who redeemed something
    update_html_file(next_redeemer)
    # In game hotkey to restart chaos mod timer
    keyboard.press_and_release("ctrl+.")
    print("Chaos mod activated!")
    # Makes each source in OBS visible - one on-screen "Award Redeemed" popup and the other being the voting options for the Chaos Mod itself
    enable_popup("Chaos Mod Popup")
    enable_popup("Chaos Mod 2")
    # Animation where the username pops up in sync to the horn playing
    time.sleep(3.867)
    enable_popup("Redeemer Username")
    time.sleep(3.2)
    disable_popup("Redeemer Username")
    time.sleep(3)
    disable_popup("Chaos Mod Popup")
    time.sleep(10)
    disable_popup("Chaos Mod 2")

# Two ways to redeem a Chaos Event - channel points and Tacho Bucks from within discord!

# Gets redeemed Chaos Event channel point redemptions from within Twitch
def get_channel_points():
    run_channel_point_server(broadcaster_id, auth_token, user_id, client_id)
    print("Redemption loop beginning")
    while True:
        msg = get_next_redemption()
        if(msg is not None): 
            item = str(msg.get("redeemed_item", "none"))
            if item == "Spawn Chaos Event":
                user_name = str(msg.get('redeemer_username', 'unknown user'))
                redemption_queue.put(user_name)
                print("Added " + user_name + " to redemption queue!")
        time.sleep(1)


# Gets redeemed Chaos Event items from the discord Tachophobi-bot that my roommate built - he just sends all purchased items over to me!
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    name = str(data['name'])
    item = str(data['item'])
    print(name + " bought " + item)
    if item == "Spawn Chaos Event":
        redemption_queue.put(name)
        print(name + " added to redemption queue!")
    # popup()
    return "Received", 200


# Processing the purchasers and enabling the popup
def process_queue():
    while True:
        next_redeemer = redemption_queue.get()
        if(next_redeemer is not None):
            print("Removed " + next_redeemer + " from redemption queue!")
            popup(next_redeemer)
            time.sleep(10)
            # Pauses chaos mod timer - timing is ever-so-slightly off, needs to be manually adjusted every 10 or so events
            keyboard.press_and_release("ctrl+.")
            print("Chaos mod paused!")
        time.sleep(1)


if __name__ == '__main__':
    # public_url = ngrok.connect(5000)
    # public_url = str(public_url)
    # print("NGROK  URL: " + public_url)
    print("Starting channel point thread!")
    get_channel_point_thread = threading.Thread(target = get_channel_points)
    get_channel_point_thread.daemon = True
    get_channel_point_thread.start()
    process_queue_thread = threading.Thread(target = process_queue)
    process_queue_thread.daemon = True
    process_queue_thread.start()
    socketio.run(app, debug=False)
 
 