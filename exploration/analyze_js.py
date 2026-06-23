"""Analyze the JS bundle to extract API endpoints and routes."""
import re
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT = os.path.dirname(os.path.abspath(__file__))
js_path = os.path.join(OUT, "index-Y23qub9R.js")

with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

print(f"JS bundle size: {len(js)} chars")

# Extract API endpoints
apis = re.findall(r'["\'](/api/[a-zA-Z0-9/_\-]+)["\']', js)
apis = sorted(set(apis))
print(f"\nAPI endpoints found: {len(apis)}")
for a in apis:
    print(f"  {a}")

# Extract route paths
routes = re.findall(r'path:\s*["\']([/][a-zA-Z0-9/_\-]*)["\']', js)
routes = sorted(set(routes))
print(f"\nRoutes found: {len(routes)}")
for r in routes:
    print(f"  {r}")

# Extract fetch/axios calls
fetch_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', js)
print(f"\nFetch calls: {len(fetch_calls)}")
for f in fetch_calls[:30]:
    print(f"  {f}")

# Extract component names (React)
components = re.findall(r'createElement\(([A-Z][a-zA-Z]+)', js)
components = sorted(set(components))
print(f"\nReact components: {len(components)}")
for c in components:
    print(f"  {c}")

# Look for navigation menu items
menu_items = re.findall(r'(?:label|title|name):\s*["\']([^"\']{2,30})["\']', js)
menu_items = sorted(set(menu_items))
print(f"\nLabels/titles found: {len(menu_items)}")
for m in menu_items:
    print(f"  {m}")

# Look for icon references (Remix Icon)
icons = re.findall(r'ri-[a-z\-]+', js)
icons = sorted(set(icons))
print(f"\nRemix icons: {len(icons)}")
for i in icons[:50]:
    print(f"  {i}")

print("\nDONE!")
