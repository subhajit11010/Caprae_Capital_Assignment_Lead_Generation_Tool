import json

def clean_json_f(input_json: object) -> str:
    """
    Cleans and formats the input JSON string to ensure it adheres to the expected schema.
    
    Args:
        input_json (str): The raw JSON object to be cleaned.
    Returns:
        str: A cleaned and formatted JSON string.
    """
    try:
        data = input_json
        
        # Ensure 'companies' key exists and is a list
        if "companies" not in data or not isinstance(data["companies"], list):
            return json.dumps({"companies": []}, indent=2)
        
        cleaned_companies = []
        for company in data["companies"]:
            cleaned_company = {
                "company_name": company.get("company_name", "").strip(),
                "industry_type": company.get("industry_type", "").strip(),
                "location": company.get("location", "").strip(),
                "company_size": company.get("company_size", "").strip() if company.get("company_size") else None,
                "street": company.get("street", "").strip() if company.get("street") else None,
                "city": company.get("city", "").strip() if company.get("city") else None,
                "state": company.get("state", "").strip() if company.get("state") else None,
                "country": company.get("country", "").strip() if company.get("country") else None,
                "phone": company.get("phone", "").strip() if company.get("phone") else None,
                "email": company.get("email", "").strip() if company.get("email") else None,
                "approx_revenue": company.get("approx_revenue", "").strip() if company.get("approx_revenue") else None,
                "business_type": company.get("business_type", "").strip(),
                "website_url": company.get("website_url", "").strip()
            }
            cleaned_companies.append(cleaned_company)
        
        cleaned_data = {"companies": cleaned_companies}
        return json.dumps(cleaned_data, indent=2)
    
    except json.JSONDecodeError:
        return json.dumps({"companies": []}, indent=2)