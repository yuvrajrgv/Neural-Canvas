"""
Neuralcanvas - API Utilities and Session Management
"""
import streamlit as st
import requests
from typing import Optional, Tuple, Any, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'authenticated': False,
        'access_token': None,
        'refresh_token': None,
        'user': None,
        'current_job': None,
        'selected_style': 'cartoon',
        'classifier_result': None,
        'generator_result': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_request(
    method: str, 
    endpoint: str, 
    data: Optional[Dict] = None, 
    files: Optional[Dict] = None, 
    auth: bool = True
) -> Tuple[Optional[Any], Optional[str]]:
    """Make API request with optional authentication."""
    headers = {}
    if auth and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files, timeout=60)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return None, "Invalid method"
        
        if response.status_code in [200, 201]:
            try:
                return response.json(), None
            except:
                return response.content, None
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = f"HTTP {response.status_code}"
            return None, error_detail
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to server. Make sure the backend is running on port 8000."
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        return None, str(e)


def login(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """Login user and store tokens."""
    data = {"username": username, "password": password}
    result, error = api_request("POST", "/auth/login", data=data, auth=False)
    
    if result:
        st.session_state.authenticated = True
        st.session_state.access_token = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user = result["user"]
        return True, None
    return False, error


def signup(email: str, username: str, password: str, full_name: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Register new user."""
    data = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name
    }
    result, error = api_request("POST", "/auth/signup", data=data, auth=False)
    
    if result:
        st.session_state.authenticated = True
        st.session_state.access_token = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user = result["user"]
        return True, None
    return False, error


def logout():
    """Logout user and clear session."""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None
    st.session_state.current_job = None
    st.session_state.classifier_result = None
    st.session_state.generator_result = None


def upload_image(file, style: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Upload image for processing."""
    files = {"file": (file.name, file.getvalue(), file.type)}
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    url = f"{API_BASE_URL}/images/upload?style={style}"
    
    try:
        response = requests.post(url, headers=headers, files=files, timeout=60)
        if response.status_code in [200, 201]:
            return response.json(), None
        return None, response.json().get("detail", "Upload failed")
    except Exception as e:
        return None, str(e)


def process_image(job_id: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Start image processing."""
    return api_request("POST", f"/images/{job_id}/process")


def get_job_status(job_id: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Get job status."""
    return api_request("GET", f"/images/{job_id}")


def get_image(job_id: str, file_type: str) -> Tuple[Optional[bytes], Optional[str]]:
    """Get image file."""
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    url = f"{API_BASE_URL}/images/file/{job_id}/{file_type}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.content, None
        return None, "Failed to load image"
    except Exception as e:
        return None, str(e)


def get_user_jobs(page: int = 1, per_page: int = 50) -> Tuple[Optional[Dict], Optional[str]]:
    """Get user's image jobs."""
    return api_request("GET", "/images/", data={"page": page, "per_page": per_page})


# ============ Cartoon Classification API ============

def classify_cartoon(file) -> Tuple[Optional[Dict], Optional[str]]:
    """Classify cartoon image to identify celebrity."""
    files = {"file": (file.name, file.getvalue(), file.type)}
    url = f"{API_BASE_URL}/cartoon/classify?top_k=5"
    
    try:
        response = requests.post(url, files=files, timeout=60)
        if response.status_code == 200:
            return response.json(), None
        try:
            error = response.json().get("detail", "Classification failed")
        except:
            error = f"HTTP {response.status_code}"
        return None, error
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to server. Make sure the backend is running."
    except Exception as e:
        return None, str(e)


def get_classifier_info() -> Tuple[Optional[Dict], Optional[str]]:
    """Get cartoon classifier model info."""
    return api_request("GET", "/cartoon/info", auth=False)


def get_classifier_health() -> Tuple[Optional[Dict], Optional[str]]:
    """Get cartoon classifier health status."""
    return api_request("GET", "/cartoon/health", auth=False)


def get_all_identities() -> Tuple[Optional[Dict], Optional[str]]:
    """Get all recognizable celebrity identities."""
    return api_request("GET", "/cartoon/identities", auth=False)


# ============ Cartoon Generator API ============

def generate_cartoon(file) -> Tuple[Optional[bytes], Optional[str]]:
    """Generate cartoon from photo using DL model."""
    files = {"file": (file.name, file.getvalue(), file.type)}
    url = f"{API_BASE_URL}/cartoon/generate"
    
    try:
        response = requests.post(url, files=files, timeout=120)
        if response.status_code == 200:
            return response.content, None
        try:
            error = response.json().get("detail", "Generation failed")
        except:
            error = f"HTTP {response.status_code}"
        return None, error
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to server. Make sure the backend is running."
    except requests.exceptions.Timeout:
        return None, "Generation timed out. The image might be too large."
    except Exception as e:
        return None, str(e)


def get_generator_info() -> Tuple[Optional[Dict], Optional[str]]:
    """Get cartoon generator model info."""
    return api_request("GET", "/cartoon/generator/info", auth=False)


# ============ Utility Functions ============

def check_backend_status() -> bool:
    """Check if backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False


def format_identity_name(name: str) -> str:
    """Format identity name for display."""
    # Replace underscores with spaces and title case
    return name.replace('_', ' ').title()
