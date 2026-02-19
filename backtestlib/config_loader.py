# -*- coding: utf-8 -*-
"""
Configuration loader for YAML configuration files.
"""
import os
import yaml
from backtestlib.exceptions import ConfigurationError


def load_yaml(file_path: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.

    Parameters:
        file_path (str): Absolute or relative path to the YAML file.

    Returns:
        dict: Parsed YAML contents.

    Raises:
        ConfigurationError: If the file does not exist or cannot be parsed.
    """
    if not os.path.exists(file_path):
        raise ConfigurationError(f"Configuration file not found: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Failed to parse YAML file '{file_path}': {e}") from e
    return config if config is not None else {}


def load_strategy_config(config_dir: str = None) -> dict:
    """
    Load strategy configuration from strategy_config.yaml.

    Parameters:
        config_dir (str, optional): Directory containing the config file.
            Defaults to the 'config/' directory in the project root.

    Returns:
        dict: Strategy configuration dictionary.
    """
    if config_dir is None:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    return load_yaml(os.path.join(config_dir, 'strategy_config.yaml'))


def load_commodities_config(config_dir: str = None) -> dict:
    """
    Load commodities configuration from commodities_config.yaml.

    Parameters:
        config_dir (str, optional): Directory containing the config file.
            Defaults to the 'config/' directory in the project root.

    Returns:
        dict: Commodities configuration dictionary.
    """
    if config_dir is None:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    return load_yaml(os.path.join(config_dir, 'commodities_config.yaml'))
