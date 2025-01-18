import yaml
import os

class ui_helper:
    def __init__(self):
        self.config_dir = "config"
        self.ui_config_file = os.path.join(self.config_dir, "ui_config.yaml")
        self.connection_config_file = os.path.join(self.config_dir, "connection_config.yaml")

    def merge_yaml_to_dict(self):
        """Merge UI and connection YAML files into a dictionary."""
        config = {}
        try:
            # Load UI configuration
            with open(self.ui_config_file, "r") as ui_file:
                config.update(yaml.safe_load(ui_file))
        except Exception as e:
            print(f"Error reading UI configuration: {e}")

        try:
            # Load connection configuration
            with open(self.connection_config_file, "r") as conn_file:
                config.update(yaml.safe_load(conn_file))
        except Exception as e:
            print(f"Error reading connection configuration: {e}")

        return config

    def get_button_keys(self, config):
        """Extract button keys from configuration."""
        return list(config.get("Button_config", {}).keys())

    def get_button_subjects(self, config):
        """Extract button subjects from configuration."""
        return {key: value["subject"] for key, value in config.get("Button_config", {}).items()}

    def get_connection_url(self, config):
        """Extract the NATS connection URL from configuration."""
        return config.get("connection_config", {}).get("url", "nats://localhost:4222")

    async def create_stream(self, js, stream_name, subjects):
        """Create a stream if it doesn't exist."""
        try:
            stream_info = await js.stream_info(stream_name)
            print(f"Stream '{stream_name}' already exists with subjects: {stream_info.config.subjects}")
        except Exception:
            try:
                await js.add_stream(name=stream_name, subjects=subjects)
                print(f"Created stream: {stream_name} with subjects: {subjects}")
            except Exception as inner_e:
                print(f"Error creating stream '{stream_name}': {inner_e}")

    async def create_durable_consumer(self, js, stream_name, subject):
        """Create a durable consumer for a stream."""
        try:
            await js.subscribe(
                subject, durable=stream_name, ack_policy="explicit", deliver_group=stream_name
            )
            print(f"Created durable consumer for stream: {stream_name}, subject: {subject}")
        except Exception as e:
            print(f"Error creating durable consumer: {e}")
