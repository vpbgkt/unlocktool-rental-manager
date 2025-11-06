"""
CLI Tool for Managing API Keys
Create, list, revoke, and monitor API keys
"""

from src.api_manager import APIManager
from src.database import PasswordResetDB
from datetime import datetime


def main():
    api_manager = APIManager()
    db = PasswordResetDB()
    
    while True:
        print("\n" + "="*60)
        print("API Key Management")
        print("="*60)
        print("\n1. Create new API key")
        print("2. List all API keys")
        print("3. View API key details")
        print("4. Revoke API key")
        print("5. View usage statistics")
        print("6. View recent activity")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            create_api_key(api_manager)
        elif choice == '2':
            list_api_keys(api_manager)
        elif choice == '3':
            view_api_key_details(api_manager)
        elif choice == '4':
            revoke_api_key(api_manager)
        elif choice == '5':
            view_usage_stats(api_manager)
        elif choice == '6':
            view_recent_activity(api_manager)
        elif choice == '7':
            print("\nGoodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")


def create_api_key(api_manager):
    """Create a new API key."""
    print("\n" + "="*60)
    print("Create New API Key")
    print("="*60)
    
    name = input("\nAPI Key Name (e.g., Customer Portal, Mobile App): ").strip()
    if not name:
        print("❌ Name is required!")
        return
    
    email = input("Email (optional): ").strip() or None
    
    rate_limit_input = input("Rate Limit (requests/day, default 100): ").strip()
    rate_limit = int(rate_limit_input) if rate_limit_input else 100
    
    notes = input("Notes (optional): ").strip() or None
    
    try:
        result = api_manager.generate_api_key(name, email, rate_limit, notes)
        
        print("\n" + "="*60)
        print("✓ API Key Created Successfully!")
        print("="*60)
        print(f"\nAPI Key ID: {result['id']}")
        print(f"Name: {result['name']}")
        print(f"Email: {result['email'] or 'N/A'}")
        print(f"Rate Limit: {result['rate_limit']} requests/day")
        print(f"Created: {result['created_at']}")
        print("\n" + "="*60)
        print("🔑 API KEY (save this - it won't be shown again):")
        print("="*60)
        print(f"\n{result['api_key']}\n")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error creating API key: {e}")


def list_api_keys(api_manager):
    """List all API keys."""
    print("\n" + "="*60)
    print("All API Keys")
    print("="*60)
    
    keys = api_manager.get_api_keys()
    
    if not keys:
        print("\nNo API keys found.")
        return
    
    print(f"\nTotal: {len(keys)} API keys\n")
    
    for key in keys:
        status_icon = "✓" if key['status'] == 'active' else "✗"
        print(f"{status_icon} ID {key['id']}: {key['name']}")
        print(f"   Status: {key['status']}")
        print(f"   Email: {key['email'] or 'N/A'}")
        print(f"   Requests: {key['total_requests']} / {key['rate_limit']} per day")
        print(f"   Created: {key['created_at']}")
        print(f"   Last Used: {key['last_used'] or 'Never'}")
        if key['notes']:
            print(f"   Notes: {key['notes']}")
        print()


def view_api_key_details(api_manager):
    """View detailed information about an API key."""
    print("\n" + "="*60)
    print("API Key Details")
    print("="*60)
    
    api_key_id = input("\nEnter API Key ID: ").strip()
    
    if not api_key_id.isdigit():
        print("❌ Invalid ID!")
        return
    
    api_key_id = int(api_key_id)
    
    # Get stats
    stats = api_manager.get_usage_stats(api_key_id, days=30)
    activity = api_manager.get_recent_activity(api_key_id, limit=10)
    
    print("\n=== Usage Statistics (Last 30 Days) ===")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Unique Accounts: {stats['unique_accounts']}")
    print(f"Websites Used: {stats['websites_used']}")
    print(f"Rentals: {stats['rentals']}")
    print(f"Returns: {stats['returns']}")
    
    print("\n=== Recent Activity (Last 10) ===")
    if activity:
        for act in activity:
            print(f"{act['timestamp']} | {act['action'].upper()} | {act['website']} | {act['username']} | {act['status']}")
    else:
        print("No activity yet.")


def revoke_api_key(api_manager):
    """Revoke an API key."""
    print("\n" + "="*60)
    print("Revoke API Key")
    print("="*60)
    
    api_key_id = input("\nEnter API Key ID to revoke: ").strip()
    
    if not api_key_id.isdigit():
        print("❌ Invalid ID!")
        return
    
    api_key_id = int(api_key_id)
    
    confirm = input(f"\n⚠️  Are you sure you want to revoke API Key #{api_key_id}? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        success = api_manager.revoke_api_key(api_key_id)
        if success:
            print(f"\n✓ API Key #{api_key_id} revoked successfully!")
        else:
            print(f"\n❌ Failed to revoke API Key #{api_key_id}. Key not found.")
    else:
        print("\nRevocation cancelled.")


def view_usage_stats(api_manager):
    """View overall usage statistics."""
    print("\n" + "="*60)
    print("Overall Usage Statistics")
    print("="*60)
    
    days = input("\nNumber of days to analyze (default 30): ").strip()
    days = int(days) if days.isdigit() else 30
    
    stats = api_manager.get_usage_stats(days=days)
    
    print(f"\n=== Statistics for Last {days} Days ===")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Active API Keys: {stats['active_api_keys']}")
    print(f"Unique Accounts: {stats['unique_accounts']}")
    print(f"Total Rentals: {stats['rentals']}")
    print(f"Total Returns: {stats['returns']}")


def view_recent_activity(api_manager):
    """View recent API activity."""
    print("\n" + "="*60)
    print("Recent API Activity")
    print("="*60)
    
    limit = input("\nNumber of records to show (default 20): ").strip()
    limit = int(limit) if limit.isdigit() else 20
    
    activity = api_manager.get_recent_activity(limit=limit)
    
    if not activity:
        print("\nNo activity recorded yet.")
        return
    
    print(f"\n=== Last {len(activity)} Activities ===\n")
    
    for act in activity:
        print(f"{act['timestamp']}")
        print(f"  API Key: {act['api_key_name']}")
        print(f"  Action: {act['action'].upper()}")
        print(f"  Website: {act['website']}")
        print(f"  Account: {act['username']}")
        print(f"  Status: {act['status']}")
        print(f"  IP: {act['ip_address'] or 'N/A'}")
        print()


if __name__ == "__main__":
    main()
