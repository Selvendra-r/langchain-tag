import os
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

# --- 1. DATABASE CONNECTION ---
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

# --- 2. LLM SETUP ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

# --- 3. MEMORY SETUP ---
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# --- 4. SQL AGENT ---
agent_executor = create_sql_agent(
    llm,
    db=db,
    agent_type="zero-shot-react-description",
    verbose=False,
    allow_dangerous_requests=True,
    top_k=100
)

# --- 5. CHAT INTERFACE ---
print("\n🚀 AI SQL Reporting Bot is Ready!")
print("Example: 'Give me a list of Chennai users'")
print("(Type 'q' to quit)\n")

chat_history = []

while True:
    user_query = input("User: ").strip()

    if user_query.lower() == 'q':
        print("Bye!")
        break

    if not user_query:
        continue

    try:
        # History context prepare
        if chat_history:
            history_text = "\n".join(chat_history[-6:])  # last 3 conversations
            full_input = f"Previous conversation:\n{history_text}\n\nCurrent question: {user_query}"
        else:
            full_input = user_query

        response = agent_executor.invoke({"input": full_input})
        bot_answer = response['output']

        # Save to history
        chat_history.append(f"User: {user_query}")
        chat_history.append(f"Bot: {bot_answer}")

        print(f"\nBot: {bot_answer}\n")

    except Exception as e:
        print(f"\n⚠️ Error: {e}\n")