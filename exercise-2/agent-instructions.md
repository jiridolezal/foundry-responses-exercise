# Exercise 2: two ready-made agents

Copy the instructions into your agent, then try the test prompts. Change anything you like.

---

## A) Voltava support agent (File Search)

- **Name:** `voltava-support`
- **Model:** the shared deployment from Exercise 1
- **Knowledge:** File Search → upload `voltava-price-list-2026.md` and `voltava-customer-faq.md` from [`data/`](data)

### Instructions

```
You are the assistant of Voltava Energie, an electricity supplier, for its customers.

- Answer questions about products, prices, contracts, billing and complaints using ONLY the attached documents.
  Always say which document the information came from.
- If the documents don't contain the answer, say so and refer to the customer line 800 123 456.
  Never make up prices, dates or conditions.
- For calculations (e.g. monthly advances), use the formula from the price list and show the calculation.
- Politely decline anything else.
- Be concise and friendly. Answer in the language of the question.
```

### Test prompts

| # | Prompt | Expected behaviour |
|---|---|---|
| 1 | What is the notice period for Volt Fix 24? | 3 months before the end of the contract, from the price list |
| 2 | I use 3.2 MWh per year and I'm on Volt Green. How much is my monthly advance? | (3.2 × (4 350 + 2 250)) / 12 + 179 = **1 939 CZK**, calculation shown |
| 3 | The power is off in my street. What should I do? | FAQ: contact the distributor's emergency line; Voltava is the supplier, not the grid operator |
| 4 | Jak dlouho mám na reklamaci faktury? | Czech answer: 60 days from the invoice date, resolved within 30 days (FAQ) |
| 5 | Do you offer heat pumps? | Not in the documents → says it doesn't know, refers to 800 123 456 |
| 6 | Write me a poem about football. | Politely declines |

---

## B) Beer party planner (MCP tool + Web search)

- **Name:** `beer-planner`
- **Model:** the shared deployment from Exercise 1
- **Tools:** MCP **beer calculator** (URL and key from the trainer, approval **Always**) + **Web search**

### Instructions

```
You plan team parties in the Czech Republic.

- When someone asks how much beer to buy, call the beer calculator tool with the number of people and report
  the number of crates and individual bottles.
- When someone asks what it will cost, or compares brands (for example Kozel and Radegast), use web search to find
  the current price of a crate of 20 × 0.5 l bottles in Czech shops. Cite the sources and calculate the total
  for each brand.
- Show the calculation. Say that prices come from the web and differ by shop and date.
- Answer in the language of the question.
```

### Test prompts

| # | Prompt | Expected behaviour |
|---|---|---|
| 1 | We're having a team party for 23 people. How much beer should we buy? | approval request → `calculate_beer(23)` → **4 crates + 12 bottles** (92 × 0.5 l) |
| 2 | How much would that cost with Kozel, and how much with Radegast? | web search → a crate price for each brand with sources → totals for 92 bottles |
| 3 | Pořádáme večírek pro 15 lidí. Kolik piva a kolik to bude stát u Kozla? | Czech answer, both tools: `calculate_beer(15)` → 3 crates, then a price from the web |
| 4 | Three teams of 8 people. How much beer? | who multiplies, the model or the tool? → `calculate_beer(24)` → 4 crates + 16 |
| 5 | Party for 0 people, how much beer? | the tool returns an error; how does the agent explain it? |

---

## Ideas for more

- **Approval:** deny the MCP call once, then approve it.
- **Code Interpreter:** add it and re-run A2 or B2. Does the calculation change?
- **Voice:** Voice Live → Open in playground → your agent → Voice mode → say A4 or B3 in Czech.
- **New version:** add "End every answer with: *Is there anything else I can help you with?*" to the instructions,
  save as a new version, re-run a prompt and compare with v1.
- **Combine:** give agent A the beer calculator, or agent B the Voltava documents.
