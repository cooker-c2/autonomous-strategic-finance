# logic_engine.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# === ADD DEBUG CODE HERE ===
api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key loaded: {api_key is not None}")  # Should print True
print(f"API Key length: {len(api_key) if api_key else 0}")  # Should be around 39 characters
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}")
# === END DEBUG CODE ===

# Define constants for financial metrics (improves readability)
REVENUE_PER_LARGE_CUSTOMER = 16500
REVENUE_PER_SMB_CUSTOMER = 500
SALESPEOPLE_TO_LARGE_CUSTOMER_RATIO = 1.5
NEW_SMB_CUSTOMERS_PER_MONTH = (30000 / 1500) * 0.45
INITIAL_LARGE_CUSTOMERS = 5
INITIAL_SALESPEOPLE = 2

# Set up the Gemini LLM with your API key
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
)

class KnowledgeBaseError(Exception):
    """Custom exception for when the knowledge base file is missing."""
    pass

def read_knowledge_base(file_path="app/knowledge_base.txt"):
    """Reads the knowledge base file into a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise KnowledgeBaseError(f"Error: knowledge_base.txt not found at {file_path}")

def generate_forecast(request):
    """
    Generates a financial forecast based on a structured request.
    """
    print(f"Processing query: {request.query}")
    
    # Use the LLM to interpret the query
    kb_text = read_knowledge_base()
    
    # Use the modern LCEL approach for the chain
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

    business_unit = chain.invoke({
        "knowledge_base": kb_text,
        "user_query": request.query
    })
    
    print(f"LLM Analysis Result: {business_unit}")

    # Use the interpreted business unit to run the forecast logic
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