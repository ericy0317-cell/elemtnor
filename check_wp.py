# -*- coding: utf-8 -*-
import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

WP_URL = "https://yange14.sg-host.com"
USER = "243626599@qq.com"
PASS = "8008208820dhc"

session = requests.Session()
r = session.post(f"{WP_URL}/wp-login.php", data={
    "log": USER,
    "pwd": PASS,
    "wp-submit": "Log In",
    "redirect_to": f"{WP_URL}/wp-admin/",
    "testcookie": "1"
}, allow_redirects=False)
print("Login status:", r.status_code)
print("Set-Cookie:", dict(r.headers).get("Set-Cookie","")[:100])

# Follow redirect
if r.status_code == 302:
    redirect_url = r.headers.get("Location","")
    print("Redirect to:", redirect_url)
    r2 = session.get(f"{WP_URL}{redirect_url}" if redirect_url.startswith("/") else redirect_url)
    print("After redirect:", r2.status_code)
    if "wp-admin" in r2.url:
        print("OK - Logged in to admin")
    else:
        # Try with cookies manually
        print("Not admin, trying login again...")
        r = session.post(f"{WP_URL}/wp-login.php", data={
            "log": USER,
            "pwd": PASS,
            "wp-submit": "Log In",
            "redirect_to": f"{WP_URL}/wp-admin/",
            "testcookie": "1"
        })
        print("Login final URL:", r.url)
        print("Login final status:", r.status_code)

# Check cookies
for cookie in session.cookies:
    print(f"Cookie: {cookie.name}={cookie.value[:30]}")
