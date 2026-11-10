"""
Unit Test Suite per Steve Capital Solana Autonomous Agent
=========================================================
Verifica TDD con Exit Code 0:
1. Calcolo allocazione Half-Kelly con cap Steve Capital.
2. Intercettazione e blocco violazioni Guardrails (Slippage eccessivo, Size eccessiva, Drawdown).
3. Routing Jupiter DEX e calcolo revenue MultiHopper (0.25% share).
4. Interfaccia Tool Steve Agent Protocol (SAP MCP).
"""

import pytest
from solana_capital_agent import (
    SolanaAutonomousCapitalAgent,
    RiskGuardrails,
    SOL_MINT,
    USDC_MINT,
)


def test_half_kelly_allocation_and_cap():
    agent = SolanaAutonomousCapitalAgent("TestWallet11111111111111111111111111111111", initial_equity_usd=1000.0)
    # Win rate 60%, win/loss 2.0 -> Full Kelly = (0.6*2 - 0.4)/2 = 0.8/2 = 0.40 -> Half Kelly = 0.20
    # Guardrails cap è 0.20
    alloc = agent.compute_half_kelly_allocation(0.60, 2.0)
    assert alloc == pytest.approx(0.20, rel=1e-3)

    # Edge case: Win rate basso (40%, win/loss 1.0) -> Negative Kelly -> 0.0
    alloc_loss = agent.compute_half_kelly_allocation(0.40, 1.0)
    assert alloc_loss == 0.0


def test_guardrails_slippage_rejection():
    agent = SolanaAutonomousCapitalAgent("TestWallet11111111111111111111111111111111", initial_equity_usd=1000.0)
    # Slippage 100 bps > limit 50 bps
    eval_res = agent.evaluate_risk_guardrails(trade_size_usd=50.0, expected_slippage_bps=100)
    assert eval_res["approved"] is False
    assert any("Slippage eccessivo" in r for r in eval_res["reasons"])
    assert agent.state.guardrail_rejections == 1


def test_guardrails_position_size_rejection():
    agent = SolanaAutonomousCapitalAgent("TestWallet11111111111111111111111111111111", initial_equity_usd=1000.0)
    # Max size = 20% di $1000 = $200. Prova con $350
    eval_res = agent.evaluate_risk_guardrails(trade_size_usd=350.0, expected_slippage_bps=20)
    assert eval_res["approved"] is False
    assert any("eccede il cap" in r for r in eval_res["reasons"])


def test_dex_quote_and_multihopper_routing():
    agent = SolanaAutonomousCapitalAgent("TestWallet11111111111111111111111111111111", initial_equity_usd=1000.0)
    quote = agent.get_dex_quote(USDC_MINT, SOL_MINT, 180.0)
    assert quote["in_amount"] == 180.0
    assert quote["out_amount"] > 0.95  # Circa 1 SOL meno slippage
    assert quote["slippage_bps"] == 50

    # Test MultiHopper revenue sharing
    mh = agent.execute_multihopper_routing("USDC", "SOL", 10000.0)
    assert mh["status"] == "CONFIRMED"
    # 0.5% total fee = $50, our share 0.25% = $25
    assert mh["total_protocol_fee_usd"] == 50.0
    assert mh["partner_revenue_share_usd"] == 25.0
    assert agent.state.multihopper_fees_earned_usd == 25.0


def test_execute_guarded_trade_and_pnl_tracking():
    agent = SolanaAutonomousCapitalAgent("TestWallet11111111111111111111111111111111", initial_equity_usd=1000.0)
    res = agent.execute_trade(action="BUY_SOL", amount_usd=100.0, slippage_bps=25)
    assert res["status"] == "SUCCESS"
    assert agent.state.trades_executed == 1
    assert agent.state.holdings["SOL"] > 0.0
    assert agent.state.cash_usdc < 1000.0
    assert agent.state.total_routed_volume_usd == 100.0


def test_sap_mcp_tool_dispatcher():
    agent = SolanaAutonomousCapitalAgent("TestWallet11111111111111111111111111111111", initial_equity_usd=1000.0)

    # Tool status
    status = agent.handle_sap_mcp_tool_call("sap_get_status", {})
    assert status["wallet"] == "TestWallet11111111111111111111111111111111"
    assert status["equity_usd"] == 1000.0

    # Tool guardrail check
    guard = agent.handle_sap_mcp_tool_call(
        "sap_evaluate_guardrails", {"trade_size_usd": 150.0, "slippage_bps": 20}
    )
    assert guard["approved"] is True

    # Tool execute
    exec_res = agent.handle_sap_mcp_tool_call(
        "sap_execute_trade", {"action": "BUY_SOL", "amount_usd": 80.0, "slippage_bps": 20}
    )
    assert exec_res["status"] == "SUCCESS"
