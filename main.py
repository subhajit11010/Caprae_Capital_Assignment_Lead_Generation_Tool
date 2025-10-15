from services.queryService import QService
from services.llm_client import LLMClient
from sentence_transformers import SentenceTransformer
from post_extraction_tools import website_adder, clean_json, lead_scoring, data_quality_enhancer
from services.add_leads import add_leads_f
import json

llm = LLMClient().client
def load_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embedder = load_model()
qservice = QService(llm, "Software Development", "Chickago", 100, "$10 million", "B2B")
lead_scorer = lead_scoring.LeadScoring(llm, embedder)
response = qservice.query()
print(response)
print("Initial extraction is done. Now cleaning the JSON...")
with open("data/uncleaned_companies.json", "r") as f:
    data = json.load(f)
cleaned_data = clean_json.clean_json_f(data)
cleaned_data_obj = json.loads(cleaned_data)

cleaned_data_obj = add_leads_f("data/all_cleaned_companies.json", cleaned_data_obj)

with open("data/all_cleaned_companies.json", "w") as f:
    json.dump(cleaned_data_obj, f, indent=2)

print("Cleaned JSON saved to all_cleaned_companies.json")
print("Now enriching the data with website URLs...")

companies = cleaned_data_obj.get("companies", [])
intermediate_data = website_adder.find_all_company_websites(companies)
final_data = website_adder.wiki_search_mode(intermediate_data)
print("Website URL enrichment completed.")

print("Now enhancing the data quality by removing duplicates...")
enhanced_data = data_quality_enhancer.enhancer(final_data, embedder)[0]

with open("data/all_cleaned_companies.json", "w") as f:
    json.dump(enhanced_data, f, indent=2)

print("Data quality enhancement completed. Cleaned data saved to all_cleaned_companies.json")

print("Now scoring the leads based on relevance (Intelligent scoring)...")
with open("data/all_cleaned_companies.json", "r") as f:
    leads = json.load(f)

res = lead_scorer.scrape_and_augment("IBM (International Business Machines Corporation) is a global leader in hybrid cloud, AI, and enterprise consulting, helping businesses transform with innovative technology and deep industry expertise. With a workforce of over 260,000 employees worldwide and a legacy of over a century, IBM partners with organizations of all sizes to drive digital reinvention and sustainable growth. In 2024, IBM reported annual revenue of $61.9 billion, underlining its commitment to delivering cutting-edge solutions in AI, quantum computing, and IT infrastructure. Headquartered in Armonk, New York, IBM operates in more than 170 countries, empowering clients to navigate the complexities of the modern digital landscape. IBM is actively seeking strategic partnerships with forward-thinking AI companies to co-create next-generation solutions and accelerate innovation.", "https://www.ibm.com/in-en")

with open("data/lead_conditions.json", "w") as f:
    json.dump(res, f, indent=2)

scored_leads = lead_scorer.score(leads, res)
print("Lead scoring completed. Here are the scored leads:")
print(scored_leads)

