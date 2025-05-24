from mcp.server.fastmcp import FastMCP
from accounts_db import (
    get_balance, transfer, get_history, get_user_accounts,
    create_account, close_account, deposit, withdraw,
    update_account_details
)

mcp = FastMCP("Retail Banking MCP")


@mcp.tool()
def open_new_account(holder_name: str, account_type: str, initial_deposit: float = 0) -> str:
    """Opens a new bank account
    
    Args:
        holder_name: Name of the account holder
        account_type: Type of account (savings/checking)
        initial_deposit: Initial amount to deposit
    """
    account_id = create_account(holder_name, account_type, initial_deposit)
    return f"Account created successfully! Your account number is {account_id}"


@mcp.tool()
def close_bank_account(account_id: str) -> str:
    """Closes an existing bank account
    
    Args:
        account_id: Account number to close
    """
    if close_account(account_id):
        return f"Account {account_id} has been closed successfully."
    return f"Could not close account {account_id}. Please ensure the balance is zero."


@mcp.tool()
def check_balance(account_id: str) -> str:
    """Returns current account balance
    
    Args:
        account_id: Account number to check
    """
    balance = get_balance(account_id)
    return f"The balance for account {account_id} is ₹{balance}."


@mcp.tool()
def deposit_money(account_id: str, amount: float, description: str = "Deposit") -> str:
    """Deposits money into an account
    
    Args:
        account_id: Account number for deposit
        amount: Amount to deposit
        description: Optional description for the transaction
    """
    if deposit(account_id, amount, description):
        return f"Successfully deposited ₹{amount} into account {account_id}."
    return f"Could not deposit into account {account_id}. Please verify the account is active."


@mcp.tool()
def withdraw_money(account_id: str, amount: float, description: str = "Withdrawal") -> str:
    """Withdraws money from an account
    
    Args:
        account_id: Account number for withdrawal
        amount: Amount to withdraw
        description: Optional description for the transaction
    """
    if withdraw(account_id, amount, description):
        return f"Successfully withdrew ₹{amount} from account {account_id}."
    return f"Could not withdraw from account {account_id}. Please check balance and account status."


@mcp.tool()
def transfer_funds(from_account: str, to_account: str, amount: float) -> str:
    """Transfers funds between two accounts
    
    Args:
        from_account: Source account number
        to_account: Destination account number
        amount: Amount to transfer
    """
    success = transfer(from_account, to_account, amount)
    return (
        f"Transferred ₹{amount} from {from_account} to {to_account}."
        if success else
        f"Transfer failed. Please check account status and balance."
    )


@mcp.tool()
def get_transaction_history(account_id: str, start_date: str = None, end_date: str = None) -> str:
    """Returns transaction history
    
    Args:
        account_id: Account number
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
    """
    history = get_history(account_id, start_date, end_date)
    if not history:
        return f"No transactions found for {account_id} in the specified period."
    
    result = f"Transaction History for {account_id}:\n"
    for trans in history:
        result += (f"\nDate: {trans['timestamp']}\n"
                  f"Type: {trans['type']}\n"
                  f"Amount: ₹{trans['amount']}\n"
                  f"Description: {trans['description']}\n"
                  f"Balance: ₹{trans['balance_after']}\n"
                  f"{'-'*40}")
    return result


@mcp.tool()
def list_accounts() -> str:
    """Lists all accounts with their details"""
    accounts = get_user_accounts()
    if not accounts:
        return "No accounts found"
    
    result = "Active Bank Accounts:\n"
    for acc_id, details in accounts.items():
        result += (f"\nAccount: {acc_id}\n"
                  f"Holder: {details['holder_name']}\n"
                  f"Type: {details['account_type']}\n"
                  f"Balance: ₹{details['balance']}\n"
                  f"Status: {details['status']}\n"
                  f"{'-'*40}")
    return result


@mcp.tool()
def update_account(account_id: str, holder_name: str = None, account_type: str = None) -> str:
    """Updates account details
    
    Args:
        account_id: Account number to update
        holder_name: New holder name (optional)
        account_type: New account type (optional)
    """
    if update_account_details(account_id, holder_name, account_type):
        return f"Account {account_id} details updated successfully."
    return f"Could not update account {account_id}. Please verify the account exists."


if __name__ == "__main__":
    mcp.run()
