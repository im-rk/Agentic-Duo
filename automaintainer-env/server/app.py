from fastapi import FastAPI, Request
from environment import AutoMaintainerEnv
from models import Action
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Initialize your God-Tier environment
env = AutoMaintainerEnv()

@app.get("/")
def health_check():
    """Satisfies the Hugging Face health check and human visitors."""
    return {
        "status": "Running", 
        "environment": "AutoMaintainerEnv",
        "message": "Ready for OpenEnv evaluation."
    }

@app.post("/reset")
async def reset_env(request: Request):
    """The OpenEnv bot calls this to start a task."""
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    # Safely get the task level if the bot provides one, default to easy
    task = body.get("task_level", "easy") if isinstance(body, dict) else "easy"
    
    obs = env.reset(task_level=task)
    return obs.model_dump()

@app.post("/step")
async def step_env(request: Request):
    """The OpenEnv bot calls this to take actions."""
    data = await request.json()
    
    # Validate the bot's action using your Pydantic schema
    action = Action(**data)
    
    # Take the step in the environment
    obs, reward, done, info = env.step(action)
    
    # Return the standardized OpenEnv response
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