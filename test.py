from sentence_transformers import SentenceTransformer
import json

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
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

source_sentence = "Software Development"
sentence_embeddings = model.encode(sentences)
source_embedding = model.encode([source_sentence])

similarities = model.similarity(sentence_embeddings, source_embedding)
print(similarities)
# print(embeddings_list)
# with open("data/key_industry_embeddings.json", "w") as f:
#     json.dump({"company_embeddings": embeddings_list}, f, indent=2)
# [4, 4]