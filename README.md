# Agentic Day 2 - Routing

Minimal LangGraph workflow demonstrating typed state, explicit routing logic, and tier-based paths.

## 🚀 Setup

1. Create and activate a Python environment (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Add an `.env` file with your OpenAI key:
   ```text
   OPENAI_API_KEY=sk-...your key...
   ```

   > Note: `.env` is excluded from git via `.gitignore`.

## ▶️ Run

```powershell
python app.py
```

## ✅ What it demonstrates

- A typed `SupportState` (`TypedDict`) tracked across the workflow
- Explicit, testable routing logic (`route_by_tier`) for `vip` vs `standard`
- LangGraph `StateGraph` wiring with conditional edges
- Optional LangChain `ChatOpenAI` usage in the VIP path (if `OPENAI_API_KEY` is set)

