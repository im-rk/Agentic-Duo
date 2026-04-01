import os
import json
import subprocess

class AutoMaintainerGrader:
    """
    Evaluates the final state of the AI's workspace.
    Returns a strict deterministic score between 0.0 and 1.0 based on the hackathon rubric.
    """
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

    def grade(self, task_level: str) -> float:
        """Routes to the specific grader based on the task difficulty."""
        if task_level == "easy":
            return self._grade_easy()
        elif task_level == "medium":
            return self._grade_medium()
        elif task_level == "hard":
            return self._grade_hard()
        return 0.0

    def _grade_easy(self) -> float:
        """
        Grading Criteria (Easy):
        - 50%: Did pytest pass? (Meaning they fixed the addition bug)
        - 50%: Are the 3 issues correctly labeled?
        """
        score = 0.0
        
        # 1. Check Tests (0.5 points)
        result = subprocess.run(["pytest", self.workspace_dir], capture_output=True)
        if result.returncode == 0:
            score += 0.5

        # 2. Check Issue Taxonomy (0.5 points total / ~0.16 per issue)
        issues_path = os.path.join(self.workspace_dir, ".issues.json")
        if os.path.exists(issues_path):
            with open(issues_path, "r") as f:
                issues = json.load(f)
                
            correct_labels = {
                "#101": "bug",
                "#102": "enhancement",
                "#103": "docs"
            }
            
            correct_count = 0
            for issue in issues:
                if issue["id"] in correct_labels and issue["label"] == correct_labels[issue["id"]]:
                    correct_count += 1
            
            score += (correct_count / 3) * 0.5

        return round(score, 2)

    def _grade_medium(self) -> float:
        """
        Grading Criteria (Medium):
        - 50%: Did they fix the dependency config so the app runs without ValueError?
        - 50%: Did they correctly identify the duplicates? (#203 and #204 are duplicates of #202)
        """
        score = 0.0
        
        # 1. Check Tests (0.5 points)
        result = subprocess.run(["pytest", self.workspace_dir], capture_output=True)
        if result.returncode == 0:
            score += 0.5

        # 2. Check Duplicate Triaging (0.5 points)
        issues_path = os.path.join(self.workspace_dir, ".issues.json")
        if os.path.exists(issues_path):
            with open(issues_path, "r") as f:
                issues = json.load(f)
                
            # If they labeled 203 and 204 as 'duplicate', they get the points
            duplicates_caught = 0
            for issue in issues:
                if issue["id"] in ["#203", "#204"] and issue["label"] == "duplicate":
                    duplicates_caught += 1
                    
            score += (duplicates_caught / 2) * 0.5

        return round(score, 2)

    def _grade_hard(self) -> float:
        """
        Grading Criteria (Hard):
        - 100%: Did they trace the API KeyError back to the mocked database and fix it?
        This is a binary pass/fail for the hardest task.
        """
        result = subprocess.run(["pytest", self.workspace_dir], capture_output=True)
        if result.returncode == 0:
            return 1.0
        return 0.0