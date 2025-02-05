"""
JobSpy Sensitive Configuration Template
=====================================

Setup Instructions:
1. Copy this file to 'config_sensitive.py'
2. Fill in your actual values
3. Keep config_sensitive.py in .gitignore

Security Best Practices:
- Never commit config_sensitive.py to version control
- Store proxy credentials securely
- Rotate credentials regularly
- Use environment variables when possible
"""

SENSITIVE_CONFIG = {
    'proxy_enabled': True,  # Set to False to disable proxy usage
    
    # Add your proxy URLs here (at least one required if proxy_enabled is True)
    'proxy_list': [
        "http://your-username:your-password@your-proxy-host:port",
        "http://your-backup-proxy-url:port"  # Optional backup proxy
    ],
    
    # IP verification services (can be customized)
    'proxy_verification_urls': [
        'http://api.ipify.org?format=json',
        'http://ip-api.com/json',
        'http://ifconfig.me/ip'
    ],
    
    # Advanced Settings
    'proxy_timeout': 10,        # Seconds to wait for proxy response
    'max_retries': 3,          # Maximum retry attempts per proxy
    'rotate_interval': 100,    # Rotate proxy after N requests
    'verify_ssl': False        # Disable for some proxy configurations
}

"""
Example format for proxy_list entries:
- Bright Data format: "http://brd-customer-[username]-zone-[zone_name]:[password]@brd.superproxy.io:22225"
- Generic format: "http://username:password@host:port"

Security Notes:
1. Never commit config_sensitive.py to version control
2. Keep your proxy credentials secure
3. Regularly rotate proxy credentials if possible
""" 