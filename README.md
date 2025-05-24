# Retail Banking System

A simple retail banking system implemented using Python, SQLite, and MCP. The system provides banking operations through MCP tools interface.



## Features

- Account Management
  - Create new accounts (savings/checking)
  - Close existing accounts
  - Update account details
  - View account information

- Transaction Operations
  - Deposit funds
  - Withdraw funds
  - Transfer between accounts
  - View transaction history with date filtering

## Setup

1. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

2. Install the project with all dependencies:
```bash
uv pip install -e .
```

3. Run the combined server:
```bash
python combined_server.py
```

The system will start:
- REST API server on `http://localhost:8000`
- MCP tools interface
- SQLite database (`banking.db`) will be created automatically when first run
- API documentation available at `http://localhost:8000/docs`

## Development Setup

For development, you might want to install additional tools:

```bash
# Install development dependencies
uv pip install black ruff pytest

# Format code
black .

# Run linting
ruff check .

# Run tests
pytest
```

## REST API Endpoints

### Accounts

1. Create Account
```http
POST /accounts/
Content-Type: application/json

{
    "holder_name": "John Doe",
    "account_type": "savings",
    "initial_deposit": 1000.0
}
```

2. Get Account Balance
```http
GET /accounts/{account_id}/balance
```

3. List All Accounts
```http
GET /accounts/
```

4. Update Account
```http
PATCH /accounts/{account_id}
Content-Type: application/json

{
    "holder_name": "John Smith",
    "account_type": "checking"
}
```

5. Close Account
```http
DELETE /accounts/{account_id}
```

### Transactions

1. Deposit Money
```http
POST /accounts/{account_id}/deposit
Content-Type: application/json

{
    "amount": 500.0,
    "description": "Salary deposit"
}
```

2. Withdraw Money
```http
POST /accounts/{account_id}/withdraw
Content-Type: application/json

{
    "amount": 200.0,
    "description": "ATM withdrawal"
}
```

3. Transfer Funds
```http
POST /transfer/
Content-Type: application/json

{
    "from_account": "acc123",
    "to_account": "acc456",
    "amount": 300.0
}
```

4. Get Transaction History
```http
GET /accounts/{account_id}/history?start_date=2024-03-01&end_date=2024-03-31
```

## MCP Tools

The following operations are available through the MCP interface:

1. Create Account:
```python
mcp_open_new_account("John Doe", "savings", 1000)
```

2. Deposit Money:
```python
mcp_deposit_money("acc123", 500, "Salary deposit")
```

3. Withdraw Money:
```python
mcp_withdraw_money("acc123", 200, "ATM withdrawal")
```

4. Transfer Funds:
```python
mcp_transfer_funds("acc123", "acc456", 300)
```

5. Check Balance:
```python
mcp_check_balance("acc123")
```

6. View Transaction History:
```python
mcp_get_transaction_history("acc123", "2024-03-01", "2024-03-31")
```

7. List Accounts:
```python
mcp_list_accounts()
```

## Database Schema

### Accounts Table
- account_id (TEXT): Primary key
- holder_name (TEXT): Account holder's name
- account_type (TEXT): Type of account (savings/checking)
- balance (REAL): Current balance
- status (TEXT): Account status (active/closed)
- created_at (TEXT): Account creation date

### Transactions Table
- id (INTEGER): Primary key
- account_id (TEXT): Foreign key to accounts
- type (TEXT): Transaction type (credit/debit)
- amount (REAL): Transaction amount
- description (TEXT): Transaction description
- balance_after (REAL): Balance after transaction
- timestamp (TEXT): Transaction timestamp
