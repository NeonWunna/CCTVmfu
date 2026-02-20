import subprocess
import platform
import logging
import asyncio

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

async def async_ping_ip(ip_address: str, timeout: int = 1) -> bool:
    """
    Ping an IP address asynchronously.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = str(timeout * 1000) if platform.system().lower() == 'windows' else str(timeout)

    command = ['ping', param, '1', timeout_param, timeout_val, ip_address]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()
        return process.returncode == 0
    except Exception as e:
        logging.error(f"Error async pinging {ip_address}: {e}")
        return False

async def check_port_async(ip_address: str, port: int = 80, timeout: float = 1.0) -> bool:
    """
    Check if a TCP port is open asynchronously.
    
    Args:
        ip_address: IP address to check
        port: Port to check (default 80)
        timeout: Timeout in seconds
        
    Returns:
        True if reachable, False otherwise
    """
    try:
        conn = asyncio.open_connection(ip_address, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

def check_port(ip_address: str, port: int = 80, timeout: int = 1) -> bool:
    """
    Check if a TCP port is open (synchronous).
    """
    import socket
    try:
        with socket.create_connection((ip_address, port), timeout=timeout):
            return True
    except:
        return False
