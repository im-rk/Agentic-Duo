import os
import shutil
import subprocess
import json
from typing import Tuple, Dict, Any
from models import Observation, Action, Reward, Issue

class AutoMaintainerEnv:
    def __init__(self):
        # We use a temporary workspace to ensure we don't accidentally delete real code
        self.workspace_dir = "/tmp/workspace"
        self.current_task_level = "easy"
        self.current_test_output = None
        self.ci_cd_status = "PENDING"
        self.step_count = 0
        self.max_steps = 15 # Prevent infinite loops to stay under 20 mins

    def reset(self, task_level: str = "easy") -> Observation:
        """
        Wipes the workspace and loads a new broken repository scenario.
        """
        self.current_task_level = task_level
        self.step_count = 0
        self.current_test_output = None
        self.ci_cd_status = "PENDING"
        
        # 1. Clean the workspace
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir)
        
        # 2. Copy the broken repository files into the active workspace
        task_source_dir = os.path.join(os.getcwd(), "tasks", task_level)
        if not os.path.exists(task_source_dir):
            # Fallback for when we haven't created the dummy files yet
            os.makedirs(self.workspace_dir, exist_ok=True)
            with open(os.path.join(self.workspace_dir, "dummy.txt"), "w") as f:
                f.write("Placeholder repo")
        else:
            shutil.copytree(task_source_dir, self.workspace_dir)

        # 3. Return the initial state
        return self.state()

    def state(self) -> Observation:
        """
        Scans the workspace and packages it into our Pydantic Observation model.
        """
        # 1. Get list of files in the workspace
        files = []
        if os.path.exists(self.workspace_dir):
            for root, _, filenames in os.walk(self.workspace_dir):
                for filename in filenames:
                    # Ignore python cache files
                    if "__pycache__" not in root and not filename.endswith(".pyc"):
                        rel_dir = os.path.relpath(root, self.workspace_dir)
                        filepath = os.path.join(rel_dir, filename) if rel_dir != "." else filename
                        files.append(filepath)

        # 2. Load open issues (we store these in a hidden JSON file in the task dir)
        issues_path = os.path.join(self.workspace_dir, ".issues.json")
        open_issues = []
        if os.path.exists(issues_path):
            with open(issues_path, "r") as f:
                raw_issues = json.load(f)
                open_issues = [Issue(**issue) for issue in raw_issues]

        return Observation(
            working_dir_files=files,
            current_test_output=self.current_test_output,
            ci_cd_status=self.ci_cd_status,
            open_issues=open_issues
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Executes the AI's action, calculates dense rewards, and checks if done.
        """
        self.step_count += 1
        reward_value = 0.0
        reward_reason = "Action executed."
        done = False

        try:
            # --- ACTION: READ FILE ---
            if action.action_type == "READ_FILE":
                target_path = os.path.join(self.workspace_dir, action.filepath)
                if os.path.exists(target_path):
                    with open(target_path, "r") as f:
                        content = f.read()
                    # We inject the file content into the test output so the AI can read it
                    self.current_test_output = f"--- FILE: {action.filepath} ---\n{content}"
                    reward_value = 0.05
                    reward_reason = "Successfully read file."
                else:
                    self.current_test_output = f"Error: File {action.filepath} not found."
                    reward_value = -0.1
                    reward_reason = "Attempted to read non-existent file."

            # --- ACTION: EDIT FILE ---
            elif action.action_type == "EDIT_FILE":
                target_path = os.path.join(self.workspace_dir, action.filepath)
                with open(target_path, "w") as f:
                    f.write(action.new_content)
                self.current_test_output = f"Successfully updated {action.filepath}."
                reward_value = 0.1
                reward_reason = "File edited successfully."

            # --- ACTION: RUN PYTEST ---
            elif action.action_type == "RUN_PYTEST":
                # We use subprocess to actually run pytest in the workspace!
                result = subprocess.run(
                    ["pytest", self.workspace_dir], 
                    capture_output=True, 
                    text=True
                )
                
                # Context Management: Truncate massive tracebacks [Hackathon Pro-tip]
                raw_output = result.stdout + result.stderr
                lines = raw_output.split("\n")
                if len(lines) > 50:
                    self.current_test_output = "...\n" + "\n".join(lines[-50:])
                else:
                    self.current_test_output = raw_output

                if result.returncode == 0:
                    self.ci_cd_status = "PASSING"
                    reward_value = 0.5
                    reward_reason = "Tests passed! Great job."
                else:
                    self.ci_cd_status = "FAILING"
                    reward_value = -0.2
                    reward_reason = "Tests failed. Review the traceback."

            # --- ACTION: LABEL ISSUE ---
            elif action.action_type == "LABEL_ISSUE":
                issues_path = os.path.join(self.workspace_dir, ".issues.json")
                if os.path.exists(issues_path):
                    with open(issues_path, "r") as f:
                        issues = json.load(f)
                    
                    labeled = False
                    for issue in issues:
                        if issue["id"] == action.issue_id:
                            issue["label"] = action.label
                            labeled = True
                            break
                    
                    if labeled:
                        with open(issues_path, "w") as f:
                            json.dump(issues, f, indent=2)
                        reward_value = 0.1
                        reward_reason = f"Labeled issue {action.issue_id} as {action.label}."
                    else:
                        reward_value = -0.1
                        reward_reason = f"Issue {action.issue_id} not found."

            # --- ACTION: SUBMIT PR (FINISH) ---
            elif action.action_type == "SUBMIT_PR":
                done = True
                if self.ci_cd_status == "PASSING":
                    reward_value = 1.0
                    reward_reason = "PR submitted with passing tests! Task complete."
                else:
                    reward_value = -0.5
                    reward_reason = "PR submitted, but tests are failing."

        except Exception as e:
            self.current_test_output = f"Environment Exception: {str(e)}"
            reward_value = -0.5
            reward_reason = "Action caused a critical environment error."

        # Safety catch for infinite loops
        if self.step_count >= self.max_steps:
            done = True
            reward_reason += " Max steps reached."

        reward = Reward(value=reward_value, reasoning=reward_reason)
        info = {"step": self.step_count}

        return self.state(), reward, done, info