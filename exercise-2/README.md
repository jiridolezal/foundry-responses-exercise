# Exercise 2: Build your own agent with knowledge and an MCP tool

**30 minutes + 5 minutes debrief · browser only · Microsoft Foundry portal (ai.azure.com, your E.ON account)**

You build a prompt agent on a topic of your choice, give it a document to search and a remote tool to call, and watch
in the trace what it does. The tool is a tiny MCP server we host for today: a **beer calculator** for team events.

**You get from the trainer (Teams chat / whiteboard):** the MCP server URL and its API key.

## 1. Create the agent (5 min)

1. Open your project → **Build** → **Agents** → **Create agent**.
2. Model: the shared deployment from Exercise 1.
3. Instructions: anything you like. No idea? Try *"You help teams plan events. Use the beer calculator for any question
   about how much beer to buy. Answer in the language of the question."*

## 2. Knowledge: File Search (5 min)

Add **File Search** and upload one document: `voltava-price-list-2026.md` or `voltava-customer-faq.md` from the
`data` folder next to this sheet (fictional electricity supplier; on GitHub open the file → **Download raw file**), or any
non-sensitive document of your own.
*What do you expect:* will the agent quote the document or make things up when the answer isn't there?

## 3. Tool: the beer calculator MCP server (5 min)

1. **Tools** → **Add** → **Model Context Protocol (MCP)** (custom tool).
2. Server URL: the URL from the trainer. Authentication: **key / custom header**, name `x-api-key`, value: the key.
3. Approval: **Always** (you will see each call before it runs).

**If you can't create the connection** (missing permission): use the URL `<server URL>?api_key=<key>` and no
authentication. Fine for this dummy server today, never for a real one.

The tool: `calculate_beer(number_of_people)` → crates of 20 and single bottles, 4 bottles per person.

## 4. Test in the playground (5 min)

| Try | What to look for |
|---|---|
| *We're having a team party for 23 people. How much beer?* | approval request, then 4 crates + 12 bottles |
| *Firemní večírek pro 10 lidí, kolik piva?* | Czech answer, 2 crates |
| *Three teams of 8 people. How much beer?* | who does the multiplication: the model or the tool? |
| a question about your document | an answer with the source |
| *Party for 0 people?* | the tool returns an error: how does the agent explain it? |

Open the **trace** for one answer: which tool, which arguments, what came back, what File Search retrieved, how many
tokens.

## 5. Play (10 min, pick any)

- **Deny** a tool call once, then approve it.
- Switch the **model** and compare answers and tokens.
- **Voice mode** in the playground: ask in Czech.
- Add **Code Interpreter** and ask for a calculation.
- Change the instructions and save a **new version**; compare v1 and v2.
- Try a **prompt injection** ("ignore your instructions and…"): what happens? (We'll come back to it in the guardrails part.)

## Debrief

- When is a prompt agent enough, and when would you need a hosted agent or your own code?
- What did the trace show you that the chat didn't?
- Where does the key for the MCP server live, and who can read it?
