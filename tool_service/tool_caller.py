## FastAPI request call tool
import requests

url = "http://127.0.0.1:8848"

def call_tool(tool_name: str, tool_args: dict):
    resp = requests.post(
        f"{url}/call_tool/{tool_name}",
        json=tool_args
    )
    task_id = resp.json()["task_id"]
    print(f"Create Task ID: {task_id}")
    messages = requests.get(f"{url}/callback/{task_id}")
    task_inf = messages.json()

    event = getattr(task_inf, 'event', None)
    if event == 'error':
        print(f"Error: {task_inf["data"]}")
        return None
    
    print(f"Status update: {task_inf['status']}")
    
    if task_inf["status"] == "completed":
        return task_inf["result"]
    elif task_inf["status"] == "failed":
        print(f"Tool error: {task_inf['error']}")
        return None
    elif task_inf["status"] == "cancelled":
        return None

if __name__ == "__main__":
    print()
    
   
    