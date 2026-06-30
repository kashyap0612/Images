import os
import shutil
from pathlib import Path

import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel
import sys

query = sys.argv[1]
subquery = query.replace(" ", "_")

# ----------------------------
# Configuration
# ----------------------------



IMAGE_FOLDER = subquery
OUTPUT_FOLDER = "output"

LABELS = [
    f"a photo of {query}",
    f"a photo not a {query}",
]

MODEL_NAME = "openai/clip-vit-base-patch32"

# ----------------------------
# Load Model
# ----------------------------

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading CLIP...")

model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)

# Create output folders
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for label in LABELS:
    folder = os.path.join(OUTPUT_FOLDER, label.replace(" ", "_"))
    os.makedirs(folder, exist_ok=True)

# ----------------------------
# Supported image formats
# ----------------------------

extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)

images = [
    p for p in Path(IMAGE_FOLDER).iterdir()
    if p.suffix.lower() in extensions
]

print(f"Found {len(images)} images\n")

# ----------------------------
# Process Images
# ----------------------------

for image_path in tqdm(images):

    try:

        image = Image.open(image_path).convert("RGB")

        inputs = processor(
            text=LABELS,
            images=image,
            return_tensors="pt",
            padding=True
        )

        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():

            outputs = model(**inputs)

            probs = outputs.logits_per_image.softmax(dim=1)

            idx = probs.argmax().item()

            predicted_label = LABELS[idx]

            confidence = probs[0][idx].item()

        destination = os.path.join(
            OUTPUT_FOLDER,
            predicted_label.replace(" ", "_"),
            image_path.name
        )

        shutil.copy(image_path, destination)

        print(
            f"{image_path.name:25} -> "
            f"{predicted_label:15} "
            f"{confidence:.3f}"
        )

    except Exception as e:

        print(image_path.name, e)

print("\nFinished!")
