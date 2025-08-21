import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
from openai import OpenAI
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

VIDEO_GEN_API = "https://api.aivideoapi.com/runway/generate/text"

app = func.FunctionApp()
client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY"),
    max_retries=3,
    timeout=60.0
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
  "title": "<title of the story>"
  "setting": {
    "year": "<year>",
    "planet": "<planet>",
    "location": "<location>",
    "description": "<description>"
  }
  "character": {
    "name": "<character name>",
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
  "image": "<a description of an image that combines the character, setting and current prompt>",
  "colour": "<a medium to dark colour in hex format that would fit with the theme of the story>"
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
    <a list of 3 possible next actions, if the story hasn't ended>
  ],
  "danger": "<a number up to 10 representing the current danger level of the situation>",
  "end": "<true or false depending if the story has reached a conclusion yet>",
  "endReason": "<the reason the the story ending, e.g. character dead or story completed>"
}
'''

# Initialize blob service client with better error handling
try:
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])
    container_client = blob_service_client.get_container_client(container="treks")
    if not container_client.exists():
        container_client.create_container()
except Exception as e:
    logging.error(f"Failed to initialize blob service: {e}")
    raise

def get_ip_from_header(headers: Dict[str, str]) -> str:
    """Extract IP address from request headers."""
    return headers.get(header_key, "unknown").split(":")[0]

async def generate_image(prompt: str, filename: str, container_path: str) -> None:
    """Generate and upload an image using DALL-E 3 with enhanced features."""
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-3",
            n=1,
            size="1024x1024",
            quality="standard",
            style="vivid"
        )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        
        container_client.upload_blob(f"{container_path}/{filename}", image_response.content, overwrite=True)
        logging.info(f"Successfully generated and uploaded image: {filename}")
        
    except Exception as e:
        logging.error(f"Failed to generate image for {filename}: {e}")
        raise

async def create_chat_completion(messages: List[Dict[str, str]], model: str = "gpt-4o") -> str:
    """Create a chat completion with the latest model and enhanced features."""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Failed to create chat completion: {e}")
        raise

async def create_response_completion(instructions: str, input_text: str, model: str = "gpt-4o") -> str:
    """Use the new Responses API for better performance and features."""
    try:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=input_text,
            response_format={"type": "json_object"}
        )
        return response.output_text
    except Exception as e:
        logging.error(f"Failed to create response completion: {e}")
        # Fallback to chat completions if responses API fails
        return await create_chat_completion([
            {"role": "system", "content": instructions},
            {"role": "user", "content": input_text}
        ], model)

@app.function_name(name="add")
@app.route(route="add")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Add a new voting option."""
    try:
        trek = req.params.get("trek")
        if not trek:
            return func.HttpResponse("Trek parameter is required", status_code=400)
            
        votes_blob = container_client.get_blob_client(f"{trek}/votes.json")
        if not votes_blob.exists():
            votes_blob.upload_blob("{\"options\":[]}")
            
        votes = json.loads(container_client.download_blob(f"{trek}/votes.json").content_as_text())
        body = json.loads(req.get_body())
        
        if body['option'] in [option['option'] for option in votes['options']]:
            return func.HttpResponse("Option already exists.", status_code=400)
            
        if get_ip_from_header(req.headers) in [option['created_by'] for option in votes['options']]:
            return func.HttpResponse("User already suggested an option.", status_code=400)
            
        if len(votes['options']) >= 10:
            return func.HttpResponse("The maximum number of options has been reached.", status_code=400)
            
        votes['options'].append({
            "option": body['option'], 
            "created_by": get_ip_from_header(req.headers), 
            "votes": [],
            "created_at": datetime.utcnow().isoformat()
        })
        
        votes_blob.upload_blob(json.dumps(votes), overwrite=True)
        return func.HttpResponse("OK")
        
    except Exception as e:
        logging.error(f"Error in add function: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

@app.function_name(name="get")
@app.route(route="get")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get voting options for a trek."""
    try:
        trek = req.params.get("trek")
        if not trek:
            return func.HttpResponse("Trek parameter is required", status_code=400)
            
        votes_blob = container_client.get_blob_client(f"{trek}/votes.json")
        if not votes_blob.exists():
            return func.HttpResponse("{\"options\":[]}", mimetype="application/json")
            
        votes = json.loads(container_client.download_blob(f"{trek}/votes.json").content_as_text())
        return func.HttpResponse(
            json.dumps([{"option": option["option"], "votes": len(option["votes"])} for option in votes['options']]),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in get function: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

@app.function_name(name="vote")
@app.route(route="vote")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Vote on an option."""
    try:
        trek = req.params.get("trek")
        if not trek:
            return func.HttpResponse("Trek parameter is required", status_code=400)
            
        votes_blob = container_client.get_blob_client(f"{trek}/votes.json")
        if not votes_blob.exists():
            return func.HttpResponse("Option does not exist.", status_code=400)
            
        votes = json.loads(container_client.download_blob(f"{trek}/votes.json").content_as_text())
        body = json.loads(req.get_body())
        
        if body['option'] not in [option['option'] for option in votes['options']]:
            return func.HttpResponse("Option does not exist.", status_code=400)
            
        user_ip = get_ip_from_header(req.headers)
        if user_ip in [user for v in [option['votes'] for option in votes['options']] for user in v]:
            return func.HttpResponse("User already voted.", status_code=400)
            
        for vote in votes['options']:
            if vote['option'] == body['option']:
                vote['votes'].append(user_ip)
                vote['last_voted'] = datetime.utcnow().isoformat()
                
        votes_blob.upload_blob(json.dumps(votes), overwrite=True)
        return func.HttpResponse("OK")
        
    except Exception as e:
        logging.error(f"Error in vote function: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

@app.function_name(name="create")
@app.route(route="create")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new trek using the latest OpenAI features."""
    try:
        vote_blobs = [blob for blob in container_client.list_blobs() 
                     if blob.name.endswith("votes.json") and blob.name[:3] >= versions["V2"]]
        
        if len(vote_blobs) >= 3:
            return func.HttpResponse("There are already the maximum number of treks in progress.", status_code=400)

        latest_trek = max([blob[:3] for blob in container_client.list_blob_names()])
        next_index = str(int('9' + latest_trek) + 1)[1:]

        body = json.loads(req.get_body())
        
        # Use the new Responses API for better performance
        completion_content = asyncio.run(create_response_completion(
            instructions=SYSTEM_PROMPT,
            input_text="generate_world: " + body["prompt"],
            model="gpt-4o"
        ))
        
        container_client.upload_blob(f"{next_index}/000.txt", completion_content)

        parsed_completion = json.loads(completion_content)
        
        # Generate images asynchronously with enhanced error handling
        image_tasks = [
            generate_image(parsed_completion["image"], "000.png", next_index),
            generate_image(parsed_completion["character"]["avatar"], "avatar.png", next_index),
            generate_image(parsed_completion["setting"]["description"], "setting.png", next_index)
        ]
        
        asyncio.run(asyncio.gather(*image_tasks, return_exceptions=True))

        container_client.upload_blob(
            f"{next_index}/votes.json", 
            json.dumps({
                "options": [{"option": o, "votes": [], "created_by": "system"} for o in parsed_completion["options"]]
            }), 
            overwrite=True
        )

        return func.HttpResponse("OK")
        
    except Exception as e:
        logging.error(f"Error in create function: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

@app.function_name(name="schedule")
@app.schedule(schedule="0 0 12 * * *", 
              arg_name="timer",
              run_on_startup=False)
def schedule(timer: func.TimerRequest) -> None:
    """Scheduled function to extend stories based on votes."""
    try:
        vote_blobs = [blob for blob in container_client.list_blobs() 
                     if blob.name.endswith("votes.json") and blob.name[:3] >= versions["V2"]]
        votes = [json.loads(container_client.download_blob(blob.name).content_as_text()) for blob in vote_blobs]
        
        for i in range(len(votes)):
            votes[i]["trek"] = vote_blobs[i].name[:3]
            
        users_have_voted = [v for v in votes if [o for o in v['options'] if o['votes']]]
        logging.info(f"Processing {len(users_have_voted)} treks with votes")
        
        for vote in users_have_voted:
            try:
                extend_story(vote)
            except Exception as e:
                logging.error(f"Failed to extend story for trek {vote['trek']}: {e}")
                
    except Exception as e:
        logging.error(f"Error in schedule function: {e}")

def extend_story(vote: Dict[str, Any]) -> None:
    """Extend the story based on the winning vote using latest OpenAI features."""
    try:
        story = sorted([blob for blob in container_client.list_blobs(vote["trek"]) 
                       if blob.name.endswith(".txt")], key=lambda b: b.name)
        downloaded = [json.loads(container_client.download_blob(s.name).content_as_text()) for s in story]
        
        # Build context for the story continuation
        story_context = ""
        for i in range(len(downloaded)):
            prefix = "generate_story: " if i == 0 else "continue_story: "
            story_context += f"{prefix}{downloaded[i]['input']}\n{json.dumps(downloaded[i])}\n\n"

        vote["options"].sort(key=lambda x: len(x['votes']), reverse=True)
        selected = vote["options"][0]["option"]

        # Use the new Responses API for story continuation
        completion_content = asyncio.run(create_response_completion(
            instructions=SYSTEM_PROMPT,
            input_text=f"{story_context}continue_story: {selected}",
            model="gpt-4o"
        ))
        
        next_index = str(int('9' + story[-1].name.split('/')[-1].split('.')[0]) + 1)[1:]
        container_client.upload_blob(f"{vote['trek']}/{next_index}.txt", completion_content)

        parsed_completion = json.loads(completion_content)
        
        # Generate image asynchronously with better error handling
        try:
            asyncio.run(generate_image(
                parsed_completion["image"], 
                f"{next_index}.png", 
                vote["trek"]
            ))
        except Exception as e:
            logging.error(f"Failed to generate image for story continuation: {e}")
        
        if not parsed_completion["end"]:
            container_client.upload_blob(
                f"{vote['trek']}/votes.json", 
                json.dumps({
                    "options": [{"option": o, "votes": [], "created_by": "system"} for o in parsed_completion["options"]]
                }), 
                overwrite=True
            )
        else:
            container_client.delete_blob(f"{vote['trek']}/votes.json")
            
    except Exception as e:
        logging.error(f"Error in extend_story: {e}")
        raise

@app.function_name(name="stream")
@app.route(route="stream")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Demonstrate streaming responses with the latest OpenAI features."""
    try:
        body = json.loads(req.get_body())
        prompt = body.get("prompt", "Tell me a short story about a brave knight.")
        
        # Use streaming for real-time response generation
        stream = client.responses.create(
            model="gpt-4o",
            input=prompt,
            stream=True
        )
        
        # Collect streamed response
        full_response = ""
        for event in stream:
            if hasattr(event, 'output_text'):
                full_response += event.output_text
        
        return func.HttpResponse(
            json.dumps({"response": full_response}),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in stream function: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

@app.function_name(name="enhanced_create")
@app.route(route="enhanced_create")
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new trek with enhanced features including better error handling and request tracking."""
    try:
        vote_blobs = [blob for blob in container_client.list_blobs() 
                     if blob.name.endswith("votes.json") and blob.name[:3] >= versions["V2"]]
        
        if len(vote_blobs) >= 3:
            return func.HttpResponse("There are already the maximum number of treks in progress.", status_code=400)

        latest_trek = max([blob[:3] for blob in container_client.list_blob_names()])
        next_index = str(int('9' + latest_trek) + 1)[1:]

        body = json.loads(req.get_body())
        
        # Use enhanced client with better error handling
        enhanced_client = client.with_options(
            max_retries=5,
            timeout=120.0
        )
        
        # Create completion with request tracking
        try:
            response = enhanced_client.responses.create(
                model="gpt-4o",
                instructions=SYSTEM_PROMPT,
                input="generate_world: " + body["prompt"],
                response_format={"type": "json_object"}
            )
            
            # Log request ID for debugging
            logging.info(f"Request ID: {response._request_id}")
            
            completion_content = response.output_text
            container_client.upload_blob(f"{next_index}/000.txt", completion_content)

            parsed_completion = json.loads(completion_content)
            
            # Enhanced image generation with better error handling
            image_tasks = []
            for image_type, prompt in [
                ("000.png", parsed_completion["image"]),
                ("avatar.png", parsed_completion["character"]["avatar"]),
                ("setting.png", parsed_completion["setting"]["description"])
            ]:
                task = generate_image(prompt, image_type, next_index)
                image_tasks.append(task)
            
            # Execute with better error handling
            results = asyncio.run(asyncio.gather(*image_tasks, return_exceptions=True))
            
            # Log any image generation errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"Image generation failed for task {i}: {result}")

            container_client.upload_blob(
                f"{next_index}/votes.json", 
                json.dumps({
                    "options": [{"option": o, "votes": [], "created_by": "system"} for o in parsed_completion["options"]],
                    "created_at": datetime.utcnow().isoformat(),
                    "request_id": response._request_id
                }), 
                overwrite=True
            )

            return func.HttpResponse("OK")
            
        except Exception as e:
            logging.error(f"Enhanced create failed: {e}")
            # Fallback to standard create method
            return main(req)
        
    except Exception as e:
        logging.error(f"Error in enhanced_create function: {e}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)