import tkinter as tk
from utils.ui_helper import ui_helper
from nats.aio.client import Client as NATS
import asyncio

async def create_buttons(window, button_keys, button_subjects, nats_client, helper):
    def button_callback(subject):
        async def callback():
            await nats_client.publish(subject, b'Button Pressed')
        return lambda: asyncio.create_task(callback())
    
    for key in button_keys:
        button = tk.Button(window, text=key, command=button_callback(button_subjects[key]))
        button.pack(pady=5)

    start_button = tk.Button(window, text="Start Streams", command=lambda: asyncio.create_task(start_streams(nats_client, helper)))
    start_button.pack(pady=5)
    
    stop_button = tk.Button(window, text="Stop Streams", command=lambda: asyncio.create_task(stop_streams(nats_client, helper, window)))
    stop_button.pack(pady=5)

async def start_streams(nats_client, helper):
    config = helper.merge_yaml_to_dict()
    button_subjects = helper.get_button_subjects(config)
    js = nats_client.jetstream()
    for key, subject in button_subjects.items():
        await helper.create_durable_consumer(js, key, subject)
    print("Streams started.")

async def stop_streams(nats_client, helper, window):
    config = helper.merge_yaml_to_dict()
    for stream_name in config['Button_config']:
        await helper.delete_stream(nats_client, stream_name)
    await nats_client.close()
    window.quit()
    print("Streams stopped and UI closed.")

async def main():
    helper = ui_helper()
    config = helper.merge_yaml_to_dict()
    button_keys = helper.get_button_keys(config)
    button_subjects = helper.get_button_subjects(config)
    connection_url = helper.get_connection_url(config)

    # Connect to NATS server
    nats_client = NATS()
    await nats_client.connect(servers=[connection_url])

    root = tk.Tk()
    root.title("Dynamic Buttons")
    
    # Set the size of the window
    root.geometry("800x600")  # Width x Height

    await create_buttons(root, button_keys, button_subjects, nats_client, helper)
    
    root.mainloop()

if __name__ == "__main__":
    asyncio.run(main())
