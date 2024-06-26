import multiprocessing
import os

max_workers_str = os.getenv("MAX_WORKERS", "2")
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "2")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)
    if max_workers_str is not None:
        max_workers = float(max_workers_str)
        if web_concurrency > max_workers:
            web_concurrency = max_workers_str


# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
keepalive = 120
errorlog = "-"
timeout = 900
captureoutput = True
max_requests = 50
max_requests_jitter = 10

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "host": host,
    "port": port,
    "max_requests": max_requests,
}
