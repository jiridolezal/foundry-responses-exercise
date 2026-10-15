# Exercise 2: agent instructions and test prompts

## Agent

- **Name:** `voltava-support`
- **Model:** the shared deployment from Exercise 1
- **Knowledge:** File Search → upload the files from `data/`
- **Tool:** MCP **beer calculator** (one tool: `calculate_beer(number_of_people)`). Endpoint and key: on the exercise
  sheet. Set approval to **always** first, so you see the approval step.

## Instructions (paste into the agent)

```
You are the assistant of Voltava Energie, an electricity supplier, for customers and for employees.

- Answer questions about products, prices, contracts, billing and complaints using ONLY the attached documents.
  Always say which document the information came from.
- When someone plans a team event or party and asks how much beer to buy, use the beer calculator tool and
  report the number of crates and individual bottles.
- If the documents and tools don't contain the answer, say so and refer to the customer line 800 123 456.
  Never make up prices, dates or conditions.
- For calculations (e.g. monthly advances), use the formula from the price list and show the calculation.
- Politely decline anything else.
- Be concise and friendly. Answer in the language of the question.
```

## Test prompts

| # | Prompt | Expected behaviour |
|---|---|---|
| 1 | What is the notice period for Volt Fix 24? | 3 months before the end of the contract, from the price list (File Search) |
| 2 | I use 3.2 MWh per year and I'm on Volt Green. How much is my monthly advance? | (3.2 × (4 350 + 2 250)) / 12 + 179 = **1 939 CZK**, calculation shown |
| 3 | We're having a team party for 23 people. How much beer should we buy? | approval request → `calculate_beer(23)` → **4 crates + 12 individual beers** (92 × 0.5 l) |
| 4 | Pořádáme firemní večírek pro 10 lidí, kolik piva máme koupit? | Czech answer, `calculate_beer(10)` → 2 crates, 0 individual |
| 5 | The power is off in my street. What should I do? | FAQ: contact the distributor's emergency line; Voltava is the supplier, not the grid operator |
| 6 | How long do I have to file a complaint about my invoice? | 60 days from the invoice date, resolved within 30 days (FAQ) |
| 7 | Do you offer heat pumps? | Not in the documents → says it doesn't know, refers to 800 123 456 |
| 8 | Write me a poem about football. | Politely declines |
| 9 | Party for 0 people, how much beer? | the tool returns an error, the agent explains it |

## Variations

- **Trace:** for prompt 3, open the trace: which tool, which arguments, what came back, how many tokens.
- **Approval:** deny the call once, then approve it.
- **Another model:** switch the agent's model (e.g. `model-router` if available, or another deployment) and re-run prompts
  2 and 3; compare answers and the trace.
- **Voice:** Voice Live → Open in playground → this agent → Voice mode → say prompt 4 in Czech.
- **Code Interpreter:** add it, re-run prompt 2.
- **New version:** add "End every answer with: *Is there anything else I can help you with?*" to the instructions, save
  as a new version, re-run prompt 1 and compare with v1.
