from mcp.server.fastmcp import FastMCP
from stravalib import Client
from fastapi import FastAPI
import uvicorn
import threading
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from pydantic import Field
from dotenv import load_dotenv
import os

load_dotenv()

# I can do like an init strava command where it calls a tool the embeds all of my runs and then stores them on qdrant

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Demo is just the name here
listener = FastAPI(
    title = "Listener"
)

listener.add_middleware(
    CORSMiddleware,
    # we have to adjust this origin to our frontend url once it is hosted
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_fastapi():
    uvicorn.run(listener, host="127.0.0.1", port=5000)

# the smart thing to do would probably be to have a different project for the listener

access_token = None
refresh_token = None


@listener.get("/authorization")
def grab_auth_code_and_exchange_for_token(request: Request):
    global access_token
    global refresh_token
    auth_code = request.query_params.get("code")

    if auth_code:
        client = Client()
        token_response = client.exchange_code_for_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code=auth_code
        )

        access_token = token_response["access_token"]
        refresh_token = token_response["refresh_token"]

        return {"message" : "Access token stored"}

    return {"message" : "Authorization Failed"}

mcp = FastMCP("Demo")


# code : d19da02f3aea9f9aa6db1325a83ca5cfba2679af
def run_mcp():
    mcp.run(transport='stdio')

# the @mcp.tool() is a decorator that allows us to make tool
@mcp.tool()
def add(a: int, b: int) -> int:
    # add two numbers
    return a + b

@mcp.tool()
def authenticate_with_strava() -> str:
    try:
        client = Client()
        url = client.authorization_url(
            client_id=CLIENT_ID,
            redirect_uri='http://127.0.0.1:5000/authorization',
            scope='activity:read_all'
        )

        return url
    except Exception as e:
        return f"The API call failed: {e}"

@mcp.tool()
def retrieve_strava_activities() -> dict:
    global access_token
    while access_token == None:
        continue

    try:
        client = Client(
            access_token=access_token,
        )

        # athlete = client.get_athlete()
        # activities = client.get_activities(after="2025-06-01", limit=10)
        activities = client.get_activities(after="2025-01-01")


        return activities

        # return {"access_token" : access_token,
        #         "type" : type(access_token)
        #        }
    except Exception as e:
        return f"Retrieving activities failed: {e}"


@mcp.tool()
def lookup_N_runs(
        N : int = Field(description="The number of runs the user wants to grab from recent activity")
    ) -> dict:

    return {"result": N}
    

# see if the model can deduce what to pass into this as input
@mcp.tool()
def lookup_specific_run_by_date(
    date: str = Field(description="Date in format YYYY-MM-DD inferred from query")
    ) -> dict:

    global access_token
    while access_token == None:
        continue
    try:
        client = Client(
            access_token=access_token
        )

        activity = client.get_activities(after=date, limit=1)

        return activity
    except Exception as e:
        return f"Retrieving activity on {date} failed: {e}"
    
# MCP tool that tells you when is a good time to run based on weather in your area




# add dynamic greeting resource
# how can i get this resource to be reached from claude desktop?
@mcp.resource("greeting://{name}")
def get_greeting(name:str) ->str:
    #get a personalized greeting
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Initialize and run the server
    # mcp.run(transport='stdio')
    # retrieve strava runs, embed, store onto qdrant?
    # run methods to assist the agent ex) compute weekly mileage, monthly milage 
    # compute historical pace trends, keep a rolling average of these metrics
    mcp_thread = threading.Thread(target=run_mcp)
    fastapi_thread = threading.Thread(target=run_fastapi)
    mcp_thread.start()
    fastapi_thread.start()
    mcp_thread.join()
    fastapi_thread.join()