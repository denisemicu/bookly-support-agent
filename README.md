# Bookly Support Agent

A customer support agent for Bookly, a fictional online bookstore.

**Live demo:** https://bookly-support-agent-xi.vercel.app

Pip helps customers with:

* Order tracking
* Return eligibility and return requests
* Refund status
* Order cancellation
* Shipping-address changes
* Missing-package claims
* Shipping, return, and password-reset questions

## How it works

Pip follows a simple workflow:

```text
Understand → Clarify → Propose → Confirm → Act → Explain
```

The agent gathers the required context, explains the tool action it can take, waits for customer confirmation, then executes the action and displays an Agent Trace with the detected intent, selected action, and tool used.

## Example prompts

Try these in the live demo:

```text
Where is my order?
```

```text
I accidentally bought the hardcover version and want to return it
```

```text
My package says delivered but I never got it
```

```text
I need to change my shipping address
```

Use any valid Bookly order ID in the format:

```text
BK-1234
```

The agent also accepts variations such as:

```text
bk1234
bk 1234
```

## Architecture

```text
Next.js chat interface
        ↓
FastAPI support agent
        ↓
Intent routing + explicit conversation state
        ↓
Mock Bookly tools + OpenAI intent classification
```

The agent uses deterministic workflow logic for operational decisions. OpenAI is used for ambiguous intent classification, not for inventing order details or deciding whether to execute customer-impacting actions.

## Key behaviors

* Multi-turn context collection
* Explicit confirmation before tool execution
* Structured conversation state for active orders and pending actions
* Deterministic mock order data for any valid `BK-####` order ID
* Invalid-ID recovery and multi-order disambiguation
* Visible agent trace for transparency and debugging

## Tech stack

* Next.js + TypeScript
* FastAPI + Python
* OpenAI API
* Vercel
* Render

## Notes

Order data and operational tools are mocked for demonstration purposes. Customer-impacting actions require explicit confirmation before execution.

