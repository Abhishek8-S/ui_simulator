import os
import yaml
from nats.aio.client import Client as NATS
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
import asyncio

class ui_helper:
    
    def merge_yaml_to_dict(self):
        directory = './config'  # Set the directory path here
        config_dict = {}

        for filename in os.listdir(directory):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as file:
                    data = yaml.safe_load(file)
                    if data:  # Check if data is not None
                        config_dict.update(data)
        
        print(config_dict)
        return config_dict
    
    def get_number_of_buttons(self, config_dict):
        button_config = config_dict.get('Button_config', {})
        return len(button_config)
    
    def get_button_keys(self, config_dict):
        button_config = config_dict.get('Button_config', {})
        return list(button_config.keys())
    
    def get_button_subjects(self, config_dict):
        button_config = config_dict.get('Button_config', {})
        return {key: value['subject'] for key, value in button_config.items() if 'subject' in value}

    def get_connection_url(self, config_dict):
        connection_config = config_dict.get('connection_config', {})
        return connection_config.get('url')

    async def create_stream(self, js, stream_name, subjects):
        try:
            stream_info = await js.stream_info(stream_name)
            print(f"Stream '{stream_name}' already exists with subjects: {stream_info.config.subjects}")
        except Exception as e:
            try:
                await js.add_stream(name=stream_name, subjects=subjects)
                print(f"Created stream: {stream_name} with subjects: {subjects}")
            except Exception as inner_e:
                print(f"Error creating stream '{stream_name}': {inner_e}")

    async def create_durable_consumer(self, js, stream_name, subject):
        try:
            config = {
                "durable_name": f"{stream_name}_consumer",
                "ack_policy": "explicit",
                "deliver_subject": subject
            }
            await js.add_consumer(stream_name, config)
            print(f"Created durable consumer for stream: {stream_name}, subject: {subject}")
        except Exception as e:
            print(f"Error creating durable consumer: {e}")

    async def delete_stream(self, nats_client, stream_name):
        js = nats_client.jetstream()
        try:
            await js.delete_stream(stream_name)
            print(f"Deleted stream: {stream_name}")
        except Exception as e:
            print(f"Error deleting stream '{stream_name}': {e}")


