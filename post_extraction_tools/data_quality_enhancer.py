import re
import json
import torch

key_industry_types = [
    "Information Technology & Services",
    "Software & SaaS",
    "Artificial Intelligence & Machine Learning",
    "Cybersecurity & Data Protection",
    "Cloud Computing & DevOps",
    "Telecommunications & Networking",
    "Semiconductors & Electronics",
    "Computer Hardware & Manufacturing",
    "Internet & Digital Media",
    "E-commerce & Retail",
    "Finance & Banking",
    "Insurance & Risk Management",
    "Investment & Asset Management",
    "Real Estate & Construction",
    "Architecture & Urban Planning",
    "Automotive & Transportation",
    "Aerospace & Defense",
    "Energy & Utilities",
    "Oil, Gas & Mining",
    "Renewable Energy & Sustainability",
    "Manufacturing & Industrial Engineering",
    "Logistics, Supply Chain & Warehousing",
    "Consumer Goods & FMCG",
    "Food & Beverages",
    "Agriculture & AgriTech",
    "Pharmaceuticals & Biotechnology",
    "Healthcare & Medical Devices",
    "Education & EdTech",
    "Media & Entertainment",
    "Sports & Recreation",
    "Travel, Tourism & Hospitality",
    "Legal Services & Law Firms",
    "Accounting & Financial Services",
    "Human Resources & Staffing",
    "Consulting & Business Services",
    "Marketing, Advertising & PR",
    "Design, Art & Creative Services",
    "Nonprofit & Social Impact",
    "Government & Public Administration",
    "Environmental Services",
    "Research & Development",
    "Mining & Metals",
    "Textiles, Apparel & Fashion",
    "Chemicals & Materials",
    "Marine & Shipping",
    "Utilities & Waste Management",
    "Printing & Publishing",
    "Electronics Repair & Maintenance",
    "Aviation & Airlines"
]

def enhancer(data: object, embedder) -> list:
    """
    Enhances the data quality by removing duplicates
    """
    # def tokenize(text):
    #     return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))
    
    companies = data.get("companies", [])
    num_of_companies = len(companies)
    duplicate_idx = set()
    duplicate_comps = []

    for i in range(num_of_companies):
        if i in duplicate_idx:
            continue

        c1 = companies[i]
        # name1 = tokenize(c1.get("company_name", ""))
        # ind1 = tokenize(c1.get("industry_type", ""))
        c1_name_embedding = embedder.encode([c1.get("company_name", "")])
        c1_ind_embedding = embedder.encode([c1.get("industry_type", "")])
        # c1["ind_embedding"] = c1_ind_embedding
        c1_country = c1.get("country", "").lower().strip()
        # print(name1, ind1, country1)

        for j in range(i+1, num_of_companies):
            if j in duplicate_idx:
                continue
            c2 = companies[j]
            c2_name_embedding = embedder.encode([c2.get("company_name", "")])
            c2_ind_embedding = embedder.encode([c2.get("industry_type", "")])
            # c2["ind_embedding"] = c2_ind_embedding
            c2_country = c2.get("country", "").lower().strip()

            name_sim = embedder.similarity(c1_name_embedding, c2_name_embedding).item()
            ind_sim = embedder.similarity(c1_ind_embedding, c2_ind_embedding).item()
            if name_sim >= 0.6 and ind_sim >= 0.6 and c1_country == c2_country:
                duplicate_idx.add(j)
                print(f"Duplicate found: {c1.get('company_name')} and {c2.get('company_name')}")
                print(f"Name similarity: {name_sim}, Industry similarity: {ind_sim}")

            # print(name2, ind2, country2)
        
            # name_intersection = len(name1 & name2)
            # industry_intersection = len(ind1 & ind2)

            # if (name_intersection >= max(len(name1), len(name2)) / 2 and
            #     industry_intersection >= max(len(ind1), len(ind2)) / 2 and
            #     country1 == country2):
                
            #     duplicate_idx.add(j)
            
    if duplicate_idx:
        print(duplicate_idx)
        duplicate_comps = [companies[i]["company_name"] for i in duplicate_idx]
        companies = [c for idx, c in enumerate(companies) if idx not in duplicate_idx]
        print(f"Removed {len(duplicate_idx)} duplicate entries.")
    else:
        print("No duplicate entries found.")
    
    print("Now adding the industry keys...")
    companies = add_ind_key(companies, embedder)
    print("Added Industry keys")

    return [{"companies": companies}, {"duplicate_company_names": duplicate_comps}]




def add_ind_key(data: list, embedder) -> list:
    with open("data/key_industry_embeddings.json", "r") as f:
        key_ind_embs = json.load(f)["industry_embeddings"]
    for c in data:
        if "key_industry" not in c:
            comp_emb = embedder.encode([c["industry_type"]])
            sim_t = embedder.similarity(key_ind_embs, comp_emb)
            max_sim_idx = torch.argmax(sim_t).item()
            c["key_industry"] = key_industry_types[max_sim_idx]

    return data
        

