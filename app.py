import streamlit as st
from services.queryService import QService
from services.llm_client import LLMClient
from sentence_transformers import SentenceTransformer
from post_extraction_tools import (
    website_adder,
    clean_json,
    lead_scoring,
    data_quality_enhancer,
    chart_data
)
from services.add_leads import add_leads_f
import json
import pandas as pd

# INITIALIZATION
llm = LLMClient().client


@st.cache_resource
def load_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


embedder = load_model()
lead_scorer = lead_scoring.LeadScoring(llm, embedder)

st.set_page_config(page_title="Caprae Capital Lead Generation Tool", layout="wide")
# st.title("Lead Management Dashboard")
# This is the navigation section
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# I defined these in order to prevent repetitive use of LLMs
if "pipeline_executed" not in st.session_state:
    st.session_state.pipeline_executed = False
if "data_enhancement" not in st.session_state:
    st.session_state.data_enhancement = False
if "intelliscore" not in st.session_state:
    st.session_state.intelliscore = False
if "lead_conditions" not in st.session_state:
    st.session_state.lead_conditions = False
if "ask_for_scrap_per" not in st.session_state:
    st.session_state.ask_scrap_per = False

with st.sidebar:
    for page_name in [
        "Dashboard",
        "Enrich Companies",
        "Enhance Data Quality",
        "IntelliSCORE",
        "Settings",
        "Profile",
    ]:
        if st.button(page_name, use_container_width=True):
            st.session_state.page = page_name

if st.session_state.page == "Dashboard":
    st.header("Welcome!!")
    st.text("Here you will find all about your leads.")
    if st.session_state.data_enhancement == True:

        fig_ind, fig_coun, fig_btype, fig_rev = chart_data.create_chart("data/all_cleaned_companies.json")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Industry-wise Distribution")
            st.plotly_chart(fig_ind, use_container_width=True)

        with col2:
            st.subheader("Country-wise Distribution")
            st.plotly_chart(fig_coun, use_container_width=True)

        with col3:
            st.subheader("Business type-wise Distribution")
            st.plotly_chart(fig_btype, use_container_width=True)
        
        st.subheader("Revenue-based Distribution")
        st.plotly_chart(fig_rev, use_container_width=True)
    df_display = chart_data.df_creator_from_json_and_process("data/all_cleaned_companies.json").sort_values(by="score", ascending=False).rename(columns={
        "company_name": "Company Name",
        "key_industry": "Industry Type",
        "industry_type": "Speciality",
        "street": "Street",
        "city": "City",
        "state": "State",
        "country": "Country",
        "phone": "Phone",
        "email": "Email",
        "company_size": "Number of Employees",
        "approx_revenue": "Revenue",
        "business_type": "Business Type",
        "website_url": "Website",
        "country": "Country"
    })
    st.subheader("All Company Details")
    st.dataframe(df_display)


if st.session_state.page == "Enrich Companies":
    tab1, tab2 = st.tabs(["Manual Entry", "Intelligent Enrichment"])
    with tab1:
        st.subheader("Enter leads info")
        with st.container(border=True):
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                lead_name = st.text_input("Company Name")
                lead_size = st.number_input(
                    "Number of Employees(whole number)", placeholder="e.g. 1000", key=0
                )
                lead_city = st.text_input("Company City")
                lead_country = st.text_input("Company Country")
                lead_email = st.text_input("Company Email")
                lead_business_type = st.text_input(
                    "Company Business Type", placeholder="B2B/B2C/Both"
                )
            with col2:
                lead_industry_type = st.text_input("Company Industry Type")
                lead_street = st.text_input("Company Street Location")
                lead_state = st.text_input("Company State")
                lead_phone = st.text_input(
                    "Company Phone", placeholder="e.g. (312) 593-3600"
                )
                lead_revenue = st.text_input(
                    "Company Revenue", placeholder="e.g. $340.2 million"
                )
                lead_web_url = st.text_input(
                    "Company Official Website URL",
                    placeholder="e.g. https://www.xyz.com",
                )

            col3, col4, col5 = st.columns([1, 1, 1])
            with col4:
                manual_entry_button = st.button(
                    "Submit",
                    use_container_width=True,
                    type="primary",
                    key="manual_entry_b",
                )
                if manual_entry_button:
                    if not (st.session_state.data_enhancement and st.session_state.intelliscore):
                        st.warning("Complete the Data Enhancement and Intelliscore Lead Scoring first!!")
                        pass
                    else:
                        lead_data = {
                            "company_name": lead_name,
                            "industry_type": lead_industry_type,
                            "location": f"{lead_city}, {lead_state}, {lead_country}",
                            "company_size": str(lead_size),
                            "street": lead_street,
                            "city": lead_city,
                            "state": lead_state,
                            "country": lead_country,
                            "phone": lead_phone,
                            "email": lead_email,
                            "approx_revenue": lead_revenue,
                            "business_type": lead_business_type,
                            "website_url": lead_web_url,
                        }
                        lead_data = {"companies": [lead_data]}
                        cleaned_data = clean_json.clean_json_f(lead_data)
                        cleaned_data_obj = json.loads(cleaned_data)
                        cleaned_data_obj = add_leads_f(
                            "data/all_cleaned_companies.json", cleaned_data_obj
                        )
                        with open("data/all_cleaned_companies.json", "w") as f:
                            json.dump(cleaned_data_obj, f, indent=2)

                        print("Cleaned JSON saved to all_cleaned_companies.json")
                        print("Now enriching the data with website URLs...")

                        companies = cleaned_data_obj.get("companies", [])
                        intermediate_data = website_adder.find_all_company_websites(
                            companies
                        )
                        final_data = website_adder.wiki_search_mode(intermediate_data)
                        print("Website URL enrichment completed.")
                        st.session_state.pipeline_executed = False
                        st.session_state.data_enhancement = False
                        st.session_state.intelliscore = False
                        st.session_state.lead_conditions = False
                    

    with tab2:
        st.subheader("Advanced Intelligent Scrapper and Data Completion")
        st.text(
            "Just enter the key details of the leads you wanna search for as well as few data of your company and SEE THE MAGIC!!"
        )
        with st.container(border=True):
            st.subheader("Lead Info")
            col6, col7 = st.columns([0.5, 0.5])
            with col6:
                lead_industry_type = st.text_input("Industry Type of Lead")
                lead_location = st.text_input("Location of the Lead")
                lead_size = st.number_input(
                    "Number of Employees (whole number)",
                    placeholder="e.g. 1000",
                    key=1,
                    step=1,
                    value=0,
                )
            with col7:
                lead_revenue = st.text_input(
                    "Revenue Threshold of Lead", placeholder="e.g. $340.2 million"
                )
                lead_business_type = st.text_input(
                    "Lead Business Type (B2B/B2C/Both)", placeholder="B2B/B2C/Both"
                )

            st.subheader("Your Company Info")
            col8, col9 = st.columns([0.5, 0.5])
            with col8:
                own_comp_info = st.text_area(
                    "Write some of the key points about your company (Optional)"
                )
            with col9:
                own_comp_web_url = st.text_input(
                    "Your Company's Official Web URL",
                    placeholder="e.g. https://www.xyz.com",
                )

            col10, col11, col12 = st.columns([1, 1, 1])
            with col11:
                intelli_enrich_button = st.button(
                    "Submit",
                    use_container_width=True,
                    type="primary",
                    key="intelli_entry_b",
                )
                if intelli_enrich_button:
                    qservice = QService(
                        llm,
                        lead_industry_type,
                        lead_location,
                        int(lead_size),
                        lead_revenue,
                        lead_business_type,
                    )
                    response = qservice.query()
                    print(response)
                    print("Initial extraction is done. Now cleaning the JSON...")
                    with open("data/uncleaned_companies.json", "r") as f:
                        data = json.load(f)

                    cleaned_data = clean_json.clean_json_f(data)
                    cleaned_data_obj = json.loads(cleaned_data)
                    cleaned_data_obj = add_leads_f(
                        "data/all_cleaned_companies.json", cleaned_data_obj
                    )
                    with open("data/all_cleaned_companies.json", "w") as f:
                        json.dump(cleaned_data_obj, f, indent=2)

                    print("Cleaned JSON saved to all_cleaned_companies.json")
                    print("Now enriching the data with website URLs...")

                    companies = cleaned_data_obj.get("companies", [])
                    intermediate_data = website_adder.find_all_company_websites(
                        companies
                    )
                    final_data = website_adder.wiki_search_mode(intermediate_data)
                    print("Website URL enrichment completed.")

                    print("Now enhancing the data quality by removing duplicates...")
                    enhanced_data = data_quality_enhancer.enhancer(
                        final_data, embedder
                    )[0]

                    with open("data/all_cleaned_companies.json", "w") as f:
                        json.dump(enhanced_data, f, indent=2)

                    print(
                        "Data quality enhancement completed. Cleaned data saved to all_cleaned_companies.json"
                    )
                    print(
                        "Now scoring the leads based on relevance (Intelligent scoring)..."
                    )

                    res = lead_scorer.scrape_and_augment(
                        own_comp_info, own_comp_web_url
                    )
                    with open("data/lead_conditions.json", "w") as f:
                        json.dump(res, f, indent=2)

                    scored_leads = lead_scorer.score(enhanced_data, res)
                    print("Lead scoring completed. Here are the scored leads:")
                    print(scored_leads)
                    st.session_state.pipeline_executed = True
                    st.session_state.data_enhancement = True
                    st.session_state.intelliscore = True
                    st.session_state.lead_conditions = True


if st.session_state.page == "Enhance Data Quality":
    st.subheader("Enhance Data Quality By Removing Duplicates and noise")
    st.text("This tool uses embedding model to ensure clean and reliable data quality.")
    with st.container(border=True):
        st.subheader("Your Current Data")
        with open("data/all_cleaned_companies.json", "r") as f:
            temp_data = json.load(f)
        temp_df = pd.DataFrame(temp_data.get("companies", []))
        st.dataframe(temp_df)
        col13, col14, col15 = st.columns([1, 1, 1])
        with col14:
            enhance_data_b = st.button(
                "Enhance Data", type="primary", use_container_width=True
            )
            if enhance_data_b and st.session_state.data_enhancement == False and st.session_state.pipeline_executed == False:
                with st.spinner("Enhancing the data..."):
                    enhancer_output = data_quality_enhancer.enhancer(
                        temp_data, embedder
                    )
                    enhanced_data, duplicate_comps = (
                        enhancer_output[0],
                        enhancer_output[1]["duplicate_company_names"],
                    )
                    st.success("Enhancement Completed!!")

                with open("data/all_cleaned_companies.json", "w") as f:
                    json.dump(enhanced_data, f, indent=2)
                if duplicate_comps == []:
                    st.text("No Duplicate Entries Found!!")
                else:
                    st.text(f"Removed {len(duplicate_comps)} duplicate companies!!")
                    st.text("Removed Companies: ")
                    for c in duplicate_comps:
                        st.text(c)
                st.session_state.data_enhancement = True

            elif enhance_data_b and st.session_state.data_enhancement == True:
                st.text("Already Enhanced!!")

if st.session_state.page == "IntelliSCORE":
    st.subheader("Advanced Lead Scoring Tool")
    st.text("This tools uses llm under the hood to generates reliable scores!!")
    with st.container(border=True):
        st.subheader("Enter Below Details")
        col16, col17 = st.columns([0.5, 0.5])
        with col16:
            additional_info = st.text_area(
                "Additional Info About Your Company",
                placeholder="additional informations...",
            )
        with col17:
            comp_url = st.text_input(
                "Your Company's Official Website URL",
                placeholder="e.g. https://www.xyz.com",
            )
            if st.session_state.lead_conditions == True:
                ask_scrap_per = st.radio(
                    "Your company url is already scrapped. Do you want to scrap again? (yes/no)",
                    options=["yes", "no"],
                    key="scrape_permission",
                )
                st.session_state.ask_scrap_per = ask_scrap_per
            else:
                ask_scrap_per = None
        col18, col19, col20 = st.columns([1, 1, 1])
        with col19:
            intelliscore_b = st.button(
                "Score Leads", use_container_width=True, type="primary"
            )
            if intelliscore_b:
                if st.session_state.data_enhancement == True:
                    with open("data/all_cleaned_companies.json", "r") as f:
                        leads = json.load(f)

                    if ask_scrap_per == "yes" or ask_scrap_per == None:
                        with st.spinner("Scraping the website..."):
                            res = lead_scorer.scrape_and_augment(
                                additional_info, comp_url
                            )
                            with open("data/lead_conditions.json", "w") as f:
                                json.dump(res, f, indent=2)
                            st.success("Scrapping Completed!")
                            if res and "error" not in res:
                                st.session_state.lead_conditions = True

                        with open("data/lead_conditions.json", "r") as f:
                            lead_cond = json.load(f)
                        with st.spinner("Scoring the leads..."):
                            scored_leads = lead_scorer.score(leads, lead_cond)
                            st.success("Scoring Completed!")

                        st.text("See Dashboard for latest scored leads!!")
                        st.session_state.intelliscore = True

                    else:
                        st.text("Skipping url scrapping...")
                        with open("data/lead_conditions.json", "r") as f:
                            lead_cond = json.load(f)
                        with st.spinner("Scoring the leads..."):
                            scored_leads = lead_scorer.score(leads, lead_cond)
                            st.success("Scoring Completed!")

                        st.text("See Dashboard for latest scored leads!!")
                        st.session_state.intelliscore = True

                else:
                    st.warning("Complete the Data Enhancement first!!")