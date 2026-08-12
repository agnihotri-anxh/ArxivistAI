import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from googlesearch import search as google_search_api
from ..core.config import settings
from .milvus_search import search_academic_database
from .prompt.system_prompt import system_prompt

import os

nvidia_api_key = os.getenv("NVIDIA_API_KEY", "").strip()

if nvidia_api_key:
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_api_key
    )
    MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b"
else:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.GROQ_API_KEY
    )
    MODEL_NAME = "llama-3.3-70b-versatile"

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

def run_agentic_rag(user_prompt: str, history: Optional[List[Dict[str, str]]] = None, max_iterations: int = 3) -> str:
    """
    Runs the Dual-RAG Agentic Workflow with conversational memory support. 
    1. ALWAYS forces Milvus Academic Database search first.
    2. Gives the LLM the Academic Context.
    3. Incorporates previous conversation turns from `history`.
    4. If Academic Context is insufficient, the LLM autonomously calls 'search_online'.
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
            
    # 2. Inject into System Prompt
    full_system_prompt = system_prompt + academic_context
    
    messages = [
        {"role": "system", "content": full_system_prompt}
    ]

    # 3. Add previous conversation history turns (up to last 10 messages)
    if history:
        for msg in history[-10:]:
            role = msg.get("role")
            content = msg.get("content")
            if role in ["user", "assistant"] and content:
                if len(messages) > 1 and messages[-1].get("role") == role:
                    continue
                messages.append({"role": role, "content": content})

    # Add current user prompt (only if not already the last message)
    if len(messages) == 1 or messages[-1].get("role") != "user":
        messages.append({"role": "user", "content": user_prompt})
    
    iterations = 0
    while iterations < max_iterations:
        iterations += 1
        
        try:
            kwargs = {
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.1
            }
            if nvidia_api_key:
                kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 4096}
            else:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # 4. Check if the LLM decided to use the fallback Web Search
            if getattr(response_message, "tool_calls", None):
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "search_online":
                        args = json.loads(tool_call.function.arguments)
                        search_query = args.get("query")
                        
                        web_results_text = execute_web_search(search_query)
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "search_online",
                            "content": web_results_text
                        })
                continue
                
            else:
                return response_message.content or "No response generated."

        except Exception as err:
            print(f"[Agent] Execution fallback note: {err}")
            try:
                fallback_res = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.1
                )
                return fallback_res.choices[0].message.content or "No response generated."
            except Exception as e2:
                return f"Error executing AI generation: {str(e2)}"

            
    return "Agent reached maximum iterations without giving a final answer."
