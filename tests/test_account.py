# -*- coding: utf-8 -*-
"""
Unit tests for backtestlib.account module.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import backtestlib.account as ba


@pytest.fixture
def account_manager():
    return ba.AccountManager()


@pytest.fixture
def account(account_manager):
    return account_manager.accounts['1st_account']


def test_account_manager_creates_default_account(account_manager):
    assert '1st_account' in account_manager.accounts


def test_account_initial_balance_is_zero(account):
    assert account.balance == 0
    assert account.cash == 0


def test_deposit_increases_cash(account):
    account.deposit(1000)
    assert account.cash == 1000


def test_withdraw_decreases_cash(account):
    account.deposit(1000)
    account.withdraw(500)
    assert account.cash == 500


def test_withdraw_raises_when_insufficient(account):
    with pytest.raises(ValueError, match="Cash isn't enough"):
        account.withdraw(100)


def test_update_balance_sums_cash_and_assets(account):
    account.deposit(1000)
    account.update_balance_from_floating_assets_cash()
    assert account.balance == 1000


def test_create_floating_asset(account):
    account.create_floating_asset_if_not_exist('test_asset')
    assert 'test_asset' in account.floating_assets
    assert account.floating_assets['test_asset'] == 0


def test_transfer_cash_to_floating_asset(account):
    account.deposit(500)
    account.create_floating_asset_if_not_exist('test_asset')
    account.transfer_cash_to_floating_asset('test_asset', 300)
    assert account.cash == 200
    assert account.floating_assets['test_asset'] == 300


def test_transfer_cash_raises_when_insufficient(account):
    account.deposit(100)
    account.create_floating_asset_if_not_exist('test_asset')
    with pytest.raises(ValueError):
        account.transfer_cash_to_floating_asset('test_asset', 200)


def test_reset_clears_account_state(account):
    account.deposit(1000)
    account.reset()
    assert account.balance == 0
    assert account.cash == 0


def test_create_new_account(account_manager):
    account_manager.create_new_account(name='second_account')
    assert 'second_account' in account_manager.accounts


def test_create_duplicate_account_raises(account_manager):
    with pytest.raises(ValueError, match="Account is existed"):
        account_manager.create_new_account(name='1st_account')
