<h1 align="center">Attest</h1>
<p align="center"><strong>Test your AI agents like you test your code.</strong></p>

<p align="center">
  <a href="https://pypi.org/project/attest-ai/"><img src="https://img.shields.io/pypi/v/attest-ai?label=PyPI&color=0F766E" alt="PyPI"></a>
  <a href="https://www.npmjs.com/package/@attest-ai/core"><img src="https://img.shields.io/npm/v/@attest-ai/core?label=npm&color=0F766E" alt="npm"></a>
  <a href="https://github.com/attest-framework/attest/blob/main/LICENSE"><img src="https://img.shields.io/github/license/attest-framework/attest?color=0F766E" alt="License"></a>
</p>

---

**Turn a real run or incident into a verified fixture, replay it in pull-request CI with zero model calls, and gate the merge on pass / fail / not evaluated (with the reason).** `attest capture` records the run; PR CI replays your agent's real code against it and sends the result to a policy gate, in Python and TypeScript. An outage of a judge or provider is reported as *not evaluated*, never as green. [Refund Desk](https://github.com/attest-framework/refund-desk) walks the whole path end to end on one synthetic double-refund incident (INC-1042): incident, trace check, capture, failing replay, merged fix, blocked regression, outage, mutation score, drafted contract, viewer.

---

Attest is an open-source testing framework for AI agents. It provides an **8-layer assertion pipeline** — deterministic checks first, LLM-as-judge only when necessary — delivering fast, reliable, cost-effective test suites for any agent framework.

### The Problem

AI agent testing today is either manual spot-checking or expensive LLM-as-judge on every assertion. Most teams default to `assert "keyword" in response` and hope for the best.

### The Solution

Attest introduces **graduated assertions**: validate schema for free, check constraints for free, verify trace structure for free — and only call an LLM judge when cheaper layers can't prove your point.

```
Layer 1  Schema         ── JSON Schema validation           ── free
Layer 2  Constraint     ── cost, latency, token budgets     ── free
Layer 3  Trace          ── tool ordering, required steps    ── free
Layer 4  Content        ── regex, keywords, substring       ── free
Layer 5  Embedding      ── semantic similarity              ── ~$0.001/call
Layer 6  LLM Judge      ── rubric-based evaluation          ── ~$0.01+/call
Layer 7  Trace Tree     ── multi-agent delegation tracking  ── free
Layer 8  Plugin         ── custom evaluation logic          ── free
```

Layers 1–4, 7–8 are deterministic and free. Use layers 5–6 only when you need semantic understanding.

---

### Key Features

**Framework agnostic** — 10 adapters: OpenAI, Anthropic, Gemini, Ollama, LangChain, LlamaIndex, Google ADK, CrewAI, OpenTelemetry, and manual instrumentation.

**Fluent assertion DSL** — chain assertions naturally across all 8 layers in a single expression.

**Native test integration** — pytest plugin (Python) and Vitest plugin (TypeScript). No new test runner to learn.

**Multi-agent support** — trace trees, delegation depth tracking, cross-agent data flow assertions, aggregate cost budgets across agent networks.

**Cost as a first-class metric** — per-assertion cost tracking, budget limits, cost reports, tiered sampling strategies for CI.

**Simulation mode** — run full test suites with zero API calls during development. Mock tools, simulated personas, deterministic replay.

**Go engine** — JSON-RPC 2.0 subprocess handles evaluation at native speed. The SDKs communicate via NDJSON over stdio.

---

## Get Started — Python

```bash
uv init --bare my-agent-tests && cd my-agent-tests   # skip when you already have a project
uv add "attest-ai>=1.0.0rc1" pytest
```

```python
from attest import agent, expect, TraceBuilder

@agent("support-bot")
def support_bot(builder: TraceBuilder, query: str) -> dict:
    builder.add_llm_call(
        name="gpt-4",
        args={"messages": [{"role": "user", "content": query}]},
        result={"response": "Your refund has been processed."},
    )
    builder.add_tool_call(
        name="process_refund",
        args={"order_id": "ORD-123"},
        result={"refund_id": "RFD-001", "status": "processed"},
    )
    builder.set_metadata(total_tokens=150, cost_usd=0.005, latency_ms=800)
    return {"message": "Refund processed", "refund_id": "RFD-001"}


def test_support_bot(attest):
    result = support_bot(query="I need a refund for order ORD-123")

    chain = (
        expect(result)
        .output_matches_schema({
            "type": "object",
            "required": ["refund_id"],
            "properties": {"refund_id": {"type": "string"}},
        })
        .cost_under(0.01)
        .latency_under(2000)
        .tools_called_in_order(["process_refund"])
        .forbidden_tools(["delete_account"])
        .output_contains("processed")
    )

    attest.evaluate(chain)
```

```bash
uv run pytest -v
```

## Get Started — TypeScript

```bash
npm install -D "@attest-ai/core@>=1.0.0-rc.1" "@attest-ai/vitest@>=1.0.0-rc.1" "vitest@^4"
```

```typescript
import { agent, attestExpect, TraceBuilder, Agent } from "@attest-ai/core";
import { useAttest, evaluate } from "@attest-ai/vitest";
import { describe, it } from "vitest";

@agent("support-bot")
class SupportBot implements Agent {
  async invoke(builder: TraceBuilder, query: string) {
    builder.addLlmCall({
      name: "gpt-4",
      args: { messages: [{ role: "user", content: query }] },
      result: { response: "Your refund has been processed." },
    });
    builder.addToolCall({
      name: "process_refund",
      args: { order_id: "ORD-123" },
      result: { refund_id: "RFD-001", status: "processed" },
    });
    builder.setMetadata({ total_tokens: 150, cost_usd: 0.005, latency_ms: 800 });
    return { message: "Refund processed", refund_id: "RFD-001" };
  }
}

describe("support bot", () => {
  it("processes refunds within budget", async (ctx) => {
    const attest = useAttest(ctx);
    const bot = new SupportBot();
    const result = await bot.invoke("Refund order ORD-123");

    const chain = attestExpect(result)
      .outputMatchesSchema({
        type: "object",
        required: ["refund_id"],
        properties: { refund_id: { type: "string" } },
      })
      .costUnder(0.01)
      .latencyUnder(2000)
      .toolsCalledInOrder(["process_refund"])
      .forbiddenTools(["delete_account"])
      .outputContains("processed");

    await evaluate(chain, attest);
  });
});
```

```bash
npx vitest
```

---

## Assertion DSL Reference

| Layer | Python | TypeScript | Cost |
|-------|--------|------------|------|
| **Schema** | `.output_matches_schema(schema)` | `.outputMatchesSchema(schema)` | Free |
| **Constraint** | `.cost_under(0.01)` `.latency_under(5000)` `.tokens_under(500)` | `.costUnder(0.01)` `.latencyUnder(5000)` `.tokensUnder(500)` | Free |
| **Trace** | `.tools_called_in_order([...])` `.required_tools([...])` `.forbidden_tools([...])` | `.toolsCalledInOrder([...])` `.requiredTools([...])` `.forbiddenTools([...])` | Free |
| **Content** | `.output_contains("x")` `.output_matches_regex(r"...")` `.output_has_all_keywords([...])` | `.outputContains("x")` `.outputMatchesRegex(/.../)`  `.outputHasAllKeywords([...])` | Free |
| **Embedding** | `.output_similar_to("ref", threshold=0.8)` | `.outputSimilarTo("ref", { threshold: 0.8 })` | ~$0.001 |
| **Judge** | `.passes_judge("criteria", threshold=0.8)` | `.passesJudge("criteria", { threshold: 0.8 })` | ~$0.01+ |
| **Trace Tree** | `.agent_called("id")` `.delegation_depth(3)` `.aggregate_cost_under(0.05)` | `.agentCalled("id")` `.delegationDepth(3)` `.aggregateCostUnder(0.05)` | Free |

---

## Adapters

Drop-in tracing for your existing agent framework — no code changes to your agent logic.

| Adapter | Python | TypeScript |
|---------|--------|------------|
| OpenAI | `OpenAIAdapter` | `OpenAIAdapter` |
| Anthropic | `AnthropicAdapter` | `AnthropicAdapter` |
| Google Gemini | `GeminiAdapter` | `GeminiAdapter` |
| Ollama | `OllamaAdapter` | `OllamaAdapter` |
| LangChain | `LangChainAdapter` | `LangChainAdapter` |
| LlamaIndex | `LlamaIndexInstrumentationHandler` | — |
| Google ADK | `GoogleADKAdapter` | — |
| CrewAI | `CrewAIAdapter` | — |
| OpenTelemetry | `OTelAdapter` | `OTelAdapter` |
| Manual | `ManualAdapter` | `ManualAdapter` |

---

## Repositories

| Repository | Description |
|------------|-------------|
| [`attest`](https://github.com/attest-framework/attest) | Core framework — Go engine, Python SDK, TypeScript SDK, pytest + Vitest plugins |
| [`attest-examples`](https://github.com/attest-framework/attest-examples) | 25 small, copyable examples — one per feature or framework, in Python and TypeScript |
| [`refund-desk`](https://github.com/attest-framework/refund-desk) | The end-to-end demo: one incident from first report to a merge gate that blocks its regression |
| [`attest-framework.github.io`](https://github.com/attest-framework/attest-framework.github.io) | Source of the documentation site at [attest-framework.github.io](https://attest-framework.github.io/) — guides, API reference, architecture docs |

---

<p align="center">
  <a href="https://attest-framework.github.io/">Documentation</a> · <a href="https://github.com/attest-framework/attest-examples">Examples</a> · <a href="https://pypi.org/project/attest-ai/">PyPI</a> · <a href="https://www.npmjs.com/package/@attest-ai/core">npm</a>
</p>
<p align="center">Apache-2.0 License</p>
