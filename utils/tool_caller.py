## FastAPI request call tool
import requests
import time
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from config import TOOLPORT
url = "http://127.0.0.1:" + str(TOOLPORT)

def call_tool(tool_name: str = None, tool_args: dict = None):
    if tool_name is None:
        try:
            t1 = time.time()
            resp = requests.get(f"{url}/get_tool")
            result = resp.json()
            t2 = time.time()
            return {
                "tool_result": result,
                "tool_elapsed_time": t2 - t1
            }
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    else:
        try:
            t1 = time.time()
            resp = requests.post(
                f"{url}/call_tool/{tool_name}",
                json=tool_args
            )
            result = resp.json()
            if result["status"]:
                t2 = time.time()
                return {
                    "tool_result": result["result"],
                    "tool_elapsed_time": t2 - t1
                }
            else:
                print(f"Tool error: {result['result']}")
                return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

if __name__ == "__main__":
    print(call_tool())
    
   
    