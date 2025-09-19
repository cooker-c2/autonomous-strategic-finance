import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from dotenv import load_dotenv
import pandas as pd

# The necessary import from your models file
from .models import ForecastRequest

load_dotenv()

# Define constants for financial metrics
REVENUE_PER_LARGE_CUSTOMER = 16500
REVENUE_PER_SMB_CUSTOMER = 500
SALESPEOPLE_TO_LARGE_CUSTOMER_RATIO = 1.5
NEW_SMB_CUSTOMERS_PER_MONTH = (30000 / 1500) * 0.45
INITIAL_LARGE_CUSTOMERS = 5
INITIAL_SALESPEOPLE = 2

class KnowledgeBaseError(Exception):
    """Custom exception for when the knowledge base file is missing."""
    pass

def get_llm():
    """Safely initialize LLM with error handling"""
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=os.getenv('GOOGLE_API_KEY')  # Explicit API key
        )
    except Exception as e:
        print(f"Google Gemini failed in logic_engine: {e}")
        # Fallback to simple logic without LLM
        return None

def read_knowledge_base(file_path="knowledge_base.txt"):
    """Reads the knowledge base file into a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise KnowledgeBaseError(f"Error: knowledge_base.txt not found at {file_path}")

# CHANGE 1: This function is now asynchronous, using `async def`.
async def generate_forecast(request: ForecastRequest, llm: ChatGoogleGenerativeAI):
    """
    Generates a financial forecast based on a structured request.
    """
    print(f"Processing query: {request.query}")
    
    # CHANGE 2: The call to this function now uses `await` because it's an async function.
    business_unit = await detect_business_unit_with_llm(llm, request.query)
    
    print(f"Business Unit: {business_unit}")

    months = request.months
    data = []
    
    if "large" in business_unit:
        large_customers = INITIAL_LARGE_CUSTOMERS
        salespeople = INITIAL_SALESPEOPLE
        for month in range(1, months + 1):
            if month % 3 == 1 and month != 1:
                salespeople += 1
            new_large = salespeople * SALESPEOPLE_TO_LARGE_CUSTOMER_RATIO
            large_customers += new_large
            large_revenue = large_customers * REVENUE_PER_LARGE_CUSTOMER
            
            data.append({
                "Month": f"M{month}",
                "Salespeople": salespeople,
                "Total Customers": round(large_customers, 1),
                "Revenue": large_revenue
            })
    
    elif "small_medium" in business_unit:
        smb_customers = 0
        for month in range(1, months + 1):
            smb_customers += NEW_SMB_CUSTOMERS_PER_MONTH
            smb_revenue = smb_customers * REVENUE_PER_SMB_CUSTOMER
            
            data.append({
                "Month": f"M{month}",
                "Total Customers": round(smb_customers, 1),
                "Revenue": smb_revenue
            })
    
    else:
        raise ValueError("The query could not be interpreted to a specific business unit. Please be more specific.")

    df = pd.DataFrame(data)
    
    return df

# CHANGE 3: This function is also now asynchronous, using `async def`.
async def detect_business_unit_with_llm(llm: ChatGoogleGenerativeAI, query: str):
    """Use LLM for business unit detection if available"""
    try:
        kb_text = read_knowledge_base()
        
        prompt_template = ChatPromptTemplate.from_template(
            """Based on the KNOWLEDGE BASE below, interpret the USER'S QUERY.
            Respond with the single business unit name 'large' or 'small_medium'.
            
            KNOWLEDGE BASE:
            {knowledge_base}
            
            USER'S QUERY: {user_query}
            """
        )

        chain = (
            {"knowledge_base": RunnablePassthrough(), "user_query": RunnablePassthrough()}
            | prompt_template
            | llm
            | RunnableLambda(lambda x: x.content.strip().lower())
        )

        # CHANGE 4: The call to `ainvoke` is now correctly awaited.
        return await chain.ainvoke({
            "knowledge_base": kb_text,
            "user_query": query  
        })
    except Exception as e:
        print(f"LLM detection failed: {e}")
        # Fallback logic if LLM fails
        return "large"
