from pydantic import BaseModel, Field
from typing import List, Optional

class CompanyData(BaseModel):
    """Schema for a single company's extracted data."""
    company_name: str = Field(description="The full legal name of the company.")
    industry_type: str = Field(description="The primary industry the company operates in.")
    location: str = Field(description="The city and state where the company is located.")
    company_size: Optional[str] = Field(description="The approximate number of employees (e.g., '100+' or '500-1000').")
    street: Optional[str] = Field(description="Street address (if available).")
    city: Optional[str] = Field(description="City (if available).")
    state: Optional[str] = Field(description="State or province (if available).")  
    country: Optional[str] = Field(description="Country (if available).")
    phone: Optional[str] = Field(description="Primary phone number (if available).")
    email: Optional[str] = Field(description="Primary email address (if available).")
    approx_revenue: Optional[str] = Field(description="The approximate annual revenue (e.g., '$15 million').")
    business_type: str = Field(description="B2B, B2C, or Both.")
    website_url: str = Field(description="The URL of the company's official website.")

class CompanyList(BaseModel):
    """The final, clean JSON list containing all found companies."""
    companies: List[CompanyData]