import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json

app = func.FunctionApp()
header_key = "User-Agent"

blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])
container_client = blob_service_client.get_container_client(container="treks")
if not container_client.exists():
    container_client.create_container()

blobs = [b for b in container_client.list_blobs()]
blobs.sort(key=lambda x: x.name)
folders = list({blob.name.split("/")[0] for blob in blobs})
trek = folders[-1]
current_trek = [b for b in blobs if b.name.startswith(trek) and b.name.endswith(".txt") and not b.name.endswith("summary.txt")][-1]
trek_index = current_trek.name.split("/")[-1].split(".")[0]

@app.function_name(name="add")
@app.route(route="add")
def main(req):
    votes_blob = container_client.get_blob_client(trek + "/votes.json")
    if not votes_blob.exists():
        votes_blob.upload_blob("{\"options\":[]}")
    votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
    body = json.loads(req.get_body())
    if(body['option'] in [option['option'] for option in votes['options']]):
        return func.HttpResponse("Option already exists.", status_code=400)
    if(req.headers[header_key] in [option['created_by'] for option in votes['options']]):
        return func.HttpResponse("User already suggested an option.", status_code=400)
    votes['options'].append({"option": body['option'], "created_by": req.headers[header_key], "votes": []})
    votes_blob.upload_blob(json.dumps(votes), overwrite=True)
    return func.HttpResponse("OK")

@app.function_name(name="get")
@app.route(route="get")
def main(req):
    votes_blob = container_client.get_blob_client(trek + "/votes.json")
    if not votes_blob.exists():
        votes_blob.upload_blob("{\"options\":{}}")
    votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
    return func.HttpResponse(json.dumps([{"option": option["option"], "votes": len(option["votes"])} for option in votes['options']]),
        mimetype="application/json")

@app.function_name(name="vote")
@app.route(route="vote")
def main(req):
    votes_blob = container_client.get_blob_client(trek + "/votes.json")
    if not votes_blob.exists():
        votes_blob.upload_blob("{\"options\":[]}")
    votes = json.loads(container_client.download_blob(trek + "/votes.json").content_as_text())
    body = json.loads(req.get_body())
    if(body['option'] not in [option['option'] for option in votes['options']]):
        return func.HttpResponse("Option does not exist.", status_code=400)
    if(req.headers[header_key] in [user for v in [option['votes'] for option in votes['options']] for user in v]):
        return func.HttpResponse("User already voted.", status_code=400)
    for vote in votes['options']:
        if vote['option'] == body['option']:
            vote['votes'].append(req.headers[header_key])
    votes_blob.upload_blob(json.dumps(votes), overwrite=True)
    return func.HttpResponse("OK")

