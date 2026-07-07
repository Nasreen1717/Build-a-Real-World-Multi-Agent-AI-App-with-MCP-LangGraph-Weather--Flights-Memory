# LangGraph Multi-Agent Travel Booking System with Long-Term Memory

import os
import json
from typing import TypedDict, Annotated
import operator
import asyncio
import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from mcp_client import (
    tavily_mcp_search,
    get_airports,
    get_airlines,
    aviation_mcp_call,
    extract_destination,
    forecast_mcp_search,
    weather_mcp_search
)

from dotenv import load_dotenv
load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

llm = ChatGroq(model="llama-3.3-70b-versatile")

# State
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
    weather_results: str


# ---------------------------------------------------------------------------
# Currency instruction reused across every agent prompt
# ---------------------------------------------------------------------------
CURRENCY_RULE = "IMPORTANT: Show ALL prices, costs, and budgets ONLY in Pakistani Rupees (PKR / Rs). Do not use USD, INR, or any other currency."


# ---------------------------------------------------------------------------
# Flight Agent
# ---------------------------------------------------------------------------
FLIGHT_AGENT_PROMPT = """
You are a travel flight expert.

""" + CURRENCY_RULE + """

User Query:
{query}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Generate:
1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range (in PKR)
6. Peak season pricing warning
7. Booking advice

Return concise travel guidance.
"""

def flight_agent(state: TravelState):
    print("\nINSIDE FLIGHT AGENT\n")
    query = state["user_query"]

    try:
        airports = asyncio.run(aviation_mcp_call("list_airports"))
        airlines = asyncio.run(aviation_mcp_call("list_airlines"))

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            airport_data=str(airports)[:3000],
            airline_data=str(airlines)[:3000]
        )

        response = llm.invoke([
            SystemMessage(content="You are an expert travel flight planner. Always quote prices in PKR."),
            HumanMessage(content=prompt)
        ])

        flight_data = response.content

    except Exception as e:
        flight_data = f"Flight information unavailable: {str(e)}"

    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight recommendations generated")],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ---------------------------------------------------------------------------
# Helper: normalize raw MCP / Tavily tool output into clean text
# ---------------------------------------------------------------------------
def format_tavily_results(raw_response, max_results: int = 5) -> str:
    try:
        if isinstance(raw_response, list):
            texts = []
            for block in raw_response:
                if isinstance(block, dict) and "text" in block:
                    texts.append(block["text"])
                else:
                    texts.append(str(block))
            raw_text = "\n".join(texts)
        else:
            raw_text = str(raw_response)

        data = json.loads(raw_text)
        results = data.get("results", [])

        if not results:
            return raw_text[:3000]

        formatted = []
        for r in results[:max_results]:
            title = (r.get("title") or "N/A").strip()
            url = (r.get("url") or "").strip()
            content = (r.get("content") or "").strip()[:400]
            formatted.append(f"- {title}\n  {content}\n  Source: {url}")

        return "\n\n".join(formatted)

    except (json.JSONDecodeError, TypeError, AttributeError, KeyError):
        return str(raw_response)[:3000]


# ---------------------------------------------------------------------------
# Hotel Agent — FIXED: ab raw JSON dump nahi karta, LLM se clean karta hai
# ---------------------------------------------------------------------------
HOTEL_AGENT_PROMPT = """
You are a travel hotel expert.

""" + CURRENCY_RULE + """

User Query:
{query}

Raw Search Data (from web search, may contain noise - use only relevant parts):
{search_data}

Based on the above, provide:
1. Top 3-5 recommended hotels with a brief description
2. Approximate price range PER NIGHT in PKR
3. Best area/neighborhood to stay
4. Booking tips

Return concise, clean travel guidance. Do NOT include raw JSON, escaped
characters, or unnecessary URLs.
"""

def hotel_agent(state: TravelState):
    print("\nINSIDE HOTEL AGENT\n")
    query = f"Best hotels for {state['user_query']}"

    try:
        raw_results = asyncio.run(tavily_mcp_search(query))
        formatted_results = format_tavily_results(raw_results)

        prompt = HOTEL_AGENT_PROMPT.format(
            query=query,
            search_data=formatted_results
        )

        response = llm.invoke([
            SystemMessage(content="You are an expert hotel and accommodation advisor. Always quote prices in PKR."),
            HumanMessage(content=prompt)
        ])

        hotel_results = response.content

    except Exception as e:
        hotel_results = f"Hotel information unavailable: {str(e)}"

    return {
        "hotel_results": hotel_results,
        "messages": [AIMessage(content="Hotel recommendations generated")],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ---------------------------------------------------------------------------
# Weather Agent
# ---------------------------------------------------------------------------
def weather_agent(state: TravelState):
    city = extract_destination(state["user_query"])

    weather_data = asyncio.run(weather_mcp_search(city))
    forecast_data = asyncio.run(forecast_mcp_search(city))

    return {
        "weather_results": f"""
        Current Weather:
        {weather_data}

        Forecast:
        {forecast_data}
        """,
        "messages": [AIMessage(content="Weather information fetched")]
    }


# ---------------------------------------------------------------------------
# Itinerary Agent
# ---------------------------------------------------------------------------
def itinerary_agent(state: TravelState):
    prompt = f"""
    Create a travel itinerary.

    {CURRENCY_RULE}

    User Query:
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}

    Weather Information:
    {state['weather_results']}

    Include a total estimated budget breakdown in PKR at the end.
    """

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner. Always quote all prices in PKR."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("itinerary_agent", itinerary_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "weather_agent")
graph.add_edge("weather_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", END)

_conn = psycopg.connect(DATABASE_URL)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    import uuid
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")
    for msg in result["messages"]:
        print(msg.content)