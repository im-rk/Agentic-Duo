import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# Import our custom environment and models
from environment import AutoMaintainerEnv
from graders import AutoMaintainerGrader
from models import Action

# Load environment variables from a .env file (for local testing)
load_dotenv()

# Strict Hackathon Required Variables (Matches Checklist Exactly)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini") 
HF_TOKEN = os.getenv("HF_TOKEN")

# Fallback for local testing if HF_TOKEN isn't set
api_key = HF_TOKEN if HF_TOKEN else os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI Client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=api_key
)

def clean_json_response(raw_text: str) -> str:
    """Removes markdown formatting if the LLM wraps the JSON in backticks."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def run_agent_on_task(env: AutoMaintainerEnv, task_level: str) -> float:
    """Runs the LLM agent loop for a specific task difficulty."""
    
    # EXACT FORMAT REQUIRED BY AUTOGRADER: [START] task=NAME
    print(f"[START] task={task_level}", flush=True)
    
    obs = env.reset(task_level=task_level)
    done = False
    
    # System prompt defining the AI's persona and JSON strictness
    system_prompt = """You are an elite Autonomous Software Maintainer.
Your goal is to fix the broken CI/CD pipeline, resolve dependency conflicts, and triage open issues in the workspace.
You must interact with the environment by outputting strictly valid JSON matching this schema:
{
  "action_type": "READ_FILE" | "EDIT_FILE" | "RUN_PYTEST" | "LABEL_ISSUE" | "SUBMIT_PR",
  "filepath": "string (optional)",
  "new_content": "string (optional)",
  "issue_id": "string (optional)",
  "label": "bug" | "enhancement" | "duplicate" | "docs" (optional)
}
NEVER output anything other than the raw JSON object. Do not include markdown or explanations outside the JSON."""

    # We keep a brief history to give the LLM context of its past actions
    messages = [{"role": "system", "content": system_prompt}]

    while not done:
        # 1. Package the current observation into the prompt
        prompt = f"CURRENT STATE:\n{obs.model_dump_json(indent=2)}\n\nWhat is your next action? (Output JSON only)"
        messages.append({"role": "user", "content": prompt})
        
        try:
            # 2. Call the LLM
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1, 
            )
            
            # 3. Parse the LLM's response
            raw_reply = response.choices[0].message.content
            messages.append({"role": "assistant", "content": raw_reply}) 
            
            clean_reply = clean_json_response(raw_reply)
            action_dict = json.loads(clean_reply)
            
            # 4. Validate using our Pydantic Model
            action = Action(**action_dict)
            
            # 5. Take the step in the environment
            obs, reward, done, info = env.step(action)
            
            # EXACT FORMAT REQUIRED BY AUTOGRADER: [STEP] step=1 reward=0.5
            # Note: This is now placed AFTER env.step() so it can access the reward value
            print(f"[STEP] step={env.step_count} reward={reward.value}", flush=True)
            
            # Prevent hitting rate limits during the hackathon validation
            time.sleep(4) 
            
        except json.JSONDecodeError:
            messages.append({"role": "user", "content": "ERROR: Your last output was not valid JSON. Please format exactly as requested."})
        except Exception as e:
            print(f"Error during step execution: {e}", flush=True)
            break

    # 6. Evaluate the final score using our deterministic grader
    grader = AutoMaintainerGrader(env.workspace_dir)
    final_score = grader.grade(task_level, env.step_count)
    
    # EXACT FORMAT REQUIRED BY AUTOGRADER: [END] task=NAME score=0.95 steps=1
    print(f"[END] task={task_level} score={final_score} steps={env.step_count}", flush=True)
    
    return final_score

if __name__ == "__main__":
    # Initialize the core environment
    env = AutoMaintainerEnv()
    
    # Run the baseline across all difficulties
    scores = {}
    for difficulty in ["easy", "medium", "hard", "extreme"]:
        score = run_agent_on_task(env, difficulty)
        scores[difficulty] = score