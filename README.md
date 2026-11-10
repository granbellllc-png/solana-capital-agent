# Steve Capital Solana Autonomous Capital Agent

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-brightgreen)
![Tests](https://img.shields.io/badge/tests-6%2F6%20passing-success)
![Solana](https://img.shields.io/badge/Solana-DeFi%20Agent-purple)

Autonomous Capital Agent on Solana built for the **OOBE Protocol Steve Capital Challenge** (Superteam Earn) with **Steve Agent Protocol (SAP MCP)**, **Jupiter DEX V6 routing**, and **MultiHopper revenue-sharing execution**.

---

## Features

- **Steve Agent Protocol (SAP MCP) Integration:** Fully compatible with OOBE Protocol's Steve Capital tool format (`sap_get_status`, `sap_evaluate_guardrails`, `sap_get_dex_quote`, `sap_execute_trade`).
- **Dynamic DEX Routing:** Real-time Jupiter DEX V6 quote synthesis across Solana SPL mints (SOL, USDC, RAY) with price impact and fee tracking.
- **Fail-Closed Risk Guardrails:**
  - **Fractional Half-Kelly Allocation:** Dynamically computes optimal size $f^* = \frac{1}{2} \cdot \frac{p \cdot b - q}{b}$ with strict 20% portfolio equity cap.
  - **Slippage Circuit Breaker:** Rejects routes exceeding 50 bps (0.50%).
  - **Daily Drawdown Limit:** Halts trading when daily equity drawdown reaches 5%.
  - **95% Historical CVaR Limit:** Caps expected tail risk below 8%.
- **MultiHopper Revenue Sharing:** Automates routing with MultiHopper fee tracking (0.50% total fee, 0.25% revenue split = $2,500 per $1M routed).

---

## Project Structure

```
.
├── solana_capital_agent.py      # Core autonomous agent & SAP MCP dispatcher
├── test_solana_capital_agent.py # Pytest verification suite (6/6 passing)
├── SUBMISSION_MANIFEST.md       # Superteam Earn submission details & X thread copy
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/granbellllc-png/solana-capital-agent.git
cd solana-capital-agent
pip install -r requirements.txt
```

### 2. Run Tests

```bash
pytest test_solana_capital_agent.py -v
```

Output:
```text
test_solana_capital_agent.py::test_half_kelly_allocation_and_cap PASSED
test_solana_capital_agent.py::test_guardrails_slippage_rejection PASSED
test_solana_capital_agent.py::test_guardrails_position_size_rejection PASSED
test_solana_capital_agent.py::test_dex_quote_and_multihopper_routing PASSED
test_solana_capital_agent.py::test_execute_guarded_trade_and_pnl_tracking PASSED
test_solana_capital_agent.py::test_sap_mcp_tool_dispatcher PASSED
============================== 6 passed in 0.07s ===============================
```

### 3. Usage via Python / SAP MCP

```python
from solana_capital_agent import SolanaAutonomousCapitalAgent

# Initialize agent with Solana wallet
agent = SolanaAutonomousCapitalAgent(
    wallet_address="YourSolanaWalletAddressHere...",
    initial_equity_usd=500.0
)

# Call SAP MCP Tools
status = agent.handle_sap_mcp_tool_call("sap_get_status", {})
print("Agent Status:", status)

# Execute guarded trade with Half-Kelly sizing
result = agent.handle_sap_mcp_tool_call("sap_execute_trade", {
    "action": "BUY_SOL",
    "amount_usd": 100.0,
    "slippage_bps": 30
})
print("Trade Result:", result)
```

---

## License

Apache-2.0. Maintained by Granbell LLC Quant & Autonomous Systems Team.
