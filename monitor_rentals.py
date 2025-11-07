"""
Real-time Rental Monitor
Continuously monitors active rentals and shows countdown timers
"""

import time
import os
from datetime import datetime, timedelta
from src.supabase_db import SupabaseDB


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time_remaining(minutes):
    """Format minutes into human-readable time."""
    if minutes < 0:
        return "EXPIRED"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"


def get_urgency_info(minutes):
    """Get urgency level and display info."""
    if minutes <= 0:
        return "🔴 EXPIRED", "Reset password NOW!"
    elif minutes <= 5:
        return "🔴 CRITICAL", "Reset password IMMEDIATELY!"
    elif minutes <= 15:
        return "🟠 HIGH", "Reset password soon"
    elif minutes <= 30:
        return "🟡 MEDIUM", "Monitor closely"
    else:
        return "🟢 LOW", "No action needed"


def monitor_rentals(refresh_seconds=30):
    """
    Monitor active rentals in real-time.
    
    Args:
        refresh_seconds: Seconds between updates (default: 30)
    """
    print("\n" + "="*80)
    print(" 🚀 REAL-TIME RENTAL MONITOR")
    print("="*80)
    print(f"\n Connecting to Supabase...")
    
    try:
        db = SupabaseDB()
        print(f" ✓ Connected successfully!\n")
        print(f" Press Ctrl+C to exit")
        print(f" Refreshing every {refresh_seconds} seconds...")
        
        while True:
            clear_screen()
            
            print("="*80)
            print(f" 📊 RENTAL DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            
            # Get active rentals
            result = db.client.table('rentals').select(
                '*, accounts(id, username, email, current_password, websites(name, url, validity_hours))'
            ).eq('status', 'active').execute()
            
            if not result.data:
                print("\n ✅ No active rentals")
                print("\n 💡 All accounts available for password reset")
            else:
                rentals = result.data
                now = datetime.now()
                
                # Sort by expiry time (soonest first)
                rentals.sort(key=lambda r: datetime.fromisoformat(r['expires_at'].replace('Z', '+00:00')))
                
                print(f"\n ⚠️  Active Rentals: {len(rentals)}")
                print("-"*80)
                
                for i, rental in enumerate(rentals, 1):
                    account = rental['accounts']
                    website = account['websites']
                    expires_at = datetime.fromisoformat(rental['expires_at'].replace('Z', '+00:00'))
                    
                    # Calculate time remaining
                    time_remaining = expires_at - now
                    minutes_remaining = int(time_remaining.total_seconds() / 60)
                    
                    urgency_icon, urgency_msg = get_urgency_info(minutes_remaining)
                    time_str = format_time_remaining(minutes_remaining)
                    
                    print(f"\n {i}. {urgency_icon} {account['username']} @ {website['name']}")
                    print(f"    Customer: {rental.get('customer_name', 'Unknown')}")
                    print(f"    Email: {rental.get('customer_email', 'N/A')}")
                    print(f"    Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"    ⏱️  Time Left: {time_str}")
                    print(f"    📋 Action: {urgency_msg}")
                    
                    if minutes_remaining <= 10:
                        print(f"    ⚡ PASSWORD RESET REQUIRED NOW!")
                        print(f"    👉 Run: python main.py --mode run-once")
                    elif minutes_remaining <= 20:
                        reset_time = now + timedelta(minutes=minutes_remaining - 5)
                        print(f"    ⏰ Reset at: {reset_time.strftime('%H:%M:%S')}")
            
            # Get statistics
            try:
                stats = db.get_dashboard_stats()
                print("\n" + "-"*80)
                print(f"\n 📈 Overall Statistics:")
                print(f"    Total Accounts: {stats['total_accounts']}")
                print(f"    Available: {stats['available_accounts']} 🟢")
                print(f"    Rented: {stats['rented_accounts']} 🔵")
                print(f"    Exceptions: {stats['exception_accounts']} 🔴")
            except:
                pass
            
            print("\n" + "="*80)
            print(f" Next update in {refresh_seconds} seconds... (Press Ctrl+C to exit)")
            print("="*80)
            
            time.sleep(refresh_seconds)
            
    except KeyboardInterrupt:
        print("\n\n✓ Monitor stopped by user")
        print("\nThank you for using Rental Monitor! 👋\n")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        print("\nPlease check your Supabase connection.\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Rental Monitor')
    parser.add_argument(
        '--refresh',
        type=int,
        default=30,
        help='Refresh interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    monitor_rentals(refresh_seconds=args.refresh)
