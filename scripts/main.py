import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import openai
import requests

root_path = os.environ["ROOT_PATH"]
openai.organization = os.environ["OPEN_AI_ORGANIZATION"]
openai.api_key = os.environ["OPEN_AI_KEY"]

blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])

container_client = blob_service_client.get_container_client(container="treks")
if not container_client.exists():
    container_client.create_container()

blobs = [b for b in container_client.list_blobs()]
blobs.sort(key=lambda x: x.name)
folders = list({blob.name.split("/")[0] for blob in blobs})
if folders == []:
  trek = "000"
  next_index = "000"
else:
  trek = folders[-1]
  current_trek = [b for b in blobs if b.name.startswith(trek) and b.name.endswith(".txt") and not b.name.endswith("summary.txt")][-1]
  trek_index = current_trek.name.split("/")[-1].split(".")[0]
  next_index = str(int('9' + trek_index) + 1)[1:]

# Get latest prompts & votes from blob storage (or initial prompt)

# Calculate most popular latest prompt using votes

# Combine latest prompts with previous prompts into a single command

# Generate next section of the story
text_input = "Attack the evil goblin within for the final battle. This should be the conclusion of the story"
if next_index == "000":
  prompt = open(f"{root_path}/scripts/templates/initial.txt", "r").read()
else:
  prompt = (open(f"{root_path}/scripts/templates/continuation.txt", "r").read()
    .replace("{{story}}", container_client.download_blob(current_trek).content_as_text())
    .replace("{{command}}", text_input)
  )

prompt_result = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[{"role": "user", "content": prompt}]
)
container_client.upload_blob(trek + "/" + f"{next_index}.txt", prompt_result.choices[0].message.content)

# Check if the story has reached a conclusion, if so end it

# Generate accompanying image
summary_result = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[{"role": "user", "content": open(f"{root_path}/scripts/templates/image.txt", "r").read().replace("{{prompt}}", container_client.download_blob(current_trek).content_as_text())}]
)
container_client.upload_blob(trek + "/" + f"{next_index}_summary.txt", summary_result.choices[0].message.content)

images = openai.Image.create(
    prompt=summary_result.choices[0].message.content,
    n=1,
    size="1024x1024"
)

image = requests.get(images.data[0].url)

# Download image and save to blob storage
container_client.upload_blob(trek + "/" + f"{next_index}.png", image.content)
