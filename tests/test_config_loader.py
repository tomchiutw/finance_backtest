# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.config_loader module.
"""
import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backtestlib.config_loader import load_yaml, load_strategy_config, load_commodities_config
from backtestlib.exceptions import ConfigurationError


def test_load_yaml_raises_for_missing_file(tmp_path):
    with pytest.raises(ConfigurationError, match="not found"):
        load_yaml(str(tmp_path / "nonexistent.yaml"))


def test_load_yaml_raises_for_invalid_yaml(tmp_path):
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text(": invalid: yaml: {")
    with pytest.raises(ConfigurationError):
        load_yaml(str(bad_yaml))


def test_load_yaml_returns_dict(tmp_path):
    valid_yaml = tmp_path / "config.yaml"
    valid_yaml.write_text("key: value\nnumber: 42\n")
    result = load_yaml(str(valid_yaml))
    assert result == {'key': 'value', 'number': 42}


def test_load_yaml_empty_file_returns_empty_dict(tmp_path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    result = load_yaml(str(empty))
    assert result == {}


def test_load_strategy_config_returns_dict():
    config = load_strategy_config()
    assert isinstance(config, dict)
    assert 'F0001' in config


def test_load_strategy_config_f0001_keys():
    config = load_strategy_config()
    f0001 = config['F0001']
    expected_keys = [
        'short_entry_percentage', 'short_close_percentage',
        'long_entry_percentage', 'leverage',
    ]
    for key in expected_keys:
        assert key in f0001, f"Expected key '{key}' in F0001 config"


def test_load_commodities_config_returns_dict():
    config = load_commodities_config()
    assert isinstance(config, dict)


def test_load_strategy_config_custom_dir(tmp_path):
    strategy_yaml = tmp_path / "strategy_config.yaml"
    strategy_yaml.write_text("TEST_STRATEGY:\n  leverage: 2.0\n")
    result = load_strategy_config(config_dir=str(tmp_path))
    assert 'TEST_STRATEGY' in result
    assert result['TEST_STRATEGY']['leverage'] == 2.0
