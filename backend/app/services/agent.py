import json
from openai import OpenAI
from ..core.config import settings
from .milvus_search import search_academic_database

# Initialize OpenAI client pointing to Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.GROQ_API_KEY
)

# The tool definition for Llama-3-70B
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_academic_database",
            "description": "Search the academic database for relevant research papers and context. Call this when you need facts to answer the user's question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The semantic search query to find relevant papers."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def run_agentic_rag(user_prompt: str, max_iterations: int = 3):
    """
    Runs the Agentic Workflow. The LLM can decide to call the search tool multiple times
    if it needs better context, before finally answering the user.
    """
    messages = [
        {"role": "system", "content": "You are a brilliant AI Research Assistant. You have access to a semantic search tool to query a massive vector database of academic papers. You must answer the user's questions accurately based on the search results. If the search results aren't helpful, you can call the tool again with a different query. Always cite the Source (Author, Year)."},
        {"role": "user", "content": user_prompt}
    ]
    
    iterations = 0
    while iterations < max_iterations:
        iterations += 1
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        # Check if the LLM decided to call a tool
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "search_academic_database":
                    args = json.loads(tool_call.function.arguments)
                    search_query = args.get("query")
                    print(f"Agent invoked search with query: {search_query}")
                    
                    # Execute the tool
                    results = search_academic_database(search_query)
                    
                    # Format results as a string
                    formatted_context = "Search Results:\n\n"
                    for i, res in enumerate(results):
                        formatted_context += f"Result {i+1}\n"
                        formatted_context += f"Source: {res['title']} by {res['authors']} ({res['published_year']})\n"
                        formatted_context += f"Text: {res['text']}\n\n"
                    
                    # Pass the results back to the LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "search_academic_database",
                        "content": formatted_context
                    })
            
            # After adding tool results, loop again to let the LLM generate the final answer
            continue
            
        else:
            # LLM didn't call a tool, so it gave a final text response
            return response_message.content
            
    return "Agent reached maximum iterations without giving a final answer."
