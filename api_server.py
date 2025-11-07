"""
Flask REST API for Tool Rental System
Provides endpoints for account rental management
"""

from flask import Flask, request, jsonify
from functools import wraps
from src.database import PasswordResetDB
from src.supabase_db import SupabaseDB
from src.api_manager import APIManager
from datetime import datetime

app = Flask(__name__)

# Use Supabase as primary database, SQLite as fallback
try:
    db = SupabaseDB()
    print("✓ Using Supabase cloud database")
except Exception as e:
    print(f"⚠ Supabase not available, falling back to SQLite: {e}")
    db = PasswordResetDB()

api_manager = APIManager()


# ===================== AUTHENTICATION =====================

def require_api_key(f):
    """Decorator to require valid API key for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'message': 'Please provide X-API-Key header'
            }), 401
        
        api_key_info = api_manager.validate_api_key(api_key)
        
        if not api_key_info:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'API key is invalid or revoked'
            }), 403
        
        # Update usage statistics
        api_manager.update_api_usage(api_key_info['id'])
        
        # Pass API key info to the route
        request.api_key_info = api_key_info
        
        return f(*args, **kwargs)
    
    return decorated_function


# ===================== PUBLIC ENDPOINTS =====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Tool Rental API'
    })


# ===================== ACCOUNT RENTAL ENDPOINTS =====================

@app.route('/api/accounts/available', methods=['GET'])
@require_api_key
def get_available_accounts():
    """
    Get list of available accounts.
    Query params:
        - website: Filter by website name (e.g., unlocktool, androidmultitool)
    """
    website = request.args.get('website')
    
    try:
        # Use Supabase's built-in function for auto-expiry
        if isinstance(db, SupabaseDB) and website:
            accounts = db.get_available_accounts(website)
        else:
            accounts = db.get_available_accounts(website)
        
        # Don't return passwords - only metadata
        safe_accounts = []
        for acc in accounts:
            safe_accounts.append({
                'id': acc.get('id'),
                'website': acc.get('website') or acc.get('websites', {}).get('name'),
                'username': acc.get('username'),
                'email': acc.get('email'),
                'validity_hours': acc.get('validity_hours') or acc.get('websites', {}).get('validity_hours'),
                'last_reset': acc.get('last_reset')
            })
        
        return jsonify({
            'success': True,
            'count': len(safe_accounts),
            'accounts': safe_accounts,
            'database': 'Supabase' if isinstance(db, SupabaseDB) else 'SQLite',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/accounts/rent', methods=['POST'])
@require_api_key
def rent_account():
    """
    Rent an available account.
    Body:
        - website: Website name (required)
        - customer_info: Customer details (optional)
    """
    data = request.get_json()
    
    if not data or 'website' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required field: website'
        }), 400
    
    website = data['website']
    customer_info = data.get('customer_info', f"API Key: {request.api_key_info['name']}")
    
    try:
        # Get available accounts for this website
        if isinstance(db, SupabaseDB):
            accounts = db.get_available_accounts(website)
            # Supabase returns different format
            if accounts:
                account = accounts[0]
                # Get website details
                website_info = db.get_website(website)
                account['validity_hours'] = website_info['validity_hours']
        else:
            accounts = db.get_available_accounts(website)
        
        if not accounts:
            return jsonify({
                'success': False,
                'error': 'No available accounts',
                'message': f'No accounts available for {website} at this time'
            }), 404
        
        # Rent the first available account
        account = accounts[0]
        customer_name = data.get('customer_name', customer_info)
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')
        
        if isinstance(db, SupabaseDB):
            rental = db.rent_account(
                account_id=account['id'],
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone
            )
        else:
            rental = db.rent_account(account['id'], customer_info)
        
        # Log the API request
        api_manager.log_api_request(
            api_key_id=request.api_key_info['id'],
            account_id=account['id'],
            website=website,
            action='rent',
            response_status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'success': True,
            'account': {
                'id': rental.get('account_id') or account['id'],
                'website': rental.get('website') or website,
                'username': rental.get('username') or account['username'],
                'password': rental.get('password') or account.get('current_password') or account.get('password'),
                'email': account.get('email'),
                'validity_hours': rental.get('validity_hours') or account.get('validity_hours'),
                'rental_id': rental.get('id'),
                'expires_at': rental.get('expires_at')
            },
            'message': f'Account rented successfully. Valid until {rental.get("expires_at")}',
            'database': 'Supabase' if isinstance(db, SupabaseDB) else 'SQLite',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        # Log failed request
        api_manager.log_api_request(
            api_key_id=request.api_key_info['id'],
            account_id=0,
            website=website,
            action='rent',
            response_status='error',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/accounts/return/<int:account_id>', methods=['POST'])
@require_api_key
def return_account(account_id):
    """Return a rented account early."""
    try:
        db.return_account(account_id)
        
        # Get website name for logging
        import sqlite3
        conn = sqlite3.connect(db.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.name FROM accounts a
            JOIN websites w ON a.website_id = w.id
            WHERE a.id = ?
        """, (account_id,))
        website = cursor.fetchone()[0]
        conn.close()
        
        # Log the API request
        api_manager.log_api_request(
            api_key_id=request.api_key_info['id'],
            account_id=account_id,
            website=website,
            action='return',
            response_status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'success': True,
            'message': 'Account returned successfully',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/accounts/status/<int:account_id>', methods=['GET'])
@require_api_key
def check_account_status(account_id):
    """Check the status of a specific account."""
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.username, a.status, w.name, r.expires_at, r.customer_name
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
            LEFT JOIN rentals r ON a.id = r.account_id AND r.status = 'active'
            WHERE a.id = ?
        """, (account_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        # Log the check request
        api_manager.log_api_request(
            api_key_id=request.api_key_info['id'],
            account_id=account_id,
            website=row[2],
            action='check',
            response_status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'success': True,
            'account': {
                'id': account_id,
                'username': row[0],
                'status': row[1],
                'website': row[2],
                'expires_at': row[3],
                'customer_name': row[4]
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===================== STATISTICS ENDPOINTS =====================

@app.route('/api/stats/me', methods=['GET'])
@require_api_key
def my_stats():
    """Get usage statistics for the current API key."""
    days = request.args.get('days', 30, type=int)
    
    try:
        stats = api_manager.get_usage_stats(
            api_key_id=request.api_key_info['id'],
            days=days
        )
        
        recent_activity = api_manager.get_recent_activity(
            api_key_id=request.api_key_info['id'],
            limit=10
        )
        
        return jsonify({
            'success': True,
            'api_key': {
                'name': request.api_key_info['name'],
                'total_requests': request.api_key_info['total_requests'],
                'rate_limit': request.api_key_info['rate_limit'],
                'created_at': request.api_key_info['created_at']
            },
            'stats': stats,
            'recent_activity': recent_activity,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


# ===================== MAIN =====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Tool Rental API Server")
    print("="*60)
    print("\nInitializing API management tables...")
    api_manager._init_api_tables()
    print("✓ API tables initialized\n")
    
    print("Starting server on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/accounts/available - List available accounts")
    print("  POST /api/accounts/rent - Rent an account")
    print("  POST /api/accounts/return/<id> - Return an account")
    print("  GET  /api/accounts/status/<id> - Check account status")
    print("  GET  /api/stats/me - Your usage statistics")
    print("\n" + "="*60 + "\n")
    
    # Run without debug mode for stability in production
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
