import os
import json

def add_leads_f(file_path: str, new_leads: object) -> object:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        new_leads_arr = new_leads["companies"]
        with open(file_path, "r") as f:
            existing_leads_arr = json.load(f).get("companies", [])
        augmented_leads_arr = existing_leads_arr + new_leads_arr
        return {"companies": augmented_leads_arr}
    else:
        return new_leads