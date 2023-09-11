import os
import openai

openai.organization = os.environ["OPEN_AI_ORGANIZATION"]
openai.api_key = os.environ["OPEN_AI_KEY"]


# Get latest prompts & votes from blob storage (or initial prompt)

# Calculate most popular latest prompt using votes

# Combine latest prompts with previous prompts into a single command

# Generate next section of the story

# Check if the story has reached a conclusion, if so end it

# Generate accompanying image

images = openai.Image.create(
    prompt="A cute baby sea otter",
    n=1,
    size="1024x1024"
)

# Download image and save to blob storage

print(images)