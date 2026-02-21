# Attest

**Test your AI agents like you test your code.**

Attest is an open-source testing framework for AI agents. It provides a graduated assertion pipeline — deterministic checks first, LLM-as-judge only when necessary — so you get fast, reliable, cost-effective test suites.

## Why Attest?

- **8-layer assertion pipeline** — from free schema validation to paid LLM judge, use the cheapest assertion that proves your point
- **Framework agnostic** — adapters for OpenAI, Anthropic, Gemini, LangChain, LlamaIndex, Google ADK, CrewAI, and more
- **pytest native** — `expect(result).output_contains("x").cost_under(0.01)` runs in your existing test suite
- **Multi-agent support** — trace trees, delegation tracking, cross-agent assertions
- **Cost as a first-class metric** — budget limits, cost reports, graduated evaluation strategies

## Repositories

| Repository | Description |
|------------|-------------|
| [attest](https://github.com/attest-framework/attest) | Core framework: Go engine, Python SDK, pytest plugin, 11 adapters |
| [attest-examples](https://github.com/attest-framework/attest-examples) | Quickstart guides, framework integrations, production patterns |

## Get Started

```bash
pip install attest-ai
```

```python
from attest import agent, expect

@agent("my-agent")
def my_agent(builder, query):
    builder.add_tool_call("search", args={"q": query})
    return {"answer": "..."}

def test_agent(attest):
    result = my_agent(query="test")
    chain = (
        expect(result)
        .output_contains("answer")
        .cost_under(0.05)
        .tools_called_in_order(["search"])
    )
    attest.evaluate(chain)
```

## License

Apache-2.0
