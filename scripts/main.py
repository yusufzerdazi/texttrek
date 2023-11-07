import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from openai import OpenAI
import requests
import json
from dotenv import load_dotenv

load_dotenv()

root_path = os.environ["ROOT_PATH"]
client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)

blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])

container_client = blob_service_client.get_container_client(container="treks")
if not container_client.exists():
    container_client.create_container()

blobs = [b for b in container_client.list_blobs()]
blobs.sort(key=lambda x: x.name)
folders = list({blob.name.split("/")[0] for blob in blobs})
if len(folders) == 0:
  trek = "000"
  next_index = "000"
else:
  trek = max(folders)
  current_treks = [b for b in blobs if b.name.startswith(trek) and b.name.endswith(".txt") and not b.name.endswith("summary.txt")]
  if len(current_treks) == 0:
    current_trek = trek + "/000.txt"
    trek_index = "000"
    next_index = "000"
  else:
    current_trek = current_treks[-1]
    trek_index = current_trek.name.split("/")[-1].split(".")[0]
    next_index = str(int('9' + trek_index) + 1)[1:]

# Get latest prompts & votes from blob storage (or initial prompt)

# Calculate most popular latest prompt using votes

# Combine latest prompts with previous prompts into a single command

# Generate next section of the story
votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
votes["options"].sort(key=lambda x: len(x['votes']), reverse=True)
vote = votes["options"][0]

# Story
if next_index == "000":
  prompt = (open(f"{root_path}/scripts/templates/initial.txt", "r").read()
    .replace("{{initial}}", vote["option"]))
else:
  prompt = (open(f"{root_path}/scripts/templates/continuation.txt", "r").read()
    .replace("{{summary}}", container_client.download_blob(trek + "/summary.txt").content_as_text())
    .replace("{{story}}", container_client.download_blob(current_trek).content_as_text())
    .replace("{{command}}", vote["option"])
  )

prompt_result = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", "content": prompt}]
)
container_client.upload_blob(trek + "/" + f"{next_index}.txt", prompt_result.choices[0].message.content)

# Check if the story has reached a conclusion, if so end it

# Image
current_story = container_client.download_blob(current_trek).content_as_text()
image_summary_result = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", "content": open(f"{root_path}/scripts/templates/image.txt", "r").read().replace("{{prompt}}", current_story)}]
)
container_client.upload_blob(trek + "/" + f"{next_index}_summary.txt", image_summary_result.choices[0].message.content)

images = client.images.generate(
    prompt=image_summary_result.choices[0].message.content,
    model="dall-e-3",
    n=1,
    size="1024x1024"
)
image = requests.get(images.data[0].url)
container_client.upload_blob(trek + "/" + f"{next_index}.png", image.content)

# Summary
if container_client.get_blob_client("summary.txt").exists():
  summary_text = container_client.download_blob("summary.txt").content_as_text()
else:
  summary_text = ""

summary_result = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", "content": (open(f"{root_path}/scripts/templates/summary.txt", "r").read()
    .replace("{{summary}}", summary_text)
    .replace("{{new}}", current_story))}]
)
container_client.upload_blob(trek + "/" + f"summary.txt", summary_result.choices[0].message.content, overwrite=True)

# Options
options_result = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", "content": (open(f"{root_path}/scripts/templates/options.txt", "r").read()
    .replace("{{story}}", current_story)
    .replace("{{summary}}", summary_text))}]
)
options = [o for o in options_result.choices[0].message.content.split("\n") if o != ""]
container_client.upload_blob(trek + "/votes.json", json.dumps({"options":[{"option": o, "votes": [], "created_by": "system"} for o in options]}), overwrite=True)
