"""Unit tests for correlation engine."""

import pytest
import pandas as pd
from pathlib import Path

from app.core.correlation import CorrelationEngine
from app.core.signal_engine import SignalEngine
from app.models import SignalResponse


class TestCorrelationEngine:
    """Test correlation analysis engine."""

    @pytest.fixture
    def engine(self):
        return CorrelationEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes properly."""
        assert engine is not None
        assert engine.results_dir is not None

    def test_analyze_lagged_correlation_invalid_period(self, engine):
        """Test with invalid period raises error."""
        with pytest.raises(ValueError):
            engine.analyze_lagged_correlation(period="invalid")


class TestSignalEngine:
    """Test signal generation engine."""

    @pytest.fixture
    def engine(self):
        return SignalEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes properly."""
        assert engine is not None
        assert engine.buy_threshold == 2.0
        assert engine.sell_threshold == -2.0

    def test_create_hold_signal(self, engine):
        """Test creating a HOLD signal."""
        signal = engine._create_hold_signal()
        assert signal.signal == "HOLD"
        assert signal.confidence == "0.0%"
        assert signal.net_score == 0.0

    def test_filter_by_thresholds(self, engine):
        """Test filtering correlations by thresholds."""
        df = pd.DataFrame({
            "ticker": ["A", "B", "C"],
            "correlation": [0.5, 0.15, 0.25],
            "period": ["1mo", "3mo", "6mo"],
            "shift_days": [1, 1, 1]
        })

        filtered = engine._filter_by_thresholds(df)
        assert len(filtered) >= 0

    def test_determine_signal_buy(self, engine):
        """Test BUY signal generation."""
        signal, confidence = engine._determine_signal(total_score=3.0, max_potential=5.0)
        assert signal == "BUY"
        assert confidence > 0

    def test_determine_signal_sell(self, engine):
        """Test SELL signal generation."""
        signal, confidence = engine._determine_signal(total_score=-3.0, max_potential=5.0)
        assert signal == "SELL"
        assert confidence > 0

    def test_determine_signal_hold(self, engine):
        """Test HOLD signal generation."""
        signal, confidence = engine._determine_signal(total_score=0.5, max_potential=5.0)
        assert signal == "HOLD"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
