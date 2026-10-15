"""
Exercise 1, part 2: Responses API

The newer API that Agent Service is built on. Same model, same deployment as part 1, but the service can keep the
conversation for you and run built-in tools (web search, code, MCP servers) on its side.

Run one variant at a time and compare with chat_completions.py:

    python responses_api.py basic        # one call: input -> output_text, usage
    python responses_api.py memory       # conversation state on the service: previous_response_id
    python responses_api.py stateless    # store=False: nothing kept, so you send the history yourself
    python responses_api.py web          # the same question without and with the web_search tool
    python responses_api.py code         # code interpreter: the model writes and runs Python in a sandbox
    python responses_api.py mcp          # a remote MCP server as a tool (Microsoft Learn docs, no auth)
    python responses_api.py reasoning    # reasoning effort low vs. high: reasoning tokens and time
    python responses_api.py json         # structured output: an answer that must match your JSON schema
    python responses_api.py background   # background mode: start, poll, collect later
    python responses_api.py conversation # Conversations API (only with Entra ID + project endpoint, see .env)
    python responses_api.py all          # everything above except conversation

Configuration (.env next to this file, see .env.example):
    AZURE_OPENAI_ENDPOINT    https://<resource>.services.ai.azure.com/openai/v1/
    AZURE_OPENAI_DEPLOYMENT  the deployment name (what you pass as `model`)
    AZURE_OPENAI_API_KEY     the key we hand out. Leave it empty to sign in with Entra ID (`az login`) instead.
"""

import json
import os
import sys
import time

from dotenv import load_dotenv
from openai import AuthenticationError, BadRequestError, NotFoundError, OpenAI, OpenAIError, PermissionDeniedError

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles: print Czech characters and emoji safely
load_dotenv()

ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")
API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
PROJECT_ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")

if not ENDPOINT or "<" in ENDPOINT:
    sys.exit("Set AZURE_OPENAI_ENDPOINT in .env, e.g. https://<resource>.services.ai.azure.com/openai/v1/")


def make_client(base_url=ENDPOINT):
    """One plain OpenAI client on the Azure v1 endpoint: no api-version, same code as for OpenAI itself."""
    if API_KEY and base_url == ENDPOINT:
        # API key: whoever has the key can call every deployment on the resource. Fine for a workshop, not for prod.
        return OpenAI(base_url=base_url, api_key=API_KEY)
    # Entra ID: your own identity from `az login`. Needs the Foundry User role (or higher) on the resource.
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
    return OpenAI(base_url=base_url, api_key=token_provider)


client = make_client()


def header(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def usage(r):
    u = r.usage
    reasoning = getattr(u.output_tokens_details, "reasoning_tokens", 0) if u.output_tokens_details else 0
    return f"input_tokens={u.input_tokens}  output_tokens={u.output_tokens} (reasoning {reasoning})"


def output_types(r):
    """What the service did, in order: reasoning, web_search_call, code_interpreter_call, mcp_call, message..."""
    return " -> ".join(item.type for item in r.output)


CONVERSATION = [
    "Hi, I'm Jana. I'm spending 3 days in Prague in November. Suggest one thing to do per day, one line each.",
    "Which of those is the best choice if it rains?",
    "What's my name and which city am I visiting?",
]


# ---------------------------------------------------------------------------------------------------------------
def basic():
    header("basic: one call. `input` instead of `messages`, `instructions` instead of a system message")
    r = client.responses.create(
        model=DEPLOYMENT,
        instructions="You are a concise assistant.",
        input="Explain the difference between kW and kWh in two sentences.",
    )
    print(r.output_text)
    print(f"\n[id={r.id}  status={r.status}  {usage(r)}]")
    print(f"[output items: {output_types(r)}]")
    print(">> The response has an id: by default the service stores it (30 days), so you can continue from it.")


def memory():
    header("memory: the SERVICE keeps the conversation. You send only the new message + previous_response_id")
    previous_id = None
    for turn, text in enumerate(CONVERSATION, 1):
        r = client.responses.create(
            model=DEPLOYMENT,
            instructions="You are a concise assistant.",
            input=text,
            previous_response_id=previous_id,  # None on the first turn
        )
        print(f"\n--- Turn {turn}  (sent 1 message + previous_response_id)")
        print(f"You:   {text}")
        print(f"Model: {r.output_text.strip()}")
        print(f"       {usage(r)}")
        previous_id = r.id
    print("\n>> You send less, but input_tokens still grows: the earlier turns are still read and billed.")
    print(">> This is short-term memory (one conversation). Long-term memory across sessions is an agent feature.")


def stateless():
    header("stateless: store=False. Nothing is kept on the service, so you manage the history (like Chat Completions)")
    history = []
    for turn, text in enumerate(CONVERSATION[:2], 1):
        history.append({"role": "user", "content": text})
        r = client.responses.create(model=DEPLOYMENT, input=history, store=False)
        history += [item.model_dump(exclude_none=True) for item in r.output if item.type == "message"]
        print(f"\n--- Turn {turn}  (sent {len(history) - 1} items)")
        print(f"Model: {r.output_text.strip()}")
        print(f"       {usage(r)}")

    print("\nNow try to continue from that unstored response by id:")
    try:
        client.responses.create(model=DEPLOYMENT, input="And in Czech?", previous_response_id=r.id)
        print("  It worked (unexpected).")
    except OpenAIError as e:
        print(f"  Fails, as expected: {getattr(e, 'status_code', '')} {type(e).__name__}")
    print(">> store=False = zero data retention on the service side, but no previous_response_id and no background.")


def web():
    header("web: the same question without and with the web_search tool")
    question = "What were the most important energy news in the Czech Republic this week? Two bullets, with sources."

    r = client.responses.create(model=DEPLOYMENT, input=question)
    print("WITHOUT tools:")
    print(r.output_text.strip())
    print(f"[{output_types(r)} | {usage(r)}]")

    r = client.responses.create(
        model=DEPLOYMENT,
        input=question,
        tools=[{"type": "web_search"}],  # remove this line and you are back to the model's training data
    )
    print("\nWITH web_search:")
    print(r.output_text.strip())
    citations = [a.url for item in r.output if item.type == "message"
                 for part in item.content for a in (getattr(part, "annotations", None) or [])]
    searches = (r.model_dump().get("tool_usage") or {}).get("web_search", {}).get("num_requests")
    print(f"[{output_types(r)} | {usage(r)} | Bing requests billed: {searches}]")
    print("Citations:", *sorted(set(citations)) or ["(none)"], sep="\n  ")
    print("\n>> The service ran the search (Grounding with Bing) and gave the results to the model:")
    print(">> compare input_tokens with the call without tools. Search results are billed as input.")
    print(">> Data goes to Bing, outside the Azure compliance boundary; admins can switch it off per subscription.")


def code():
    header("code: code interpreter. The model writes Python and the service runs it in a sandbox container")
    r = client.responses.create(
        model=DEPLOYMENT,
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
        input=("A household uses 3.2 MWh of electricity per year. Energy costs 4,350 CZK/MWh, distribution "
               "2,250 CZK/MWh and the fixed fee is 179 CZK per month. Compute the monthly advance with Python "
               "and round it to whole CZK."),
    )
    for item in r.output:
        if item.type == "code_interpreter_call":
            print("Code the model ran:\n" + "\n".join("    " + line for line in (item.code or "").splitlines()))
    print("\n" + r.output_text.strip())
    print(f"\n[{output_types(r)} | {usage(r)}]")
    print(">> Exact arithmetic instead of a guess. The sandbox is billed per session (on top of tokens).")


def mcp():
    header("mcp: a remote MCP server as a tool. Here: Microsoft Learn docs (public, no auth)")
    r = client.responses.create(
        model=DEPLOYMENT,
        tools=[{
            "type": "mcp",
            "server_label": "microsoft_learn",
            "server_url": "https://learn.microsoft.com/api/mcp",
            "require_approval": "never",  # default is "always": you approve every call before data leaves
        }],
        input="According to Microsoft Learn, how long are stored Azure OpenAI responses retained by default? "
              "One sentence.",
    )
    for item in r.output:
        if item.type == "mcp_list_tools":
            print("Tools the server offered:", ", ".join(t.name for t in item.tools))
        elif item.type == "mcp_call":
            print(f"Called: {item.name}({item.arguments})")
    print("\n" + r.output_text.strip())
    print(f"\n[{output_types(r)} | {usage(r)}]")
    print(">> Look at input_tokens: everything the tool returned went into the model's context, and you pay for it.")
    print(">> Your own MCP server works the same way; add auth with \"headers\": {\"Authorization\": \"Bearer ...\"}.")


def reasoning():
    header("reasoning: the same question with reasoning effort low vs. high")
    question = ("A heat pump uses 2.8 kWh of electricity to deliver 10 kWh of heat. Electricity costs 6.2 CZK/kWh, "
                "gas heating costs 2.1 CZK per kWh of heat. Which is cheaper per 10 kWh of heat and by how much?")
    for effort in ("low", "high"):
        start = time.perf_counter()
        r = client.responses.create(model=DEPLOYMENT, input=question, reasoning={"effort": effort})
        print(f"\n--- effort={effort}  ({time.perf_counter() - start:.1f} s)  {usage(r)}")
        print(r.output_text.strip()[:400])
    print("\n>> Reasoning tokens are billed as output tokens, but you never see them.")


def structured():
    header("json: structured output. The answer must match your JSON schema (no 'please return JSON' prompting)")
    schema = {
        "type": "object",
        "properties": {
            "customer_id": {"type": ["string", "null"]},
            "intent": {"type": "string", "enum": ["outage", "billing", "contract_change", "complaint", "other"]},
            "postal_code": {"type": ["string", "null"]},
            "urgent": {"type": "boolean"},
            "summary": {"type": "string"},
        },
        "required": ["customer_id", "intent", "postal_code", "urgent", "summary"],
        "additionalProperties": False,
    }
    email = ("Dobrý den, jsem váš zákazník číslo 1042. Od rána nám v Praze 4 (PSČ 140 00) nejde proud "
             "a máme doma lednici s léky. Kdy to opravíte? Jana Nováková")
    r = client.responses.create(
        model=DEPLOYMENT,
        instructions="Extract the fields from the customer e-mail.",
        input=email,
        text={"format": {"type": "json_schema", "name": "ticket", "schema": schema, "strict": True}},
    )
    print(json.dumps(json.loads(r.output_text), indent=2, ensure_ascii=False))
    print(">> In Chat Completions the same thing is `response_format`; in Responses it's `text.format`.")


def background():
    header("background: start a long task, get an id back immediately, poll for the result")
    r = client.responses.create(
        model=DEPLOYMENT,
        input="Write a 150-word explanation of how the electricity grid balances supply and demand.",
        background=True,
    )
    print(f"Submitted {r.id}, status={r.status}")
    while r.status in ("queued", "in_progress"):
        time.sleep(2)
        r = client.responses.retrieve(r.id)
        print(f"  ... status={r.status}")
    print("\n" + r.output_text.strip())
    print(">> No open connection while the model works. Needs store=True (the default).")


def conversation():
    header("conversation: a durable conversation object (what Agent Service uses under the hood)")
    if API_KEY or not PROJECT_ENDPOINT or "<" in PROJECT_ENDPOINT:
        print("Skipped: Conversations live on the Foundry PROJECT endpoint, which accepts only Entra ID.")
        print("To try it: empty AZURE_OPENAI_API_KEY, set AZURE_AI_PROJECT_ENDPOINT, `az login`, Foundry User role.")
        return
    project = make_client(f"{PROJECT_ENDPOINT}/openai/v1/")
    conv = project.conversations.create(metadata={"exercise": "ex1"})
    print(f"Conversation {conv.id}")
    for text in CONVERSATION:
        r = project.responses.create(model=DEPLOYMENT, input=text, conversation=conv.id)
        print(f"\nYou:   {text}\nModel: {r.output_text.strip()}\n       {usage(r)}")
    items = list(project.conversations.items.list(conv.id, order="asc"))
    print(f"\nThe conversation holds {len(items)} items (messages, tool calls...) until you delete it.")
    project.conversations.delete(conv.id)


VARIANTS = {
    "basic": basic, "memory": memory, "stateless": stateless, "web": web, "code": code, "mcp": mcp,
    "reasoning": reasoning, "json": structured, "background": background, "conversation": conversation,
}

if __name__ == "__main__":
    print(f"Responses API on deployment '{DEPLOYMENT}' ({'API key' if API_KEY else 'Entra ID'})")
    wanted = []
    for arg in sys.argv[1:] or ["basic"]:
        wanted += [v for v in VARIANTS if v != "conversation"] if arg == "all" else [arg]
    for name in wanted:
        if name not in VARIANTS:
            sys.exit(f"Unknown variant '{name}'. Use one of: {', '.join(VARIANTS)}, all")
        try:
            VARIANTS[name]()
        except BadRequestError as e:
            # e.g. a tool switched off by the admin, or a parameter the deployed model doesn't support
            print(f"\n!! {name}: the service refused the request: {e}")
        except (AuthenticationError, PermissionDeniedError) as e:
            sys.exit(f"\nAccess denied ({e.status_code}). With a key: check AZURE_OPENAI_API_KEY in .env (no quotes, no "
                     "spaces). Without a key: `az login` as yourself and ask for the Foundry User role on the resource.")
        except NotFoundError:
            sys.exit("\nNot found (404). Check AZURE_OPENAI_ENDPOINT (ends with /openai/v1/) and that "
                     f"AZURE_OPENAI_DEPLOYMENT='{DEPLOYMENT}' is exactly the deployment name.")
