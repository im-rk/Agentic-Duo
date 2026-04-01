from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Issue(BaseModel):
    id: str = Field(description="Unique identifier for the issue, e.g., '#12'")
    title: str = Field(description="Title of the bug report or feature request")
    body: str = Field(description="Detailed description or traceback of the issue")
    label: Optional[str] = Field(default=None, description="Current taxonomy tag applied to the issue")

class Observation(BaseModel):
    working_dir_files: List[str] = Field(
        description="A list of filepaths currently present in the repository."
    )
    current_test_output: Optional[str] = Field(
        default=None, 
        description="Truncated stdout/stderr from the most recent pytest execution. Null if not yet run."
    )
    ci_cd_status: Literal["PASSING", "FAILING", "PENDING"] = Field(
        description="Current global state of the repository's test suite."
    )
    open_issues: List[Issue] = Field(
        description="List of issues that need to be triaged or resolved."
    )

class Action(BaseModel):
    action_type: Literal["READ_FILE", "EDIT_FILE", "RUN_PYTEST", "LABEL_ISSUE", "SUBMIT_PR"] = Field(
        description="The specific operation the agent wants to perform."
    )
    filepath: Optional[str] = Field(
        default=None, 
        description="Target file for reading or editing (e.g., 'src/engine.py')."
    )
    new_content: Optional[str] = Field(
        default=None, 
        description="The complete new string content to write to the file (used only with EDIT_FILE)."
    )
    issue_id: Optional[str] = Field(
        default=None, 
        description="The ID of the issue to modify (e.g., '#12')."
    )
    label: Optional[Literal["bug", "enhancement", "duplicate", "docs"]] = Field(
        default=None, 
        description="The specific taxonomy label to apply to an issue."
    )

class Reward(BaseModel):
    value: float = Field(
        description="The numerical reward for the current step.",
        ge=-1.0, 
        le=1.0
    )
    reasoning: str = Field(
        description="A human-readable explanation of why this reward was given."
    )