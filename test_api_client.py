"""
Example Python client for the Tool Rental API
Demonstrates how to integrate the API into your applications
"""

import requests
import json
from datetime import datetime

# API Configuration
API_KEY = "urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY"  # Replace with your API key
BASE_URL = "http://localhost:5000/api"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(title)
    print("="*60 + "\n")


def health_check():
    """Check if API server is running."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Server is healthy!")
            print(f"  Service: {data['service']}")
            print(f"  Status: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        print("\nMake sure the API server is running:")
        print("  .\\venv\\Scripts\\python.exe api_server.py")
        return False


def list_available_accounts(website="unlocktool"):
    """List available accounts for a website."""
    print_section(f"2. List Available Accounts ({website})")
    try:
        response = requests.get(
            f"{BASE_URL}/accounts/available?website={website}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['count']} available accounts:\n")
            for acc in data['accounts']:
                print(f"  ID {acc['id']}: {acc['username']}")
                print(f"    Website: {acc['website']}")
                print(f"    Email: {acc['email']}")
                print(f"    Valid for: {acc['validity_hours']} hours")
                print(f"    Last reset: {acc['last_reset']}")
                print()
            return data['accounts']
        else:
            error = response.json()
            print(f"✗ Error: {error.get('error', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return []


def rent_account(website="unlocktool", customer_info="Python Client Test"):
    """Rent an account."""
    print_section(f"3. Rent an Account ({website})")
    try:
        data = {
            "website": website,
            "customer_info": customer_info
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/rent",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            account = result['account']
            print(f"✓ Account rented successfully!\n")
            print(f"  Rental ID: {account['rental_id']}")
            print(f"  Website: {account['website']}")
            print(f"  Username: {account['username']}")
            print(f"  Password: {account['password']}")
            print(f"  Email: {account['email']}")
            print(f"  Valid for: {account['validity_hours']} hours")
            print(f"  Expires at: {account['expires_at']}")
            print(f"\n  Message: {result['message']}")
            return account
        else:
            error = response.json()
            print(f"✗ Error: {error.get('error', 'Unknown error')}")
            print(f"  Message: {error.get('message', '')}")
            return None
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return None


def check_account_status(account_id):
    """Check the status of an account."""
    print_section(f"4. Check Account Status (ID: {account_id})")
    try:
        response = requests.get(
            f"{BASE_URL}/accounts/status/{account_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            account = result['account']
            print(f"✓ Account Status:\n")
            print(f"  Username: {account['username']}")
            print(f"  Status: {account['status']}")
            print(f"  Website: {account['website']}")
            
            if account['status'] == 'rented':
                print(f"  Expires at: {account['expires_at']}")
                print(f"  Customer: {account.get('customer_name', 'N/A')}")
            
            return account
        else:
            error = response.json()
            print(f"✗ Error: {error.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return None


def return_account(account_id):
    """Return a rented account."""
    print_section(f"5. Return Account (ID: {account_id})")
    try:
        response = requests.post(
            f"{BASE_URL}/accounts/return/{account_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {result['message']}")
            return True
        else:
            error = response.json()
            print(f"✗ Error: {error.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False


def get_my_stats():
    """Get usage statistics for current API key."""
    print_section("6. My Usage Statistics")
    try:
        response = requests.get(
            f"{BASE_URL}/stats/me?days=30",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            api_key_info = result['api_key']
            stats = result['stats']
            
            print(f"✓ API Key Information:\n")
            print(f"  Name: {api_key_info['name']}")
            print(f"  Total Requests: {api_key_info['total_requests']}")
            print(f"  Rate Limit: {api_key_info['rate_limit']} per day")
            print(f"  Created: {api_key_info['created_at']}")
            
            print(f"\n✓ Usage Statistics (Last 30 days):\n")
            print(f"  Total Requests: {stats['total_requests']}")
            print(f"  Unique Accounts Used: {stats['unique_accounts']}")
            print(f"  Websites Used: {stats['websites_used']}")
            print(f"  Total Rentals: {stats['rentals']}")
            print(f"  Total Returns: {stats['returns']}")
            
            if result['recent_activity']:
                print(f"\n✓ Recent Activity (Last 10):\n")
                for act in result['recent_activity'][:5]:  # Show first 5
                    print(f"  {act['timestamp']} | {act['action'].upper()} | {act['website']} | {act['username']}")
            
            return stats
        else:
            error = response.json()
            print(f"✗ Error: {error.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return None


def main():
    """Run the demo."""
    print("\n" + "="*60)
    print("Tool Rental API - Python Client Demo")
    print("="*60)
    
    # 1. Health check
    if not health_check():
        return
    
    # 2. List available accounts
    accounts = list_available_accounts("unlocktool")
    
    if accounts:
        # 3. Rent an account
        rented_account = rent_account("unlocktool", "Demo Customer #12345")
        
        if rented_account:
            account_id = rented_account['id']
            
            # 4. Check account status
            check_account_status(account_id)
            
            # 5. Return the account
            return_account(account_id)
            
            # Verify it's available again
            check_account_status(account_id)
    
    # 6. View statistics
    get_my_stats()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nYou can now integrate this API into your:")
    print("  - Customer portal/website")
    print("  - Mobile applications")
    print("  - Automated systems")
    print("  - Third-party integrations")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
