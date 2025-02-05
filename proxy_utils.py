from typing import Dict, Any, Optional
from requests import Session, Response
import requests
import warnings
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_proxy(proxy: str, verification_urls: list) -> bool:
    """Verify proxy is working and hiding the real IP"""
    try:
        # First check real IP
        real_ip = get_real_ip(verification_urls)
        if not real_ip:
            print("Could not verify real IP")
            return False
            
        proxy_ip = get_proxy_ip(proxy, verification_urls)
        if not proxy_ip:
            print("Could not verify proxy IP")
            return False
            
        if real_ip != proxy_ip:
            print(f"\nProxy verification successful!")
            print(f"Real IP: {real_ip[:3]}... (hidden for security)")
            print(f"Proxy IP: {proxy_ip}")
            return True
        else:
            print("\nWarning: Proxy not working - IPs match!")
            return False
            
    except Exception as e:
        print(f"\nProxy verification failed: {str(e)}")
        return False

def verify_proxy_usage(session: Session, url: str) -> Dict[str, Any]:
    """Verify proxy usage and return traffic stats"""
    try:
        response = session.get(url, stream=True)
        content_size = len(response.content)
        
        return {
            "status_code": response.status_code,
            "content_size": content_size,
            "headers": dict(response.headers),
            "proxy_used": bool(session.proxies)
        }
    except Exception as e:
        print(f"Error tracking proxy usage: {str(e)}")
        return {
            "status_code": 0,
            "content_size": 0,
            "headers": {},
            "proxy_used": False
        }

def get_real_ip(verification_urls: list) -> Optional[str]:
    """Get real IP address without proxy"""
    for url in verification_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.ok:
                return extract_ip(response, url)
        except:
            continue
    return None

def get_proxy_ip(proxy: str, verification_urls: list) -> Optional[str]:
    """Get IP address when using proxy"""
    proxies = {'http': proxy, 'https': proxy}
    session = requests.Session()
    session.verify = False
    
    for url in verification_urls:
        try:
            response = session.get(url, proxies=proxies, timeout=10)
            if response.ok:
                return extract_ip(response, url)
        except:
            continue
    return None

def extract_ip(response: Response, url: str) -> str:
    """Extract IP from response based on service used"""
    if 'ifconfig.me' in url:
        return response.text
    return response.json().get('ip', response.text) 