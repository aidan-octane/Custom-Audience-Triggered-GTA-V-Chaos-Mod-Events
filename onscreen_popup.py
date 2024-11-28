import obsws_python as obs
from keys import OBS_HOST, OBS_PASSWORD, OBS_PORT

# Will crash if OBS is not open or if it can't connect to OBS Websockets (e.g. if websockets are turned off)

cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3)


# Documentation - https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#sceneitemenablestatechanged

def enable_popup(popup_source_name):
    # Get current active scene
    resp = cl.get_scene_list()
    current_scene_name = resp.current_program_scene_name
    # current_scene_uuid = resp.current_program_scene_uuid

    # Get source that we want to manipulate
    try:
        resp = cl.get_scene_item_id(scene_name=current_scene_name, source_name=popup_source_name)
        source_id = resp.scene_item_id

        # Change visibility of source
        resp = cl.set_scene_item_enabled(scene_name=current_scene_name, item_id=source_id, enabled=True)
    except Exception as e:
        print("Error: " + str(e))

def disable_popup(popup_source_name):
    # Get current active scene
    resp = cl.get_scene_list()
    current_scene_name = resp.current_program_scene_name
    # current_scene_uuid = resp.current_program_scene_uuid

    # Get source that we want to manipulate
    try:
        resp = cl.get_scene_item_id(scene_name=current_scene_name, source_name=popup_source_name)
        source_id = resp.scene_item_id

        # Change visibility of source
        resp = cl.set_scene_item_enabled(scene_name=current_scene_name, item_id=source_id, enabled=False)
    except Exception as e:
        print("Error: " + str(e))
