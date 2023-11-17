import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
from openai import OpenAI
import logging
import requests

app = func.FunctionApp()
client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)
header_key = "X-Forwarded-For"
versions = {
    "V2": "005"
}

SYSTEM_PROMPT = '''
You are a text based adventure game generator, able to interpret the following commands:

Command: generate_world
Description: Return a JSON response in the following format. The prompt should be a detailed description that sets the scene for the world and character.
{
  "input": "<The prompt inputted by the user>",
  "style": "<The writing style that the story should take>",
  "setting": {
    "year": "<year>",
    "planet": "<planet>",
    "location": "<location>",
    "description": "<description>"
  }
  "character": {
    "health": "<a number out of 100 representing the character's current health>",
    "inventory": [
       <an array of items in the character's inventory>
    ],
    "age": <age>,
    "race": "<race>",
    "gender": "<gender>",
    "alignment": "<alignment>",
    "backstory": "<backstory>",
    "avatar": "A full frontal portrait of a <description>"
  },
  "options": [
    <a list of 3 possible next actions>
  ],
  "danger": "<a number up to 10 representing the current danger level of the situation>",
  "prompt": "<prompt>",
  "image": "<a description of an image that combines the character, setting and current prompt>"
}

Command: continue_story
Description: Return a JSON response in the following format, with no comments or formatting. If the action is to broad or vague, or uses an item not present in the user's inventory, the action should fail and prompt the user as to why.  Specific actions that don't make sense in context but are physically possible, are allowed. The world is full of danger and not all characters will be helpful to the user's cause. It's possible for enemies to attack the user with a probability dependent on the danger level. The story should be interesting and unpredictable with some difficult puzzles to solve, and some actions that will lead to the character's death. The prompt should provide a detailed and compelling description of the situation, and all dialogue should be returned in full.
{
  "input": "<The prompt inputted by the user>",
  "status": "<success or failure depending if the character's action succeeded>",
  "prompt": "<prompt>",
  "image": "<a description of an image that combines the character, setting and current prompt>",
  "character": {
    "health": "<a number out of 100 representing the character's current health>",
    "inventory": [
       <an array of items in the character's inventory.>
    ]
  },
  "options": [
    <a list of 3 possible next actions>
  ],
  "danger": "<a number up to 10 representing the current danger level of the situation>",
  "end": "<true or false depending if the story has reached a conclusion yet>",
  "endReason": "<the reason the the story ending, e.g. character dead or story completed>"
}
'''

blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])
container_client = blob_service_client.get_container_client(container="treks")
if not container_client.exists():
    container_client.create_container()

def get_ip_from_header(headers):
    return headers[header_key].split(":")[0]

@app.function_name(name="add")
@app.route(route="add")
def main(req):
    trek = req.params.get("trek")
    votes_blob = container_client.get_blob_client(trek + "/votes.json")
    if not votes_blob.exists():
        votes_blob.upload_blob("{\"options\":[]}")
    votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
    body = json.loads(req.get_body())
    if(body['option'] in [option['option'] for option in votes['options']]):
        return func.HttpResponse("Option already exists.", status_code=400)
    if(get_ip_from_header(req.headers) in [option['created_by'] for option in votes['options']]):
        return func.HttpResponse("User already suggested an option.", status_code=400)
    votes['options'].append({"option": body['option'], "created_by": get_ip_from_header(req.headers), "votes": []})
    votes_blob.upload_blob(json.dumps(votes), overwrite=True)
    return func.HttpResponse("OK")

@app.function_name(name="get")
@app.route(route="get")
def main(req):
    trek = req.params.get("trek")
    votes_blob = container_client.get_blob_client(trek + "/votes.json")
    if not votes_blob.exists():
        return func.HttpResponse("{\"options\":[]}")
    votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
    return func.HttpResponse(json.dumps([{"option": option["option"], "votes": len(option["votes"])} for option in votes['options']]),
        mimetype="application/json")

@app.function_name(name="vote")
@app.route(route="vote")
def main(req):
    trek = req.params.get("trek")
    votes_blob = container_client.get_blob_client(trek + "/votes.json")
    if not votes_blob.exists():
        return func.HttpResponse("Option does not exist.", status_code=400)
    votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
    body = json.loads(req.get_body())
    if(body['option'] not in [option['option'] for option in votes['options']]):
        return func.HttpResponse("Option does not exist.", status_code=400)
    if(get_ip_from_header(req.headers) in [user for v in [option['votes'] for option in votes['options']] for user in v]):
        return func.HttpResponse("User already voted.", status_code=400)
    for vote in votes['options']:
        if vote['option'] == body['option']:
            vote['votes'].append(get_ip_from_header(req.headers))
    votes_blob.upload_blob(json.dumps(votes), overwrite=True)
    return func.HttpResponse("OK")

@app.function_name(name="schedule")
@app.schedule(schedule="0 12 * * * *", 
              arg_name="timer",
              run_on_startup=False)
def schedule(timer: func.TimerRequest) -> None:
    vote_blobs = [blob for blob in container_client.list_blobs() if blob.name.endswith("votes.json") and blob.name[:3] >= versions["V2"]]
    votes = [json.loads(container_client.download_blob(blob.name).content_as_text()) for blob in vote_blobs]
    for i in range(len(votes)):
        votes[i]["trek"] = vote_blobs[i].name[:3]
    users_have_voted = [v for v in votes if [o for o in v['options'] if o['votes']]]
    logging.info(users_have_voted) 
    for vote in users_have_voted:
        extend_story(vote)

def extend_story(vote):
    story = sorted([blob for blob in container_client.list_blobs(vote["trek"]) if blob.name.endswith(".txt")], key=lambda b: b.name)
    downloaded = [json.loads(container_client.download_blob(s.name).content_as_text()) for s in story]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for i in range(len(downloaded)):
        prefix = "generate_story: " if i == 0 else "continue_story: "
        messages.append({"role": "user", "content": prefix + downloaded[i]["input"]})
        messages.append({"role": "system", "content": json.dumps(downloaded[i])})

    vote["options"].sort(key=lambda x: len(x['votes']), reverse=True)
    selected = vote["options"][0]["option"]

    messages.append({"role": "user", "content": "continue_story: " + selected})

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    next_index = str(int('9' + story[-1].name.split('/')[-1].split('.')[0]) + 1)[1:]
    container_client.upload_blob(vote["trek"] + "/" + f"{next_index}.txt", completion.choices[0].message.content)

    parsed_completion = json.loads(completion.choices[0].message.content)
    images = client.images.generate(
        prompt=parsed_completion["image"],
        model="dall-e-3",
        n=1,
        size="1024x1024"
    )
    image = requests.get(images.data[0].url)
    container_client.upload_blob(vote["trek"] + "/" + f"{next_index}.png", image.content)
    container_client.upload_blob(vote["trek"] + "/votes.json", json.dumps({"options":[{"option": o, "votes": [], "created_by": "system"} for o in parsed_completion["options"]]}), overwrite=True)