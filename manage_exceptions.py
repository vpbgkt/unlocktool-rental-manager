"""CLI tool to manage accounts marked with exceptions."""

import sys
from src.database import PasswordResetDB

def main():
    """Manage exception accounts."""
    db = PasswordResetDB()
    
    print("=" * 70)
    print("EXCEPTION ACCOUNTS MANAGEMENT")
    print("=" * 70)
    
    # Get all exception accounts
    exceptions = db.get_exception_accounts()
    
    if not exceptions:
        print("\n✓ No accounts with exceptions found!")
        return
    
    print(f"\nFound {len(exceptions)} account(s) with exceptions:\n")
    
    for acc in exceptions:
        print(f"ID: {acc['id']}")
        print(f"  Website: {acc['website']}")
        print(f"  Username: {acc['username']}")
        print(f"  Email: {acc['email']}")
        print(f"  Reason: {acc['exception_reason']}")
        print(f"  Failed Attempts: {acc['failed_attempts']}")
        print(f"  Last Failed: {acc['last_failed']}")
        print("-" * 70)
    
    print("\nOptions:")
    print("1. Clear exception and update password")
    print("2. Exit")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == '1':
        account_id = input("Enter Account ID to fix: ").strip()
        new_password = input("Enter the correct current password: ").strip()
        
        if account_id and new_password:
            db.reset_account_exception(int(account_id), new_password)
            
            # Also update config file
            import json
            with open('config/accounts.json', 'r') as f:
                config = json.load(f)
            
            for acc in config['accounts']:
                found = False
                for exc in exceptions:
                    if acc['username'] == exc['username']:
                        acc['current_password'] = new_password
                        found = True
                        break
                if found:
                    break
            
            with open('config/accounts.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✓ Account {account_id} exception cleared and password updated!")
        else:
            print("\n✗ Invalid input. Cancelled.")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
