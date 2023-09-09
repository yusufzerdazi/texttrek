import os
import openai

openai.organization = os.environ["OPEN_AI_ORGANIZATION"]
openai.api_key = os.environ["OPEN_AI_KEY"]

images = openai.Image.create(
    prompt="A cute baby sea otter",
    n=2,
    size="1024x1024"
)

print(images)