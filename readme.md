# <p align="center"> Caprae Capital Lead Generation Tool</p>
## <p align="center">About</p>
This tool is intended to generate potential leads based on lead parameters and some of the generator's info. It leverages advanced tools like intelliegent scraping and extraction which on the other hand, implements embedder model (all-MiniLM-L6-v2) and gemini-2.5-flash internally to given precise and reliable lead informations. This tools also implements IntelliSCORE which is a custom-built advanced lead scoring tool which automatically generate accurate scores by comparing generator data and lead's data. If you click <b>Intelligent Enrichment</b> option in the <b>Enrich</b> tool, it will automatically do all of the tool's tasks so that you don't have to manually implement the post-extraction tools.
## <p align="center">Features</p>
<h3>This Tool leverages a __ stage data pipeline in a single process.</h3>
1. Data Cleaning (Removing Noise and parsing data in proper format).
2. Website URL enrichment(If required)
3. Data enhancement by removing duplicates and handling None/NaN type data
4. Lead scoring using custom-built IntelliSCORE microservice

