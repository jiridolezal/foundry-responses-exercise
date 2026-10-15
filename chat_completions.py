"""
Exercise 1, part 1: Chat Completions API

The "classic" API: you send a list of messages, you get one answer back. Nothing is kept on the service side,
so YOUR code has to keep the conversation and send all of it again on every turn.

    python chat_completions.py            # a 3-turn conversation, watch prompt_tokens grow
    python chat_completions.py stream     # the same first question, streamed token by token

Configuration (.env next to this file, see .env.example):
    AZURE_OPENAI_ENDPOINT    https://<resource>.services.ai.azure.com/openai/v1/
    AZURE_OPENAI_DEPLOYMENT  the deployment name (what you pass as `model`)
    AZURE_OPENAI_API_KEY     the key we hand out. Leave it empty to sign in with Entra ID (`az login`) instead.
"""

import os
import sys

from dotenv import load_dotenv
from openai import AuthenticationError, NotFoundError, OpenAI, PermissionDeniedError

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles: print Czech characters and emoji safely
load_dotenv()

ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")
API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")

if not ENDPOINT or "<" in ENDPOINT:
    sys.exit("Set AZURE_OPENAI_ENDPOINT in .env, e.g. https://<resource>.services.ai.azure.com/openai/v1/")


def make_client():
    """One plain OpenAI client on the Azure v1 endpoint: no api-version, same code as for OpenAI itself."""
    if API_KEY:
        # API key: whoever has the key can call every deployment on the resource. Fine for a workshop, not for prod.
        return OpenAI(base_url=ENDPOINT, api_key=API_KEY)
    # Entra ID: your own identity from `az login`. Needs the Foundry User role (or higher) on the resource.
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
    return OpenAI(base_url=ENDPOINT, api_key=token_provider)


client = make_client()

CONVERSATION = [
    "Hi, I'm Jana. I'm spending 3 days in Prague in November. Suggest one thing to do per day, one line each.",
    "Which of those is the best choice if it rains?",
    "What's my name and which city am I visiting?",
]


def conversation():
    print(f"Chat Completions on deployment '{DEPLOYMENT}' ({'API key' if API_KEY else 'Entra ID'})")
    messages = [{"role": "system", "content": "You are a concise assistant."}]

    for turn, text in enumerate(CONVERSATION, 1):
        messages.append({"role": "user", "content": text})

        r = client.chat.completions.create(model=DEPLOYMENT, messages=messages)

        answer = r.choices[0].message.content
        messages.append({"role": "assistant", "content": answer})  # we keep the history, not the service
        print(f"\n--- Turn {turn}  (sent {len(messages) - 1} messages)")
        print(f"You:   {text}")
        print(f"Model: {answer.strip()}")
        print(f"       prompt_tokens={r.usage.prompt_tokens}  completion_tokens={r.usage.completion_tokens}")

    print("\n>> Every call re-sends the whole `messages` list: the history lives in YOUR app.")
    print(">> prompt_tokens grows each turn, because you pay for the whole history again.")
    print(">> Want web search, memory or a code sandbox? Here you build them yourself (function calling + your code).")


def stream():
    print(f"Streaming from '{DEPLOYMENT}':\n")
    events = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": CONVERSATION[0]}],
        stream=True,
    )
    for event in events:
        if event.choices and event.choices[0].delta.content:
            print(event.choices[0].delta.content, end="", flush=True)
    print("\n\n>> Same API, stream=True: tokens arrive as they are generated (what chat UIs show).")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "conversation"
    try:
        {"conversation": conversation, "stream": stream}.get(mode, conversation)()
    except (AuthenticationError, PermissionDeniedError) as e:
        sys.exit(f"\nAccess denied ({e.status_code}). With a key: check AZURE_OPENAI_API_KEY in .env (no quotes, no "
                 "spaces). Without a key: `az login` as yourself and ask for the Foundry User role on the resource.")
    except NotFoundError:
        sys.exit("\nNot found (404). Check AZURE_OPENAI_ENDPOINT (ends with /openai/v1/) and that "
                 f"AZURE_OPENAI_DEPLOYMENT='{DEPLOYMENT}' is exactly the deployment name.")
