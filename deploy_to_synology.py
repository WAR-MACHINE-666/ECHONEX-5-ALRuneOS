# deploy_to_synology.py
import docker
import subprocess

def deploy_aeprs_to_synology():
    """Deploy AEPRS to Synology via Docker"""
    
    # Build Docker image
    subprocess.run([
        "docker", "build", 
        "-t", "aeprs-spectra:latest", 
        "."
    ])
    
    # Deploy via Cloudflare Tunnel
    subprocess.run([
        "docker", "run", "-d",
        "--name", "aeprs-production",
        "-p", "8080:8080",
        "-v", "/volume1/aeprs:/app/data",
        "aeprs-spectra:latest"
    ])

if __name__ == "__main__":
    deploy_aeprs_to_synology()