# Exercise 2: Build an agent in the Foundry portal and try everything you can

**30 minutes + 5 minutes debrief · browser only · Microsoft Foundry portal (ai.azure.com, your E.ON account)**

The goal is to **explore**: create a prompt agent in the portal, test it in the playground, and switch on as many
features as you can (knowledge, tools, approvals, voice, versions…). Build anything you like. No idea? Pick one of the
two ready-made agents below; their instructions and test prompts are in [`agent-instructions.md`](agent-instructions.md).

**You get from the trainer (Teams chat):** the URL and the API key of the beer-calculator MCP server (agent B).

## 1. Open your project (2 min)

[ai.azure.com](https://ai.azure.com) → sign in with your E.ON account → make sure the **New Foundry** toggle is on →
open your own project (`<surname>-ws`).

## 2. Create an agent (3 min)

**Build** → **Agents** → **Create agent** → give it a name → model: the shared deployment from Exercise 1 → paste
instructions. Then pick one:

| | **A) Voltava support agent** | **B) Beer party planner** |
|---|---|---|
| What it does | Answers customer questions about a fictional electricity supplier from its documents | Works out how much beer a team party needs and what it costs, Kozel vs. Radegast |
| Knowledge | **File Search** with the two files in [`data/`](data) | – |
| Tools | – (add Code Interpreter later for calculations) | **MCP**: the beer calculator + **Web search** for current prices |
| Instructions and test prompts | [`agent-instructions.md`](agent-instructions.md) → A | [`agent-instructions.md`](agent-instructions.md) → B |

### A) File Search

Download both files from [`data/`](data) (on GitHub: open the file → **Download raw file**):
`voltava-price-list-2026.md` and `voltava-customer-faq.md`. In the agent, add **File Search** and upload them. You can
also upload any non-sensitive document of your own.

### B) The beer calculator (MCP) and Web search

1. **Tools** → **Add** → **Model Context Protocol (MCP)** (custom).
   Server URL: from the trainer. Authentication: **key / custom header**, name `x-api-key`, value: the key.
   Approval: **Always** (you see each call before it runs).
2. **Tools** → **Add** → **Web search**.

The beer tool is `calculate_beer(number_of_people)`: 4 bottles per person, returned as crates of 20 and single bottles.

**Can't create the MCP connection?** Use the URL `<server URL>?api_key=<key>` and no authentication. Fine for this
dummy server today, never for a real one.

## 3. Test it in the playground (10 min)

Use the test prompts from [`agent-instructions.md`](agent-instructions.md). **Before each one, guess** what the agent
will do. Look at:

- **Which tool ran:** File Search, the MCP call (with its arguments and result) or Web search, and when.
- **Sources:** does the answer cite the document or the web page it came from?
- **Unknown answers:** does the agent say "I don't know", or does it make something up?
- **Approval:** the MCP call waits for you. What exactly are you approving?

## 4. Explore (15 min, as many as you can)

- **Deny** an MCP call once, then approve it. What does the agent say?
- Add the **other agent's** knowledge or tools: File Search to B, the beer calculator to A.
- Add **Code Interpreter** and ask for a calculation (a monthly advance, the price per person).
- **Voice mode:** talk to your agent in Czech (Voice Live → Open in playground → your agent → Voice mode → Start session).
- Change the instructions and save a **new version**. Compare v1 and v2 with the same prompt.
- Switch **Web search** off and ask about prices again.
- Try a **prompt injection** ("ignore your instructions and…") or ask something off-topic. We'll come back to it in
  the guardrails part.
- Click around: Tools catalog, Knowledge, Evaluations, the agent's code view. What would you use in your team?

**Not possible in this workshop environment** (your role is Foundry User + Foundry Project Manager on your project):
deploying models, changing content filters, publishing the agent to Teams / Microsoft 365, and traces (no Application
Insights is connected). The trainer shows these in the demos.

## Debrief

- When is a prompt agent enough, and when would you need a hosted agent or your own code?
- Which feature surprised you, and which one would you use first?
- Where does the key for the MCP server live, and who can read it? Where did the web search query go?

## If something goes wrong

| You see | Fix |
|---|---|
| You don't see your project | Check the **New Foundry** toggle and that you're signed in with your E.ON account; ask the trainer |
| Error when saving the MCP tool / connection | Use the `?api_key=` URL fallback above |
| MCP call fails or times out | Check the URL (it ends with `/mcp`) and the key; tell the trainer |
| Web search isn't offered or is refused | Skip it; the beer calculator still works |
| Voice mode doesn't start | Allow the microphone in the browser; if it still fails, skip it |
