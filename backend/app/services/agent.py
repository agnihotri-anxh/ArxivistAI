import json
from openai import OpenAI
from googlesearch import search as google_search_api
from ..core.config import settings
from .milvus_search import search_academic_database
from .prompt.system_prompt import system_prompt

# Initialize OpenAI client pointing to Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.GROQ_API_KEY
)

# The fallback tool definition for Llama-3-70B
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_online",
            "description": "Searches the open internet for an answer. ONLY call this if the Primary Academic Context provided in the prompt does NOT contain the answer to the user's question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The web search query to find the missing information."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def execute_web_search(query: str) -> str:
    """Performs a live Google search and returns text snippets."""
    print(f"[Fallback] Agent invoked Web Search for: '{query}'")
    try:
        results = list(google_search_api(query, advanced=True, num_results=3))
        formatted = "Web Search Results:\n\n"
        for r in results:
            formatted += f"Title: {r.title}\nDescription: {r.description}\nURL: {r.url}\n\n"
        return formatted if results else "No web results found."
    except Exception as e:
        return f"Web search failed: {str(e)}"

def run_agentic_rag(user_prompt: str, max_iterations: int = 3):
    """
    Runs the Dual-RAG Agentic Workflow. 
    1. ALWAYS forces Milvus Academic Database search first.
    2. Gives the LLM the Academic Context.
    3. If the Academic Context is insufficient, the LLM autonomously calls 'search_online'.
    """
    
    # 1. Force Milvus Retrieval First
    print(f"[Primary RAG] Querying Milvus for: '{user_prompt}'")
    academic_results = search_academic_database(user_prompt)
    
    academic_context = "\n\n=== PRIMARY ACADEMIC CONTEXT ===\n"
    if not academic_results:
        academic_context += "No academic papers found in the internal database.\n"
    else:
        for i, res in enumerate(academic_results):
            academic_context += f"[Result {i+1}]\n"
            academic_context += f"Source: {res['title']} by {res['authors']} ({res['published_year']})\n"
            academic_context += f"Text: {res['text']}\n\n"
            
    # 2. Inject into the LLM Prompt
    full_system_prompt = system_prompt + academic_context
    
    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    iterations = 0
    while iterations < max_iterations:
        iterations += 1
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        # 3. Check if the LLM decided to use the fallback Web Search
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "search_online":
                    args = json.loads(tool_call.function.arguments)
                    search_query = args.get("query")
                    
                    # Execute the Web tool
                    web_results_text = execute_web_search(search_query)
                    
                    # Pass the web results back to the LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "search_online",
                        "content": web_results_text
                    })
            
            # After adding tool results, loop again to let the LLM generate the final answer
            continue
            
        else:
            # LLM didn't call a tool, so it gave a final text response
            return response_message.content
            
    return "Agent reached maximum iterations without giving a final answer."
