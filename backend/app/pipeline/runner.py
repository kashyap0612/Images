import os
import shutil
import traceback
from app.database import get_supabase_client
from app.pipeline.search import search_google_links
from app.pipeline.downloader import get_page_html, extract_image_urls, download_images
from app.pipeline.classifier import classify_and_upload

def update_job_status(job_id: str, status: str, progress: int, total_images: int = 0):
    """Updates the state of the scraper job in Supabase database."""
    supabase = get_supabase_client()
    try:
        data = {
            "status": status,
            "progress": progress
        }
        # If successfully completed or failed, we report final relevant image counts
        if status == "completed" or total_images > 0:
            data["total_images"] = total_images
            
        supabase.table("jobs").update(data).eq("id", job_id).execute()
    except Exception as e:
        print(f"Database error updating status for job {job_id}: {e}")

def run_scraping_pipeline(job_id: str, query: str):
    """
    Executes the full pipeline in a single workflow:
    Google Search -> URL crawl -> image download -> CLIP classification -> Storage / DB upload.
    """
    temp_dir = f"temp_{job_id}"
    supabase = get_supabase_client()
    
    try:
        # Step 1: Extract links from Google
        update_job_status(job_id, "searching", 10)
        urls = search_google_links(query, limit=5)
        print(f"Extracted search result domains: {urls}")
        
        if not urls:
            update_job_status(job_id, "completed", 100, total_images=0)
            return
            
        # Step 2: Download raw images to temp directory
        update_job_status(job_id, "scraping", 30)
        all_downloaded_images = []
        
        for idx, url in enumerate(urls, start=1):
            progress_val = 30 + int((idx / len(urls)) * 30)
            update_job_status(job_id, f"scraping page {idx}/{len(urls)}", progress_val)
            
            html = get_page_html(url)
            image_urls = extract_image_urls(url, html)
            
            # Download max 15 candidate images per page to keep execution fast
            downloaded = download_images(image_urls, temp_dir, limit_per_run=15)
            all_downloaded_images.extend(downloaded)
            
        print(f"Downloaded total of {len(all_downloaded_images)} candidate images locally")
        
        if not all_downloaded_images:
            update_job_status(job_id, "completed", 100, total_images=0)
            return
            
        # Step 3: Local CLIP classification and Supabase Storage uploads
        update_job_status(job_id, "classifying", 70)
        curated_results = classify_and_upload(all_downloaded_images, query, job_id)
        
        # Step 4: Write curated results to DB
        update_job_status(job_id, "saving", 90)
        db_records = []
        relevant_count = 0
        
        for item in curated_results:
            db_records.append({
                "job_id": job_id,
                "image_url": item["image_url"],
                "is_relevant": item["is_relevant"],
                "confidence": item["confidence"]
            })
            if item["is_relevant"]:
                relevant_count += 1
                
        if db_records:
            supabase.table("dataset_images").insert(db_records).execute()
            
        # Complete
        update_job_status(job_id, "completed", 100, total_images=relevant_count)
        print(f"Pipeline job completed. Labeled {relevant_count} true positives.")
        
    except Exception as e:
        print(f"Critical execution failure in job {job_id}: {e}")
        traceback.print_exc()
        update_job_status(job_id, "failed", 100)
        
    finally:
        # Guarantee cleanup of temporary folder from disk
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Failed to clear temp directory {temp_dir}: {e}")
