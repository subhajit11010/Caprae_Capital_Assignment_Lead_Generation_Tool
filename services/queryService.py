from services.llm_client import LLMClient
from post_extraction_tools.jsonparser import JSONOutputParser
from services.parametricSearch import ParametricSearch
from langchain.output_parsers import StructuredOutputParser # Import the parser
from data_models import CompanyList
import re
import json

class QService:
    def __init__(self, llm, industry_type: str, location: str, company_size: int, revenue_threshold: str, buisness_type: str):
        self.llm = llm
        self.parametric_search = ParametricSearch(self.llm)
        self.industry_type = industry_type
        self.location = location
        self.company_size = company_size
        self.revenue_threshold = revenue_threshold
        self.buisness_type = buisness_type

    def query(self):
        q = f"""
            Role: You are a business research assistant. Your task is to find companies based on specific criteria provided by the user using the tools that are given to you.
            Task: Find Companies in the {self.industry_type} industry, located in {self.location}, with a company size of more than or equal to {self.company_size} employees, and a revenue threshold of {self.revenue_threshold}. The companies should be of type {self.buisness_type}.
            Instructions:
            1. Use the scraper tools to gather information from company websites.
            2. Then extract:
                - Company Name
                - Industry Type
                - Location
                - Company Size
                - Street(if available)
                - City(if available)
                - State(if available)
                - Country(if available)
                - Phone
                - Email
                - Approx Revenue
                - Business Type (B2B or B2C or Both)
                - Website URL
            3. If any field is not available, leave it blank or use null.
            4. You *MUST* fill Approx revenue in the strict format of "(currency)X unit" like $100 million or $2 billion.
            5. You *MUST* fill Company Size in the strict *NUMBER* format like "1000", "2500" etc.
            6. After completing the search and extraction, you **MUST** provide your final output in the MRKL parser compatible format:
            a. **Start with a final Thought:** State that you have finished the search and are providing the results.
            b. **Use the Final Answer tag:** Enclose the extracted company data within the `Final Answer:` tag.
            c. **Format Data as JSON:** The content of the Final Answer **MUST** be a single JSON object (enclosed in ```json...```) with the exact structure:

                ```json
                {{
                "companies": [
                    {{
                    "company_name": "...",
                    "industry_type": "...",
                    "location": "...",
                    "company_size": "...",
                    "street": "...",
                    "city": "...",
                    "state": "...",
                    "country": "...",
                    "contact_info": "...",
                    "approx_revenue": "...",
                    "business_type": "...",
                    "website_url": "..."
                    }}
                ]
                }}
                ```
            7. You must return a minimum of 5 companies that meet the criteria. If you cannot find enough companies, return as many as you can.

            **YOUR FINAL OUTPUT MUST FOLLOW THIS STRUCTURE (INCLUDING THE THOUGHT AND FINAL ANSWER TAGS):**
    
            Thought: I have successfully gathered the required data. I will now output the final answer in the requested JSON format.
            Final Answer:
            ```json
            ... (Your JSON data here)
            ```
        """

        raw_company_data = self.parametric_search.agent.run(input=q, handle_parsing_errors=True)
        print(raw_company_data)
        structured_llm = self.llm.with_structured_output(CompanyList)
        print("😂😂😂😂😂")

        extraction_prompt = f"""
            You are a data cleaning expert. Your task is to extract the required fields from the raw text provided below and format it into a single JSON object.

            # Required Fields:
            - Company Name
            - Industry Type
            - Location
            - Company Size
            - Street
            - City
            - State
            - Country
            - Phone
            - Email
            - Approx Revenue
            - Business Type
            - Website URL

            # Raw Text Data:
            ---
            {raw_company_data}
            ---
        """
        final_chain = structured_llm.bind(format=CompanyList)
        final_response = final_chain.invoke(extraction_prompt)

        json_output = final_response.model_dump_json(indent=2)
        # filename = f"companies_{self.industry_type}_{self.location}.json".replace(" ", "_").lower()
        filename = "uncleaned_companies.json"
        try:
            with open(f"data/{filename}", 'w', encoding="utf-8") as f:
                f.write(json_output)
                print(f"Data successfully written to {filename}")
        except Exception as e:
            print(f"Error writing to file: {str(e)}")

        return final_response