from mcp.server.fastmcp import FastMCP

# Demo is just the name here
mcp = FastMCP("Demo")

print("we ran it")

# the @mcp.tool() is a decorator that allows us to make tool
@mcp.tool()
def add(a: int, b: int) -> int:
    # add two numbers
    return a + b

# add dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name:str) ->str:
    #get a personalized greeting
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')