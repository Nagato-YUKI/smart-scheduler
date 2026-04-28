# -*- coding: utf-8 -*-
"""深度诊断后端 API 404 问题"""
import urllib.request
import urllib.error
import json

BACKEND = "https://smart-scheduler-0q2w.onrender.com"

urls_to_test = [
    "/api/health",
    "/api/rooms",
    "/api/rooms/",
    "/rooms",
    "/rooms/",
    "/api/teachers",
    "/api/classes",
    "/api/courses",
    "/api/holidays",
    "/api/schedule/results",
    "/api/schedule/run",
]

for url in urls_to_test:
    full = f"{BACKEND}{url}"
    try:
        req = urllib.request.Request(full)
        req.add_header("User-Agent", "Mozilla/5.0")
        resp = urllib.request.urlopen(req, timeout=15)
        body = resp.read().decode("utf-8", errors="replace")
        print(f"[200] {url} -> {body[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[{e.code}] {url} -> {body[:200]}")
    except Exception as e:
        print(f"[ERR] {url} -> {str(e)}")
