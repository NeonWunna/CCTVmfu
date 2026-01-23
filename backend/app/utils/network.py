import subprocess
import platform
import logging

def ping_ip(ip_address: str, timeout: int = 2) -> bool:
    """
    Ping an IP address to check if it's reachable.
    
    Args:
        ip_address: IP address to ping
        timeout: Timeout in seconds
        
    Returns:
        True if reachable, False otherwise
    """
    # Determine the ping parameter based on the operating system
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # helper for timeout
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = str(timeout * 1000) if platform.system().lower() == 'windows' else str(timeout)

    command = ['ping', param, '1', timeout_param, timeout_val, ip_address]
    
    try:
        # Run the ping command
        # stdout=subprocess.DEVNULL and stderr=subprocess.DEVNULL silence the output
        response = subprocess.run(
            command, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Error pinging {ip_address}: {e}")
        return False
