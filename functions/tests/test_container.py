from __future__ import annotations


import subprocess
import time
from pathlib import Path

import pytest
import requests


@pytest.fixture(scope="session")
def docker_container() -> str | None:
    """Build and run the Docker container for testing."""
    project_root = Path(__file__).parent.parent.parent

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Docker is not available")
        return None

    # Build the image
    try:
        subprocess.run(
            ["docker", "build", "-t", "civiksutra-test", "."],
            cwd=project_root,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Docker build failed: {e.stderr.decode()}")

    # Run the container
    try:
        container_id = subprocess.run(
            ["docker", "run", "-d", "-p", "8080:8080", "civiksutra-test"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Docker run failed: {e.stderr.decode()}")

    # Wait for Nginx to start
    time.sleep(2)

    yield container_id

    # Cleanup
    subprocess.run(["docker", "stop", container_id], check=True, capture_output=True)
    subprocess.run(["docker", "rm", container_id], check=True, capture_output=True)


def test_docker_container_serves_frontend(docker_container: str | None) -> None:
    """Verify that the Docker container serves the frontend on port 8080."""
    if not docker_container:
        return

    # Test root endpoint
    response = requests.get("http://localhost:8080/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "CivikSutra" in response.text

    # Test health check / arbitrary path fallback (SPA routing)
    response = requests.get("http://localhost:8080/some-random-path")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "CivikSutra" in response.text
