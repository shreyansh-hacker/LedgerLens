import pytest
from decimal import Decimal
from datetime import datetime
from app.synthetic.generator import SyntheticFinancialDataEngine, quantize_money
from app.synthetic.scenarios import ScenarioType, DEFAULT_SCENARIO_DISTRIBUTION


@pytest.fixture
def default_engine():
    return SyntheticFinancialDataEngine(seed=42)


def test_determinism_same_seed():
    """Test that two engines with the same seed generate identical datasets."""
    engine1 = SyntheticFinancialDataEngine(seed=123)
    engine2 = SyntheticFinancialDataEngine(seed=123)

    data1 = engine1.generate_dataset(num_clusters=100)
    data2 = engine2.generate_dataset(num_clusters=100)

    assert len(data1["orders"]) == len(data2["orders"])
    for i in range(100):
        assert data1["orders"][i]["total_amount"] == data2["orders"][i]["total_amount"]
        assert data1["payments"][i]["amount"] == data2["payments"][i]["amount"]
        assert data1["ground_truth"][i]["scenario_type"] == data2["ground_truth"][i]["scenario_type"]
        assert data1["ground_truth"][i]["expected_difference"] == data2["ground_truth"][i]["expected_difference"]


def test_different_seeds_produce_different_data():
    """Test that different seeds produce distinct outputs."""
    engine1 = SyntheticFinancialDataEngine(seed=42)
    engine2 = SyntheticFinancialDataEngine(seed=999)

    data1 = engine1.generate_dataset(num_clusters=50)
    data2 = engine2.generate_dataset(num_clusters=50)

    amounts1 = [o["total_amount"] for o in data1["orders"]]
    amounts2 = [o["total_amount"] for o in data2["orders"]]

    assert amounts1 != amounts2


def test_decimal_precision_everywhere(default_engine):
    """Test that all financial amount fields use Decimal and have 2 decimal places."""
    data = default_engine.generate_dataset(num_clusters=200)

    for order in data["orders"]:
        amt = order["total_amount"]
        assert isinstance(amt, Decimal)
        assert amt.as_tuple().exponent == -2
        assert amt > 0

    for payment in data["payments"]:
        amt = payment["amount"]
        assert isinstance(amt, Decimal)
        assert amt.as_tuple().exponent == -2
        assert amt > 0

    for fee in data["fees"]:
        amt = fee["amount"]
        assert isinstance(amt, Decimal)
        assert amt.as_tuple().exponent == -2
        assert amt >= 0

    for tax in data["taxes"]:
        amt = tax["amount"]
        assert isinstance(amt, Decimal)
        assert amt.as_tuple().exponent == -2
        assert amt >= 0

    for st in data["settlements"]:
        assert isinstance(st["gross_amount"], Decimal)
        assert isinstance(st["fee_amount"], Decimal)
        assert isinstance(st["tax_amount"], Decimal)
        assert isinstance(st["net_amount"], Decimal)
        assert st["net_amount"] > 0

    for bnk in data["bank_transactions"]:
        assert isinstance(bnk["credit_amount"], Decimal)
        assert bnk["credit_amount"] > 0


def test_non_negative_amounts(default_engine):
    """Test that all generated financial entities have non-negative amounts."""
    data = default_engine.generate_dataset(num_clusters=500)

    assert all(o["total_amount"] > Decimal("0.00") for o in data["orders"])
    assert all(p["amount"] > Decimal("0.00") for p in data["payments"])
    assert all(f["amount"] >= Decimal("0.00") for f in data["fees"])
    assert all(t["amount"] >= Decimal("0.00") for t in data["taxes"])
    assert all(s["net_amount"] > Decimal("0.00") for s in data["settlements"])
    assert all(b["credit_amount"] > Decimal("0.00") for b in data["bank_transactions"])


def test_expected_settlement_formula(default_engine):
    """Test that baseline expected settlement equals Payment - Fee - Tax - Refund."""
    data = default_engine.generate_dataset(num_clusters=150)

    for i in range(150):
        payment_amt = data["payments"][i]["amount"]
        fee_amt = data["fees"][i]["amount"]
        tax_amt = data["taxes"][i]["amount"]
        expected_settlement = data["ground_truth"][i]["expected_settlement_amount"]

        calculated = quantize_money(payment_amt - fee_amt - tax_amt)
        assert expected_settlement == calculated


def test_scenario_distribution_statistical_bounds():
    """Test that scenario generation conforms to configured distribution across 1,000 samples."""
    engine = SyntheticFinancialDataEngine(seed=42)
    data = engine.generate_dataset(num_clusters=1000)

    counts = {}
    for gt in data["ground_truth"]:
        st = gt["scenario_type"]
        counts[st] = counts.get(st, 0) + 1

    # NORMAL_MATCH is configured for ~60% (allow 53% to 67% due to random sampling)
    normal_pct = counts[ScenarioType.NORMAL_MATCH] / 1000.0
    assert 0.53 <= normal_pct <= 0.67

    # All 10 scenario types must be represented
    for scenario_type in ScenarioType:
        assert scenario_type in counts
        assert counts[scenario_type] > 0


def test_normal_scenarios_reconcile_cleanly():
    """Test that normal scenarios have zero difference and are marked MATCHED."""
    # Force 100% normal distribution
    custom_dist = {st: 0.0 for st in ScenarioType}
    custom_dist[ScenarioType.NORMAL_MATCH] = 1.0

    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=custom_dist)
    data = engine.generate_dataset(num_clusters=50)

    for i in range(50):
        gt = data["ground_truth"][i]
        assert gt["scenario_type"] == ScenarioType.NORMAL_MATCH
        assert gt["expected_status"] == "MATCHED"
        assert gt["expected_difference"] == Decimal("0.00")
        assert gt["should_auto_resolve"] is True
        assert gt["should_require_human_review"] is False

        # Verify settlement matches bank transaction
        set_net = data["settlements"][i]["net_amount"]
        bnk_amt = data["bank_transactions"][i]["credit_amount"]
        assert set_net == bnk_amt


def test_missing_bank_scenario_behavior():
    """Test that missing bank transaction scenarios omit bank records."""
    custom_dist = {st: 0.0 for st in ScenarioType}
    custom_dist[ScenarioType.MISSING_BANK_TRANSACTION] = 1.0

    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=custom_dist)
    data = engine.generate_dataset(num_clusters=20)

    # 20 orders, 20 settlements, but 0 bank transactions
    assert len(data["orders"]) == 20
    assert len(data["settlements"]) == 20
    assert len(data["bank_transactions"]) == 0

    for gt in data["ground_truth"]:
        assert gt["scenario_type"] == ScenarioType.MISSING_BANK_TRANSACTION
        assert gt["expected_status"] == "EXCEPTION"
        assert gt["expected_difference"] > 0
        assert gt["should_require_human_review"] is True


def test_missing_settlement_scenario_behavior():
    """Test that missing settlement scenarios omit both settlement and bank records."""
    custom_dist = {st: 0.0 for st in ScenarioType}
    custom_dist[ScenarioType.MISSING_SETTLEMENT] = 1.0

    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=custom_dist)
    data = engine.generate_dataset(num_clusters=20)

    assert len(data["orders"]) == 20
    assert len(data["payments"]) == 20
    assert len(data["settlements"]) == 0
    assert len(data["bank_transactions"]) == 0

    for gt in data["ground_truth"]:
        assert gt["scenario_type"] == ScenarioType.MISSING_SETTLEMENT
        assert gt["expected_status"] == "EXCEPTION"
        assert gt["expected_difference"] > 0


def test_duplicate_settlement_scenario():
    """Test that duplicate settlement scenario generates extra settlement records."""
    custom_dist = {st: 0.0 for st in ScenarioType}
    custom_dist[ScenarioType.DUPLICATE_SETTLEMENT] = 1.0

    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=custom_dist)
    data = engine.generate_dataset(num_clusters=15)

    # 15 orders produce 30 settlements (original + duplicate)
    assert len(data["orders"]) == 15
    assert len(data["settlements"]) == 30

    for gt in data["ground_truth"]:
        assert gt["scenario_type"] == ScenarioType.DUPLICATE_SETTLEMENT
        assert gt["expected_status"] == "EXCEPTION"


def test_reference_discrepancy_scenario():
    """Test that reference discrepancy scenarios modify settlement reference IDs."""
    custom_dist = {st: 0.0 for st in ScenarioType}
    custom_dist[ScenarioType.REFERENCE_ID_DISCREPANCY] = 1.0

    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=custom_dist)
    data = engine.generate_dataset(num_clusters=20)

    for i in range(20):
        gt = data["ground_truth"][i]
        st = data["settlements"][i]
        assert gt["scenario_type"] == ScenarioType.REFERENCE_ID_DISCREPANCY
        assert "SET_EXT_ERR" in st["settlement_reference"]


def test_unexplained_exception_is_not_explainable():
    """Test that unexplained exceptions have is_explainable=False and require human review."""
    custom_dist = {st: 0.0 for st in ScenarioType}
    custom_dist[ScenarioType.UNEXPLAINED_EXCEPTION] = 1.0

    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=custom_dist)
    data = engine.generate_dataset(num_clusters=25)

    for gt in data["ground_truth"]:
        assert gt["scenario_type"] == ScenarioType.UNEXPLAINED_EXCEPTION
        assert gt["expected_status"] == "EXCEPTION"
        assert gt["is_explainable"] is False  # Must not hallucinate!
        assert gt["should_require_human_review"] is True
        assert gt["expected_difference"] > 0


def test_large_scale_generation_1000_clusters(default_engine):
    """Test that the generator smoothly creates 1,000 clusters within reasonable time."""
    start_time = datetime.now()
    data = default_engine.generate_dataset(num_clusters=1000)
    duration_secs = (datetime.now() - start_time).total_seconds()

    assert len(data["orders"]) == 1000
    assert len(data["payments"]) == 1000
    assert len(data["fees"]) == 1000
    assert len(data["taxes"]) == 1000
    assert len(data["ground_truth"]) == 1000
    assert duration_secs < 2.0  # Must be fast (< 2 seconds)
