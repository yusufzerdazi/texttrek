import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from openai import OpenAI
import requests
import datetime

load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])
client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)

container_client = blob_service_client.get_container_client(container="treks")
if not container_client.exists():
    container_client.create_container()

images_container_client = blob_service_client.get_container_client(container="images")
if not images_container_client.exists():
    images_container_client.create_container()

blobs = [b for b in container_client.list_blobs()]
blobs.sort(key=lambda x: x.name)
images = [b for b in blobs if b.name.endswith(".png")]
summaries = [b for b in blobs if b.name.endswith("_summary.txt")]
images.reverse()

for image in images:
    if image.last_modified.replace(tzinfo=None) > datetime.datetime.strptime('2023-11-05', '%Y-%m-%d', ):
        continue
    # dl = container_client.download_blob(image).content_as_bytes()
    # images_container_client.upload_blob(image.name, dl, overwrite=True)
    summary = [s for s in summaries if s.name.startswith(image.name.split(".")[0])]
    if(summary):
        print(summary[0].name)
        gen = client.images.generate(
            prompt=container_client.download_blob(summary[0]).content_as_text(),
            model="dall-e-3",
            n=1,
            size="1024x1024"
        )
        gen = requests.get(gen.data[0].url)
        container_client.upload_blob(image.name, gen.content, overwrite=True)
