# Exercise 1: Chat Completions vs. Responses API

Same model, same deployment, two APIs. You run two short Python scripts and compare who keeps the conversation,
what you pay for, and what the service can do for you.

**Time:** 30 minutes + 5 minutes debrief. **You need:** the endpoint, deployment name and API key from the lecturer.

## 1. Setup (5 min)

**A) On your laptop** (Python 3.10 or newer):

```bash
git clone https://github.com/jiridolezal/foundry-responses-exercise.git   # or "Code → Download ZIP" and unzip
cd foundry-responses-exercise
pip install -r requirements.txt
cp .env.example .env                          # Windows: copy .env.example .env
```

**B) No Python or no pip on your laptop? Use Azure Cloud Shell** (browser only, Python is already there):
open [shell.azure.com](https://shell.azure.com) → **Bash** → if asked, choose **No storage account required**, then:

```bash
git clone https://github.com/jiridolezal/foundry-responses-exercise.git && cd foundry-responses-exercise
pip install --user -r requirements.txt        # a red "dependency resolver" warning about ansible is harmless
cp .env.example .env && code .env             # or: nano .env
```

Then fill in `.env` with the three values from the lecturer:

```
AZURE_OPENAI_ENDPOINT=https://<resource>.services.ai.azure.com/openai/v1/
AZURE_OPENAI_DEPLOYMENT=<deployment name>
AZURE_OPENAI_API_KEY=<key>
```

(No key? Leave `AZURE_OPENAI_API_KEY` empty and run `az login`: the scripts then use your Entra ID account, which
needs the **Foundry User** role on the resource.)

## 2. Chat Completions (5 min)

```bash
python chat_completions.py
python chat_completions.py stream
```

*Before you run it:* the third question is "What's my name?". How will the model know?
Watch `prompt_tokens` on each turn.

## 3. Responses API (20 min)

Run the variants one by one. **Before each one, guess what will happen.**

| Command | What to look at |
|---|---|
| `python responses_api.py basic` | `input` + `instructions` instead of `messages`; the response has an `id` |
| `python responses_api.py memory` | You send only the new message. Does `input_tokens` still grow? Why? |
| `python responses_api.py stateless` | `store=False`: what breaks? |
| `python responses_api.py web` | The same question without and with `web_search`: citations, `input_tokens` |
| `python responses_api.py code` | The Python code the model wrote and the service ran |
| `python responses_api.py mcp` | Which tools the MCP server offered, which one the model called, `input_tokens` |
| `python responses_api.py reasoning` | `reasoning` tokens for low vs. high effort |
| `python responses_api.py json` | A Czech e-mail turned into JSON that matches a schema |
| `python responses_api.py background` | `queued` → `in_progress` → `completed` without an open connection |
| *(Entra ID only)* `python responses_api.py conversation` | A conversation object that lives until you delete it |

Done early? Change something yourself in `responses_api.py`: your own question, a different `reasoning` effort,
`"require_approval": "always"` in the MCP tool, a `user_location` for web search, another field in the JSON schema.

## 4. Wrap-up: fill in

| | Chat Completions | Responses |
|---|---|---|
| Who keeps the conversation history? | | |
| What is stored on the service side, and for how long? | | |
| Is earlier context billed again on every turn? | | |
| Web search, code, MCP: who runs them? | | |
| What does Agent Service use? | | |

## If something goes wrong

| You see | Fix |
|---|---|
| `Access denied (401)` | The key in `.env` is wrong or has quotes/spaces around it |
| `Not found (404)` | The endpoint must end with `/openai/v1/`; the deployment name must match exactly |
| `429 Too Many Requests` | Everyone shares one deployment: wait 10 seconds and run it again |
| `!! web: the service refused the request` | Web search is switched off in this subscription: skip that variant |
| `ModuleNotFoundError` | `pip install -r requirements.txt` didn't run in this folder (Cloud Shell: add `--user`) |
