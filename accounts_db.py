import sqlite3
from datetime import datetime
import uuid
from contextlib import contextmanager

DATABASE_NAME = "banking.db"

def init_db():
    """Initialize the database with required tables"""
    with get_db() as (conn, cur):
        # Create accounts table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            holder_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL
        )
        ''')

        # Create transactions table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            balance_after REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts (account_id)
        )
        ''')
        conn.commit()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    try:
        yield conn, cur
    finally:
        conn.close()

def create_account(holder_name: str, account_type: str, initial_deposit: float = 0):
    account_id = f"acc{str(uuid.uuid4())[:8]}"
    with get_db() as (conn, cur):
        cur.execute('''
        INSERT INTO accounts (account_id, holder_name, account_type, balance, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (account_id, holder_name, account_type, initial_deposit, datetime.now().strftime("%Y-%m-%d")))
        
        if initial_deposit > 0:
            cur.execute('''
            INSERT INTO transactions (account_id, type, amount, description, balance_after, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (account_id, "credit", initial_deposit, "Initial deposit", initial_deposit, 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
    return account_id

def close_account(account_id: str) -> bool:
    with get_db() as (conn, cur):
        cur.execute('SELECT balance FROM accounts WHERE account_id = ?', (account_id,))
        result = cur.fetchone()
        
        if not result or result[0] != 0:
            return False
            
        cur.execute('''
        UPDATE accounts SET status = 'closed'
        WHERE account_id = ?
        ''', (account_id,))
        conn.commit()
        return cur.rowcount > 0

def get_balance(account_id: str) -> float:
    with get_db() as (conn, cur):
        cur.execute('SELECT balance FROM accounts WHERE account_id = ?', (account_id,))
        result = cur.fetchone()
        return result[0] if result else 0.0

def deposit(account_id: str, amount: float, description: str = "Deposit") -> bool:
    with get_db() as (conn, cur):
        # Check account status
        cur.execute('SELECT balance FROM accounts WHERE account_id = ? AND status = "active"', (account_id,))
        result = cur.fetchone()
        if not result:
            return False
        
        new_balance = result[0] + amount
        
        # Update balance
        cur.execute('''
        UPDATE accounts SET balance = ?
        WHERE account_id = ?
        ''', (new_balance, account_id))
        
        # Record transaction
        cur.execute('''
        INSERT INTO transactions (account_id, type, amount, description, balance_after, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (account_id, "credit", amount, description, new_balance, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        return True

def withdraw(account_id: str, amount: float, description: str = "Withdrawal") -> bool:
    with get_db() as (conn, cur):
        # Check account status and balance
        cur.execute('''
        SELECT balance FROM accounts 
        WHERE account_id = ? AND status = "active" AND balance >= ?
        ''', (account_id, amount))
        result = cur.fetchone()
        if not result:
            return False
        
        new_balance = result[0] - amount
        
        # Update balance
        cur.execute('''
        UPDATE accounts SET balance = ?
        WHERE account_id = ?
        ''', (new_balance, account_id))
        
        # Record transaction
        cur.execute('''
        INSERT INTO transactions (account_id, type, amount, description, balance_after, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (account_id, "debit", amount, description, new_balance, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        return True

def transfer(from_acc: str, to_acc: str, amount: float) -> bool:
    with get_db() as (conn, cur):
        try:
            # Start transaction
            conn.execute('BEGIN TRANSACTION')
            
            # Withdraw from source account
            if not withdraw(from_acc, amount, f"Transfer to {to_acc}"):
                conn.rollback()
                return False
                
            # Deposit to destination account
            if not deposit(to_acc, amount, f"Transfer from {from_acc}"):
                conn.rollback()
                return False
                
            conn.commit()
            return True
            
        except Exception:
            conn.rollback()
            return False

def get_history(account_id: str, start_date: str = None, end_date: str = None):
    with get_db() as (conn, cur):
        query = '''
        SELECT timestamp, type, amount, description, balance_after
        FROM transactions
        WHERE account_id = ?
        '''
        params = [account_id]
        
        if start_date and end_date:
            query += ' AND date(timestamp) BETWEEN date(?) AND date(?)'
            params.extend([start_date, end_date])
            
        query += ' ORDER BY timestamp DESC'
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        return [
            {
                'timestamp': row[0],
                'type': row[1],
                'amount': row[2],
                'description': row[3],
                'balance_after': row[4]
            }
            for row in rows
        ]

def get_user_accounts():
    with get_db() as (conn, cur):
        cur.execute('''
        SELECT account_id, holder_name, account_type, balance, status
        FROM accounts
        ''')
        rows = cur.fetchall()
        
        return {
            row[0]: {
                'holder_name': row[1],
                'account_type': row[2],
                'balance': row[3],
                'status': row[4]
            }
            for row in rows
        }

def update_account_details(account_id: str, holder_name: str = None, account_type: str = None) -> bool:
    with get_db() as (conn, cur):
        updates = []
        params = []
        
        if holder_name:
            updates.append('holder_name = ?')
            params.append(holder_name)
        if account_type:
            updates.append('account_type = ?')
            params.append(account_type)
            
        if not updates:
            return True
            
        params.append(account_id)
        query = f'''
        UPDATE accounts 
        SET {', '.join(updates)}
        WHERE account_id = ?
        '''
        
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount > 0

# Initialize the database when the module is imported
init_db()