"""Shared lock for CPU-bound model inference."""
import threading


inference_lock = threading.Lock()