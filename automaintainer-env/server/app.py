from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from environment import AutoMaintainerEnv
from models import Action
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

env = AutoMaintainerEnv()

@app.get("/")
def serve_dashboard():
    """Serves the beautiful visual dashboard to human visitors."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(base_dir, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "Running", 
        "message": "API is active, but index.html was not found."
    }
@app.post("/reset")
async def reset_env(request: Request):
    """The OpenEnv bot calls this to start a task."""
    try:
        body = await request.json()
    except Exception:
        body = {}
        
 
    task = body.get("task_level", "easy") if isinstance(body, dict) else "easy"
    
    obs = env.reset(task_level=task)
    return obs.model_dump()

@app.post("/step")
async def step_env(request: Request):
    """The OpenEnv bot calls this to take actions."""
    data = await request.json()
    

    action = Action(**data)
    
  
    obs, reward, done, info = env.step(action)
    
 
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info
    }

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == '__main__':
    main()