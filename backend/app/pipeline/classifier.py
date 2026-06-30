import os
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from app.database import get_supabase_client

# Lazy-loaded CLIP resources to avoid importing time issues during startup
_model = None
_processor = None

def get_clip_model():
    global _model, _processor
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing CLIP Model on device: {device}")
        model_name = "openai/clip-vit-base-patch32"
        _model = CLIPModel.from_pretrained(model_name).to(device)
        _processor = CLIPProcessor.from_pretrained(model_name)
    return _model, _processor

def classify_and_upload(image_paths: list, query: str, job_id: str) -> list:
    """
    Classifies a list of image paths using CLIP and uploads them to Supabase Storage.
    
    image_paths: List of tuples (local_filepath, source_url)
    query: Target keyword for labelling
    job_id: ID of current scraper task
    
    Returns: List of dicts matching database column details.
    """
    model, processor = get_clip_model()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Construct distinct targets
    labels = [
        f"a photo of {query}",
        f"a screenshot, layout, or image completely unrelated to {query}"
    ]
    
    supabase = get_supabase_client()
    results = []
    
    for filepath, source_url in image_paths:
        if not os.path.exists(filepath):
            continue
            
        try:
            # 1. Run CLIP Evaluation
            image = Image.open(filepath).convert("RGB")
            inputs = processor(
                text=labels,
                images=image,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)
                idx = probs.argmax().item()
                confidence = probs[0][idx].item()
                
            is_relevant = (idx == 0)
            
            # 2. Upload asset to Supabase Storage ("datasets" bucket)
            filename = os.path.basename(filepath)
            subfolder = "relevant" if is_relevant else "noise"
            storage_path = f"jobs/{job_id}/{subfolder}/{filename}"
            
            content_type = "image/jpeg"
            if filename.lower().endswith(".webp"):
                content_type = "image/webp"
            elif filename.lower().endswith(".png"):
                content_type = "image/png"
                
            with open(filepath, "rb") as f:
                # Upload to Supabase bucket 'datasets'
                # Note: 'datasets' bucket must be configured as a PUBLIC bucket in Supabase UI
                supabase.storage.from_("datasets").upload(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": content_type}
                )
                
            # Retrieve generated public URL
            public_url = supabase.storage.from_("datasets").get_public_url(storage_path)
            
            results.append({
                "image_url": public_url,
                "is_relevant": is_relevant,
                "confidence": confidence
            })
            
            # Clean up local file after successful upload
            os.remove(filepath)
            
        except Exception as e:
            print(f"Error classifying/uploading image {filepath}: {e}")
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
                    
    return results
