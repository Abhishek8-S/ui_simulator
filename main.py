import threading
import asyncio
import tkinter as tk
from nats.aio.client import Client as NATS
from utils.ui_helper import ui_helper


class ThreadingAdapter:
    def __init__(self, root, helper, nats_client):
        self.root = root
        self.helper = helper
        self.nats_client = nats_client
        self.loop = asyncio.get_event_loop()

    def start_gui_thread(self):
        """Start the Tkinter GUI in a separate thread."""
        threading.Thread(target=self.run_gui).start()

    def run_gui(self):
        """Run the Tkinter main loop in the main thread."""
        self.root.after(100, self.run_asyncio_in_gui_thread)
        self.root.mainloop()

    def run_asyncio_in_gui_thread(self):
        """Run the asyncio loop in the Tkinter GUI thread."""
        self.loop.call_soon_threadsafe(self.run_asyncio_loop)

    def run_asyncio_loop(self):
        """Run the asyncio event loop in the main thread."""
        try:
            self.loop.run_forever()
        except RuntimeError:
            pass

    def make_button_callback(self, subject):
        async def callback():
            await self.nats_client.publish(subject, b"Button Pressed")
            print(f"Published to subject: {subject}")

        def wrapper():
            asyncio.run_coroutine_threadsafe(callback(), self.loop)

        return wrapper

    def start_streams(self):
        """Start the stream creation task."""
        asyncio.run_coroutine_threadsafe(self._start_streams(), self.loop)

    async def _start_streams(self):
        """Asynchronous method to create streams."""
        config = self.helper.merge_yaml_to_dict()
        button_config = config.get("Button_config", {})
        js = self.nats_client.jetstream()

        # Create streams dynamically
        for key, value in button_config.items():
            stream_name = value["stream"]
            subject = value["subject"]
            await self.helper.create_stream(js, stream_name, [subject])

            # Create durable consumers for the streams
            try:
                await self.helper.create_durable_consumer(js, stream_name, subject)
            except Exception as e:
                print(f"Failed to create consumer for stream {stream_name}, subject {subject}: {e}")

        print("Streams and consumers created successfully.")

    def stop_streams(self):
        """Stop the stream tasks and quit the GUI."""
        self.root.quit()


async def main_asyncio_tasks():
    """Run all background tasks including NATS connection and stream management."""
    helper = ui_helper()
    config = helper.merge_yaml_to_dict()
    connection_url = helper.get_connection_url(config)

    # Connect to NATS server
    nats_client = NATS()
    await nats_client.connect(servers=[connection_url])
    print("Connected to NATS server")

    # Start the Tkinter GUI
    root = tk.Tk()
    adapter = ThreadingAdapter(root, helper, nats_client)

    # Start the GUI thread
    adapter.start_gui_thread()

    try:
        await asyncio.gather(asyncio.to_thread(root.mainloop))
    finally:
        await nats_client.close()
        print("NATS connection closed.")


if __name__ == "__main__":
    asyncio.run(main_asyncio_tasks())
