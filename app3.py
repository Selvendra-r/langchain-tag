import os
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

from dotenv import load_dotenv
load_dotenv()

# --- 1. DATABASE CONNECTION ---

# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")  # ← change
# DB_HOST = os.getenv("DB_HOST")
# DB_NAME = "DB_NAME"
DB_USER = "root"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_NAME = "sales_report"
db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
engine = create_engine(db_url)

try:
    db = SQLDatabase(engine)
    print(f"✅ Connected to Database: {DB_NAME}")
    print(f"📊 Tables found: {db.get_usable_table_names()}")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

# --- 2. LLM SETUP (GROQ - FREE & FAST) ---
# Get your FREE key from: https://console.groq.com
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
# llm = ChatGroq(
#     model_name="llama-3.1-8b-instant", 
#     temperature=0
# )

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

# # --- 3. SQL AGENT CREATION ---
# table_info = """
# Table: users
# Columns: id (INTEGER, PK), name (VARCHAR), email (VARCHAR),phone (BIGINT), city (VARCHAR)
# """

# custom_prefix = f"""You are an efficient SQL expert.
# You have access to the following database schema:
# {table_info}

# Rules:
# 1. When asked to add or insert a users, construct an INSERT statement for the 'users' table.
# 2. Use the following tool flow: 
#    - Thought: Analyze the query.
#    - Action: sql_db_query_checker
#    - Action Input: SQL QUERY
#    - Observation: Results from checker.
#    - Thought: I will now run the query.
#    - Action: sql_db_query
#    - Action Input: SQL QUERY
# 3. DO NOT output code blocks to the users; only use tools to run them.
# 4. CONFIRM to the users once the data is successfully added."""

agent_executor = create_sql_agent(
    llm, 
    db=db, 
    agent_type="zero-shot-react-description",
    # prefix=custom_prefix,
    verbose=False,
    allow_dangerous_requests=True,
    top_k=100
)

# --- 4. CHAT INTERFACE ---
print("\n🚀 AI SQL Reporting Bot is Ready!")
print("Example: 'Give me a list of Chennai users' or 'Show me a merged sales report'")
print("(Type 'q' to quit)\n")

while True:
    user_query = input("User: ")
    
    if user_query.lower() == 'q':
        print("Bye!")
        break
    
    if not user_query.strip():
        continue 

    try:
        # Agent analyzes the question, writes SQL, runs it, and gives the answer
        response = agent_executor.invoke({"input": user_query})
        print(f"\nBot: {response['output']}\n")
    except Exception as e:
        print(f"\n⚠️ Error: {e}\n")






