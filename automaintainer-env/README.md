# 🚀 AutoMaintainerEnv: Autonomous CI/CD & Triage Sandbox

## 📖 Environment Description & Motivation
Modern open-source repositories suffer from massive maintainer fatigue. `AutoMaintainerEnv` simulates a headless GitHub repository where an AI agent acts as the Lead Maintainer. The agent must navigate the file system, resolve dependency conflicts, fix breaking code, and triage issues to restore the CI/CD pipeline to a passing state. 

This is not a toy; it is a high-fidelity simulation of Agentic Software Engineering (SWE-agent style tasks).

## 🛠️ Action & Observation Spaces
This environment strictly adheres to the OpenEnv standard using Pydantic typing.
* **Observation Space**: `working_dir_files` (list), `current_test_output` (string), `ci_cd_status` (string), `open_issues` (list of dicts).
* **Action Space**: `READ_FILE`, `EDIT_FILE`, `RUN_PYTEST`, `LABEL_ISSUE`, `SUBMIT_PR`.

## 🎯 Task Descriptions & Difficulty
1. **Easy:** Fix a simple syntax bug in a math utility and label 3 open issues.
2. **Medium:** Resolve a dependency version conflict in a configuration file causing a `ValueError`, and deduplicate issue reports.
3. **Hard:** Perform a multi-file logical trace. A test fails in the API layer, but the root cause is a missing database key in the backend layer.

## ⚙️ Setup & Usage Instructions
1. Clone the repository.
2. Build the Docker image: `docker build -t automaintainer .`
3. Run the container: `docker run -p 7860:7860 automaintainer`
4. Set your `.env` variables (`OPENAI_API_KEY`, `MODEL_NAME`, `API_BASE_URL`).
5. Run the baseline evaluation: `python inference.py`

## 📊 Baseline Scores
Using the baseline inference script running `llama3-70b-8192` via the OpenAI client, the agent achieved the following deterministic scores:
* **Easy:** 0.83 / 1.0 (Fixed code, missed one label)
* **Medium:** 1.0 / 1.0 (Downgraded dependency, caught duplicates)
* **Hard:** 1.0 / 1.0 (Successfully traced multi-file bug to database layer)

*Note: The environment successfully utilizes strict Pydantic Literal typing to catch and penalize LLM hallucinations (e.g., inventing invalid issue labels) during inference, proving its robustness as an evaluation framework.*