"""Initialize the rental system database with websites and sample accounts."""

from src.database import PasswordResetDB

def init_system():
    """Initialize the rental system with default websites."""
    db = PasswordResetDB()
    
    print("=" * 60)
    print("Initializing Tool Rental System Database")
    print("=" * 60)
    
    # Add websites/tools
    websites = [
        {
            'name': 'unlocktool',
            'url': 'https://unlocktool.net',
            'validity_hours': 6,
            'description': 'Unlock Tool - Valid for 6 hours'
        },
        {
            'name': 'androidmultitool',
            'url': 'https://androidmultitool.com',
            'validity_hours': 2,
            'description': 'Android Multi Tool - Valid for 2 hours'
        }
    ]
    
    for website in websites:
        try:
            website_id = db.add_website(
                name=website['name'],
                url=website['url'],
                validity_hours=website['validity_hours'],
                description=website['description']
            )
            print(f"✓ Added website: {website['name']} (ID: {website_id}, Valid: {website['validity_hours']}h)")
        except Exception as e:
            print(f"✗ Error adding {website['name']}: {e}")
    
    print("\n" + "=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)
    
    # Display statistics
    stats = db.get_dashboard_stats()
    print(f"\nTotal Websites: {stats['total_websites']}")
    print(f"Total Accounts: {stats['total_accounts']}")
    print(f"Available Accounts: {stats['available_accounts']}")
    print(f"Rented Accounts: {stats['rented_accounts']}")
    
    print("\nNext steps:")
    print("1. Update config/accounts.json with your accounts")
    print("2. Add 'website' field to each account (e.g., 'unlocktool' or 'androidmultitool')")
    print("3. Run: python main.py --mode run-once")
    
if __name__ == '__main__':
    init_system()
