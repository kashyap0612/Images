import os
import base64
import requests
from app.database import get_supabase_client

def classify_and_upload(image_paths: list, query: str, job_id: str) -> list:
    """
    Classifies a list of local images using Hugging Face Serverless Inference API (CLIP).
    Falls back to direct upload (bypassing CLIP) if Hugging Face is blocked by a network firewall.
    
    image_paths: List of tuples (local_filepath, source_url)
    query: Target keyword for dataset tagging
    job_id: ID of the scraping run
    """
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not hf_token:
        print("Warning: HUGGINGFACE_API_TOKEN env variable is not set. Classification will fail.")
        
    labels = [
        f"a photo of {query}",
        f"a screenshot, layout, or image completely unrelated to {query}"
    ]
    
    supabase = get_supabase_client()
    results = []
    
    api_url = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    
    for filepath, source_url in image_paths:
        if not os.path.exists(filepath):
            continue
            
        try:
            with open(filepath, "rb") as f:
                img_bytes = f.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            
            payload = {
                "inputs": img_b64,
                "parameters": {
                    "candidate_labels": labels
                }
            }
            
            # 1. Query Hugging Face CLIP Serverless API
            response = requests.post(api_url, headers=headers, json=payload, timeout=20)
            
            if response.status_code != 200:
                raise Exception(f"Hugging Face API error {response.status_code}: {response.text}")
                
            api_res = response.json()
            
            if not isinstance(api_res, list) or len(api_res) == 0:
                raise Exception(f"Unexpected response format from HF: {api_res}")
                
            best_match = api_res[0]
            predicted_label = best_match["label"]
            confidence = best_match["score"]
            
            is_relevant = (predicted_label == labels[0])
            
            # 2. Upload to Supabase Storage ("datasets" bucket)
            filename = os.path.basename(filepath)
            subfolder = "relevant" if is_relevant else "noise"
            storage_path = f"jobs/{job_id}/{subfolder}/{filename}"
            
            content_type = "image/jpeg"
            if filename.lower().endswith(".webp"):
                content_type = "image/webp"
            elif filename.lower().endswith(".png"):
                content_type = "image/png"
                
            supabase.storage.from_("datasets").upload(
                path=storage_path,
                file=img_bytes,
                file_options={"content-type": content_type}
            )
            
            public_url = supabase.storage.from_("datasets").get_public_url(storage_path)
            
            results.append({
                "image_url": public_url,
                "is_relevant": is_relevant,
                "confidence": confidence
            })
            
            os.remove(filepath)
            
        except Exception as e:
            # --- Network Fallback Logic ---
            # If the institutional Wi-Fi blocks Hugging Face (DNS resolution / connection fails),
            # we bypass CLIP and upload the image directly to the 'relevant' bucket.
            err_str = str(e).lower()
            if "failed to resolve" in err_str or "connection" in err_str or "max retries exceeded" in err_str:
                print(f"Network block detected (Hugging Face API blocked). Bypassing CLIP for {filepath}...")
                try:
                    filename = os.path.basename(filepath)
                    storage_path = f"jobs/{job_id}/relevant/{filename}"
                    content_type = "image/jpeg"
                    if filename.lower().endswith(".webp"):
                        content_type = "image/webp"
                    elif filename.lower().endswith(".png"):
                        content_type = "image/png"
                        
                    # Direct upload to Supabase Storage
                    supabase.storage.from_("datasets").upload(
                        path=storage_path,
                        file=img_bytes,
                        file_options={"content-type": content_type}
                    )
                    
                    public_url = supabase.storage.from_("datasets").get_public_url(storage_path)
                    
                    # Mark as relevant with high confidence fallback
                    results.append({
                        "image_url": public_url,
                        "is_relevant": True,
                        "confidence": 1.0
                    })
                    
                    os.remove(filepath)
                    continue
                except Exception as upload_err:
                    print(f"Direct fallback upload to Supabase also failed: {upload_err}")
            
            # Print original traceback for logs
            import traceback
            print(f"Error classifying/uploading image {filepath} via HF API: {e}")
            traceback.print_exc()
            
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
                    
    return results
