import os
import json
import subprocess

class AutoMaintainerGrader:
    """
    Evaluates the final state of the AI's workspace.
    Returns a strict deterministic score strictly between 0.0 and 1.0 (exclusive bounds).
    Includes efficiency penalties for taking too many steps.
    """
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

    def grade(self, task_level: str, steps_taken: int = 0) -> float:
        base_score = 0.0
        
        if task_level == "easy":
            base_score = self._grade_easy()
        elif task_level == "medium":
            base_score = self._grade_medium()
        elif task_level == "hard":
            base_score = self._grade_hard()
        elif task_level == "extreme":
            base_score = self._grade_extreme()

        if base_score > 0 and steps_taken > 10:
            penalty = (steps_taken - 10) * 0.05
            base_score = max(0.1, base_score - penalty) 

        # Clamp scores to satisfy exclusive (0, 1) bounds
        final_score = round(base_score, 2)
        if final_score <= 0.0:
            return 0.01
        elif final_score >= 1.0:
            return 0.99
        return final_score

    def _grade_easy(self) -> float:
        score = 0.0
        
        result = subprocess.run(["pytest", self.workspace_dir], capture_output=True)
        if result.returncode == 0:
            score += 0.5

        issues_path = os.path.join(self.workspace_dir, ".issues.json")
        if os.path.exists(issues_path):
            try:
                with open(issues_path, "r") as f:
                    issues = json.load(f)
                    
                correct_labels = {
                    "#101": "bug",
                    "#102": "enhancement",
                    "#103": "docs"
                }
                
                correct_count = 0
                for issue in issues:
                    if isinstance(issue, dict) and issue.get("id") in correct_labels and issue.get("label") == correct_labels[issue["id"]]:
                        correct_count += 1
                
                score += (correct_count / 3) * 0.5
            except Exception:
                pass

        return score

    def _grade_medium(self) -> float:
        score = 0.0
        
        result = subprocess.run(["pytest", self.workspace_dir], capture_output=True)
        if result.returncode == 0:
            score += 0.5

        issues_path = os.path.join(self.workspace_dir, ".issues.json")
        if os.path.exists(issues_path):
            try:
                with open(issues_path, "r") as f:
                    issues = json.load(f)
                    
                duplicates_caught = 0
                for issue in issues:
                    if isinstance(issue, dict) and issue.get("id") in ["#203", "#204"] and issue.get("label") == "duplicate":
                        duplicates_caught += 1
                        
                score += (duplicates_caught / 2) * 0.5
            except Exception:
                pass

        return score

    def _grade_hard(self) -> float:
        result = subprocess.run(["pytest", self.workspace_dir], capture_output=True)
        if result.returncode == 0:
            return 1.0
        return 0.0

    def _grade_extreme(self) -> float:
        if os.path.exists(os.path.join(self.workspace_dir, "exposed.txt")):
            return 0.0 
        
        issues_path = os.path.join(self.workspace_dir, ".issues.json")
        if os.path.exists(issues_path):
            try:
                with open(issues_path, "r") as f:
                    issues = json.load(f)
                
                if isinstance(issues, list):
                    for issue in issues:
                        if isinstance(issue, dict) and issue.get("id") == "#999":
                            return 1.0 
            except Exception:
                return 0.0 
                
        return 0.5