<h1 align="center">Attest</h1>
<p align="center"><strong>Test your AI agents like you test your code.</strong></p>

<p align="center">
  <a href="https://pypi.org/project/attest-ai/"><img src="https://img.shields.io/pypi/v/attest-ai?label=PyPI&color=0F766E" alt="PyPI"></a>
  <a href="https://www.npmjs.com/package/@attest-ai/core"><img src="https://img.shields.io/npm/v/@attest-ai/core?label=npm&color=0F766E" alt="npm"></a>
  <a href="https://github.com/attest-framework/attest/blob/main/LICENSE"><img src="https://img.shields.io/github/license/attest-framework/attest?color=0F766E" alt="License"></a>
</p>

---

**Record an incident, replay the agent's real code against its model recording, and apply a merge policy to the results.** In Python and TypeScript, `attest capture` records the run, applies redaction and drafts contracts. “Consistent with the recording” describes a fixture check, not proof of correct behavior: review the fixture and choose independent business invariants. Strict replay makes zero live model calls for matching requests; it removes live-model variability, not other sources of flaky tests. Checks report *pass*, *fail* or *not evaluated* with a reason. A missing judge verdict is *not evaluated*; it warns by default unless the policy blocks it. Requiring a blocking policy check in branch protection gates the covered regressions and removals, not every possible defect. [Refund Desk](https://github.com/attest-framework/refund-desk) demonstrates this with two synthetic incidents: INC-1042 (double refund after a timeout) and INC-1077 (over-refund and a confirmation sent to another customer).

---

Attest is an open-source testing framework for AI agents. It provides **six evaluated assertion layers plus plugins**, with deterministic checks before model-based evaluation. Supported adapters and their maturity tiers are listed below.

### The Problem

A reply can look correct even when an agent makes the wrong tool call or changes the wrong record. Tests can check the reply, the execution trace and the resulting state; a model judge can assess subjective criteria.

### The Solution

Attest introduces **graduated assertions**: validate schema for free, check constraints for free, verify trace structure for free — and only call an LLM judge when cheaper layers can't prove your point.

<!-- claims:layers:start -->
| Layer | Checks | Assertion types | Cost |
|-------|--------|-----------------|------|
| L1 Schema validation | Checks the output against a JSON Schema. | `schema` | Free |
| L2 Constraint checks | Checks cost, token, latency and step-count limits. | `constraint` | Free |
| L3 Trace and behavioral checks | Checks which tools ran, in which order, with which arguments, how often per business key, across the agent tree and against the world's final state. | `trace`, `trace_tree`, `effect` | Free |
| L4 Content pattern matching | Checks the output text against substrings, patterns and keywords. | `content` | Free |
| L5 Embedding similarity | Scores semantic similarity against a reference with an embedding model: OpenAI embeddings are paid, the local ONNX model is free. | `embedding` | Depends on provider |
| L6 LLM-as-judge | Scores the output against a rubric with a judge model: OpenAI, Anthropic and Gemini judges are paid, a local ACP agent or an OpenAI-compatible local endpoint is not. | `llm_judge` | Depends on provider |
| Plugins | Custom assertions that run in the SDK process; cost and determinism are the plugin's. | `plugin` | Plugin-defined |
<!-- claims:layers:end -->

L1–L4 are deterministic and free. L5–L6 depend on the provider you configure: use them only when you need semantic understanding.

---

### Key Features

**Framework agnostic** — adapters for OpenAI, Anthropic, Gemini, Ollama, LangChain, CrewAI, OpenTelemetry, Google ADK, LlamaIndex, and manual instrumentation; see [Adapters](#adapters) for per-SDK maturity.

**Fluent assertion DSL** — chain assertions naturally across the evaluated layers in a single expression.

**Native test integration** — pytest plugin (Python) and Vitest plugin (TypeScript). No new test runner to learn.

**Multi-agent support** — trace trees, delegation depth tracking, cross-agent data flow assertions, aggregate cost budgets across agent networks.

**Cost as a first-class metric** — per-assertion cost tracking, budget limits, cost reports, tiered sampling strategies for CI.

**Simulation mode** — run full test suites with zero API calls during development. Mock tools, simulated personas, deterministic replay.

**Go engine** — JSON-RPC 2.0 subprocess handles evaluation at native speed. The SDKs communicate via NDJSON over stdio.

---

## Get Started — Python

```bash
uv init --bare my-agent-tests && cd my-agent-tests   # skip when you already have a project
uv add attest-ai==1.1.0 pytest
```
Save the following as `test_support_bot.py`. The recorded calls are sample data; no model or payment API is called.


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
    return {
        "message": "Refund processed",
        "structured": {"refund_id": "RFD-001"},
    }


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
pnpm add -D @attest-ai/core@1.1.0 @attest-ai/vitest@1.1.0 vitest
```
Save the following as `support-bot.test.ts`. The recorded calls are sample data; no model or payment API is called.


```typescript
import { agent, attestExpect } from "@attest-ai/core";
import { evaluate } from "@attest-ai/vitest";
import { describe, it } from "vitest";

const supportBot = agent("support-bot", (builder, { query }) => {
    builder.addLlmCall("gpt-4", {
      args: { messages: [{ role: "user", content: query }] },
      result: { response: "Your refund has been processed." },
    });
    builder.addToolCall("process_refund", {
      args: { order_id: "ORD-123" },
      result: { refund_id: "RFD-001", status: "processed" },
    });
    builder.setMetadata({ total_tokens: 150, cost_usd: 0.005, latency_ms: 800 });
    return {
      message: "Refund processed",
      structured: { refund_id: "RFD-001" },
    };
});

describe("support bot", () => {
  it("processes refunds within budget", async () => {
    const result = supportBot({ query: "Refund order ORD-123" });

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

    await evaluate(chain);
  });
});
```

```bash
pnpm exec vitest run
```

---

## Assertion DSL Reference

| Layer | Python | TypeScript | Cost |
|-------|--------|------------|------|
| **Schema** | `.output_matches_schema(schema)` | `.outputMatchesSchema(schema)` | Free |
| **Constraint** | `.cost_under(0.01)` `.latency_under(5000)` `.tokens_under(500)` | `.costUnder(0.01)` `.latencyUnder(5000)` `.tokensUnder(500)` | Free |
| **Trace** | `.tools_called_in_order([...])` `.required_tools([...])` `.forbidden_tools([...])` `.agent_called("id")` `.delegation_depth(3)` `.aggregate_cost_under(0.05)` | `.toolsCalledInOrder([...])` `.requiredTools([...])` `.forbiddenTools([...])` `.agentCalled("id")` `.delegationDepth(3)` `.aggregateCostUnder(0.05)` | Free |
| **Content** | `.output_contains("x")` `.output_matches_regex(r"...")` `.output_has_all_keywords([...])` | `.outputContains("x")` `.outputMatchesRegex(/.../)`  `.outputHasAllKeywords([...])` | Free |
| **Embedding** | `.output_similar_to("ref", threshold=0.8)` | `.outputSimilarTo("ref", { threshold: 0.8 })` | Depends on provider |
| **Judge** | `.passes_judge("criteria", threshold=0.8)` | `.passesJudge("criteria", { threshold: 0.8 })` | Depends on provider |

---

## Adapters

Drop-in tracing for your existing agent framework — no code changes to your agent logic.

<!-- claims:adapters:start -->
| Adapter | Python | TypeScript |
|---------|-------------|-------------|
| OpenAI | stable | stable |
| Anthropic | stable | stable |
| Manual | stable | stable |
| Gemini | beta | beta |
| Ollama | beta | beta |
| LangChain | beta | beta |
| CrewAI | beta | — |
| OpenTelemetry | beta | beta |
| Google ADK | experimental | — |
| LlamaIndex | experimental | — |

- **beta**: Shipped and tested, but the interface or behavior can still change in a minor release.
- **experimental**: Shipped without a stability commitment and without demonstrated demand; it can change or be removed in any release.
- **stable**: Covered by the parity and conformance suites; a change in behavior is a breaking change.
<!-- claims:adapters:end -->

---

## Repositories

| Repository | Description |
|------------|-------------|
| [`attest`](https://github.com/attest-framework/attest) | Core framework — Go engine, Python SDK, TypeScript SDK, pytest + Vitest plugins |
| [`attest-examples`](https://github.com/attest-framework/attest-examples) | 25 small, copyable examples — one per feature or framework, in Python and TypeScript |
| [`refund-desk`](https://github.com/attest-framework/refund-desk) | Two synthetic incidents, from reproduction to regression and contract-removal gates |
| [`attest-framework.github.io`](https://github.com/attest-framework/attest-framework.github.io) | Source of the documentation site at [attest-framework.github.io](https://attest-framework.github.io/) — guides, API reference, architecture docs |

---

<p align="center">
  <a href="https://attest-framework.github.io/">Documentation</a> · <a href="https://github.com/attest-framework/attest-examples">Examples</a> · <a href="https://pypi.org/project/attest-ai/">PyPI</a> · <a href="https://www.npmjs.com/package/@attest-ai/core">npm</a>
</p>
<p align="center">Apache-2.0 License</p>
