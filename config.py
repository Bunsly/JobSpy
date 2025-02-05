# Default configuration that can be committed
DEFAULT_CONFIG = {
    'search_term': 'IT Engineer',
    'location': 'Lone Tree, CO',
    'distance': 25,
    'results_wanted': 50,
    'job_type': 'fulltime',
    'hours_old': 72,
    'search_sites': ["indeed", "linkedin"],
    'exclude_clearance': True,
    'clearance_keywords': [
        'clearance', 'security clearance', 'secret', 'top secret', 
        'ts/sci', 'sci', 'classified', 'poly', 'polygraph',
        'public trust', 'security+', 'security plus'
    ]
}


try:
    # Try to import sensitive config from a local file
    from .config_sensitive import SENSITIVE_CONFIG
except ImportError:
    print("Warning: No sensitive configuration found. Using defaults.") 