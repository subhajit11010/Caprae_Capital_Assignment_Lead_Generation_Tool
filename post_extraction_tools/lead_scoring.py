import os
from services.llm_client import LLMClient
# from sentence_transformers import SentenceTransformer
from services.scraper import scrape_website
import json
import requests
from post_extraction_tools.jsonparser import JSONOutputParser

class LeadScoring:
    def __init__(self, llm, embedder):
        self.llm = llm
        self.parser = JSONOutputParser()
        # self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.embedder = embedder

    def augment_query(self, additional_info: str, page_data: str):
        augmented_query = f"""
                additional_info: {additional_info}
                page data: {page_data}
                **Task**: You are an expert buisness analyst. A company wants to create it's lead scoring conditions from it's page data and additional_info. Your task is to create conditions for the fields in the *Structure* from the company page data and the additional_info to score a lead. But you will not directly score any lead. You will only create the conditions for scoring the lead.
                **Structure**: 
                {{
                    "industry_type": "...",
                    "company_size": "...",
                    "street": "...",
                    "city": "...",
                    "state": "...",
                    "country": "...",
                    "approx_revenue": "...",  
                    "business_type": "..."
                }}

                **Instructions**:
                1. You must *Analyze* the page data and the additional_info to determine the **CONDITIONS** for each field in the *Structure*. You have to give the conditions such that if a lead meets those conditions, it can be considered a good lead for the company.
                2. Don't just copy the values from the page data or additional_info. You have to determine the best possible conditions only for the fields: "industry_type", "company_size", "approx_revenue", "business_type" based on the page data and additional_info. For the fields: "street", "city", "state", "country", see the instruction number 6 below.
                3. If you encounter any field in the *Structure* that is not present in the page data as well as the additional_info, assign it null or empty string.
                4. *Business_type* can only be among B2B or B2C or Both. You have to determine the best possible condition for the field "business_type" based on the page data and additional_info.
                5. If additional_info are empty, you have to create the conditions solely based on the page data.
                6. If parts of additional_info are contradictory to the page data, prioritize the page data and ignore that contradictory part of the additional_info.
                7. If the location of the company is given anywhere, then you have to break it down into street, city, state and country. If any part is missing, assign it null or empty string and fill up the corresponding field in the *Structure*. 
                8. You *MUST* fill Approx revenue in the strict format of "(currency)X unit" like $100 million or $2 billion. Absolutely **DO NOT WRITE AS 'greater than $100 million'. JUST WRITE IN THE GIVEN FORMAT IN THE INSTRUCTION.
                9. You *MUST* fill Company_size in the strict *NUMBER* format like 1000, 2500 etc. Absolutely **DO NOT WRITE AS 'greater than 1000 employees'. JUST WRITE IN THE GIVEN *NUMBER* FORMAT.  
                10. Ensure that the conditions are specific and relevant to the company's target audience and business goals.
                11. You **MUST** respond only in JSON format as below:
                    ```json
                    {{
                        "industry_type": "...",
                        "company_size": "...",
                        "street": "...",
                        "city": "...",
                        "state": "...",
                        "country": "...",
                        "approx_revenue": "...",  
                        "business_type": "..."
                    }}
                    ```
                12. You **MUST** not include any additional information or explanations in the output. Only provide the JSON object.
                """
        return augmented_query
    
    def scrape_and_augment(self, additional_info: str, url: str):
        page_data = scrape_website(url)
        if page_data.startswith("Error scraping the URL") or page_data == "" or page_data is None:
            return {"error": page_data}
        augmented_query = self.augment_query(additional_info, page_data)
        res = self.llm.invoke([augmented_query])
        # print(res.content, type(res.content))
        parsed_res = self.parser.parse(res.content)
        return parsed_res

    def score(self, leads: object, conditions: object):
        # scored_leads = []
        for lead in leads["companies"]:
            if "score" not in lead:
                score = 0
                if "industry_type" in conditions:
                    try: 
                        lead_industry_embedding = self.embedder.encode([lead.get("industry_type", '')])
                        company_industry_embedding = self.embedder.encode([conditions["industry_type"]])
                        sim = self.embedder.similarity(lead_industry_embedding, company_industry_embedding).item()
                        score += round(sim, 2)
                        # print(score)
                    except Exception as e:
                        # print(f"1. error occured: {str(e)}")
                        pass

                if "company_size" in conditions:
                    try:
                        if int(lead.get('company_size', 0)) >= int(conditions['company_size']):
                            score += 1.0
                    except Exception:
                        # print("2. error occured")
                        pass

                if "approx_revenue" in conditions: # This measures lead weight in terms of revenue
                    try:
                        lead_revenue = lead.get('approx_revenue', '').replace('$', '').replace(' million', '').replace(' billion', '')
                        condition_revenue = conditions['approx_revenue'].replace('$', '').replace(' million', '').replace(' billion', '')
                        if float(lead_revenue) >= float(condition_revenue):
                            score += 1.0
                            # print(score)
                    except Exception:
                        # print("3. error occured")
                        pass

                if "business_type" in conditions:
                    try:
                        if lead.get('business_type', '').lower() == conditions['business_type'].lower() or conditions['business_type'].lower() == 'both':
                            score += 1.0
                    except Exception:
                        # print("4. error occured")
                        pass
                
                lead['score'] = score
                # scored_leads.append(lead)
                root_dir = os.path.dirname(os.path.abspath(__file__))
                data_folder = os.path.join(root_dir, "..", "data")
                os.makedirs(data_folder, exist_ok=True)

                file_path = os.path.join(data_folder, "all_cleaned_companies.json")

                with open(file_path, "w") as f:
                    json.dump(leads, f, indent=2)

        return leads

# llm = LLMClient().client
# leadscoring = LeadScoring(llm)
# res = leadscoring.scrape_and_augment("We are looking for partnerships with AI companies. our company size is 3700 . We are located at 1455 3rd St, San Francisco, CA 94158, United States. We were approximately $4.3 billion in revenue for the first half of 2025 and are targeting $13 billion in total revenue for the full year", "https://openai.com")

# with open("data/cleaned_companies.json", "r") as f:
#     leads = json.load(f)

# scored_leads = leadscoring.score(leads, res)
# print(scored_leads)
    


    
