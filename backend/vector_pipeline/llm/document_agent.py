import json
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from vector_pipeline.config.settings import MISTRAL_API_KEY, MISTRAL_MODEL, MISTRAL_TEMPERATURE
from vector_pipeline.embeddings.embed_store import load_vectorstore, get_embedding_model
from vector_pipeline.retrieval.query import query_vectorstore

import psycopg2
import logging

logger = logging.getLogger(__name__)

# Basic in-memory conversational storage for demo purposes
# In production, this should ideally use a proper DB-backed memory per session.
session_memory = {}

@tool
def search_standard_templates(query: str, clause_type: str = None) -> str:
    """Searches the standard legal templates (ChromaDB) for similar clauses. 
    Use this to see what 'Standard' language looks like for a specific topic.
    If searching for a specific clause type, provide it."""
    try:
        model = get_embedding_model()
        vs = load_vectorstore(model)
        results = query_vectorstore(vs, query, clause_type=clause_type, document_type=None, k=3)
        if not results:
            return "No matching standard templates found."
        
        response = ""
        for doc, score in results:
            doc_type = doc.metadata.get("document_type", "Template")
            c_type = doc.metadata.get("clause", "Unknown")
            response += f"[{doc_type} - {c_type}] (Similarity {round(score,2)}): {doc.page_content}\n\n"
        return response
    except Exception as e:
        return f"Error searching templates: {str(e)}"

@tool
def get_client_clauses(document_id: str, clause_type: str = None) -> str:
    """Fetches the actual clauses uploaded by the client from the PostgreSQL database.
    Use this to read exactly what the client's contract says.
    Pass 'clause_type' to filter (e.g., 'Indemnification'), or leave None for all clauses."""
    from vector_pipeline.config.settings import DATABASE_URL
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            if clause_type:
                cur.execute(
                    "SELECT clause, content FROM clauses WHERE document_id = %s AND clause ILIKE %s LIMIT 15", 
                    (document_id, f"%{clause_type}%")
                )
            else:
                cur.execute(
                    "SELECT clause, content FROM clauses WHERE document_id = %s LIMIT 15", 
                    (document_id,)
                )
            rows = cur.fetchall()
            if not rows:
                return "No clauses found for this document matching your criteria."
                
            response = ""
            for row in rows:
                response += f"[{row[0]}]: {row[1][:500]}...\n\n"
            return response
    except Exception as e:
        return f"Database error fetching clauses: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()

@tool
def get_risk_analysis(document_id: str) -> str:
    """Fetches the overall risk tagging and analysis for the entire document, summarizing high, medium, and low risk clauses."""
    from vector_pipeline.config.settings import DATABASE_URL
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute("SELECT review_data FROM document_reviews WHERE document_id = %s", (document_id,))
            row = cur.fetchone()
            if not row:
                return "No risk analysis has been generated for this document yet."
            
            review_data = row[0]
            if not isinstance(review_data, list):
                if isinstance(review_data, str):
                    review_data = json.loads(review_data)
                else:
                    return "Risk data is malformed."
            
            high_risk = []
            medium_risk = []
            for clause in review_data:
                risk = clause.get("risk", "Low")
                if risk == "High":
                    high_risk.append(f"[{clause.get('clause_type', 'Unknown')}]: {clause.get('content', '')[:200]}...")
                elif risk == "Medium":
                    medium_risk.append(f"[{clause.get('clause_type', 'Unknown')}]: {clause.get('content', '')[:200]}...")
            
            response = f"Document Risk Summary:\nTotal Clauses Analyzed: {len(review_data)}\n"
            response += f"High Risk Clauses ({len(high_risk)}):\n" + "\n".join(high_risk) + "\n\n"
            response += f"Medium Risk Clauses ({len(medium_risk)}):\n" + "\n".join(medium_risk)
            return response
    except Exception as e:
        return f"Database error fetching risk analysis: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()

def get_agent_executor():
    """Returns a Mistral agent equipped with the tools."""
    llm = ChatMistralAI(
        model=MISTRAL_MODEL,
        mistral_api_key=MISTRAL_API_KEY,
        temperature=MISTRAL_TEMPERATURE
    )
    # Bind the tools to the LLM
    llm_with_tools = llm.bind_tools([search_standard_templates, get_client_clauses, get_risk_analysis])
    return llm_with_tools

def chat_with_document(document_id: str, user_message: str, session_id: str = "default_session") -> str:
    """
    Main entry point for chatting with a document.
    Maintains a simple message history and triggers tools if needed.
    """
    llm = get_agent_executor()
    
    # Initialize session history if it doesn't exist
    if session_id not in session_memory:
        system_instruction = f"""You are an elite legal AI assistant embedded in the LACCIS contract review platform.
You are chatting with a legal professional who is reviewing a single document (ID: {document_id}).
You have access to tools to query the client's clauses, search standard legal templates, and fetch the overall risk analysis.
Always give direct, strictly factual answers. If asked about what the contract says, always use your 'get_client_clauses' tool first to read it.
If asked about document risks or high-risk clauses, use the 'get_risk_analysis' tool.
Do NOT guess what the contract says."""
        session_memory[session_id] = [SystemMessage(content=system_instruction)]
        
    # Append user message
    session_memory[session_id].append(HumanMessage(content=user_message))
    
    # Run LLM (it might decide to use a tool)
    response = llm.invoke(session_memory[session_id])
    session_memory[session_id].append(response)
    
    # Check if a tool was called
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            logger.info(f"Agent invoked tool: {tool_name} with args {tool_args}")
            
            # Execute the correct tool
            if tool_name == "get_client_clauses":
                tool_args["document_id"] = document_id
                tool_result = get_client_clauses.invoke(tool_args)
            elif tool_name == "search_standard_templates":
                tool_result = search_standard_templates.invoke(tool_args)
            elif tool_name == "get_risk_analysis":
                tool_args["document_id"] = document_id
                tool_result = get_risk_analysis.invoke(tool_args)
            else:
                tool_result = f"Error: Tool {tool_name} not found."
                
            # Feed the tool's result back into the memory
            from langchain_core.messages import ToolMessage
            session_memory[session_id].append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
            
        # Call the LLM one final time to synthesize the final answer
        final_response = llm.invoke(session_memory[session_id])
        session_memory[session_id].append(final_response)
        return final_response.content
    else:
        # It just answered directly
        return response.content
