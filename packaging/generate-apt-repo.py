#!/usr/bin/env python3
"""
Generate an APT flat repository (Packages, Packages.gz, Release, index.html)
from the built .deb packages in dist/.
"""

import os
import sys
import shutil
import gzip
import hashlib
import datetime
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(REPO_ROOT, "dist")
OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "build", "apt-repo")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Ensure .deb packages exist
deb_files = [f for f in os.listdir(DIST_DIR) if f.endswith(".deb")] if os.path.exists(DIST_DIR) else []
if not deb_files:
    print("==> No .deb files found in dist/. Building package first...")
    build_script = os.path.join(REPO_ROOT, "packaging", "build-deb.sh")
    subprocess.run([build_script], check=True)
    deb_files = [f for f in os.listdir(DIST_DIR) if f.endswith(".deb")]

if not deb_files:
    print("Error: Failed to find or generate .deb package.", file=sys.stderr)
    sys.exit(1)

# 2. Copy .deb files to target directory
for deb in deb_files:
    src = os.path.join(DIST_DIR, deb)
    dst = os.path.join(OUTPUT_DIR, deb)
    shutil.copy2(src, dst)
    print(f"==> Copied {deb} to {OUTPUT_DIR}")

# 3. Generate Packages index using dpkg-scanpackages
proc = subprocess.run(
    ["dpkg-scanpackages", ".", "/dev/null"],
    cwd=OUTPUT_DIR,
    capture_output=True,
    text=True,
    check=True
)
packages_content = proc.stdout
packages_path = os.path.join(OUTPUT_DIR, "Packages")
with open(packages_path, "w", encoding="utf-8") as f:
    f.write(packages_content)

# 4. Generate Packages.gz
packages_gz_path = os.path.join(OUTPUT_DIR, "Packages.gz")
with open(packages_gz_path, "wb") as f_out:
    f_out.write(gzip.compress(packages_content.encode("utf-8")))

# 5. Compute checksums
def get_file_info(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "rb") as f:
        data = f.read()
    return len(data), hashlib.md5(data).hexdigest(), hashlib.sha1(data).hexdigest(), hashlib.sha256(data).hexdigest()

files_to_hash = ["Packages", "Packages.gz"] + deb_files
file_info = {f: get_file_info(f) for f in files_to_hash}

now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")

release_content = f"""Archive: stable
Component: main
Origin: linux-audio-focus
Label: Linux Audio Focus Repository
Architecture: all amd64
Date: {now_utc}
MD5Sum:
""" + "\n".join(f" {info[1]} {info[0]} {f}" for f, info in file_info.items()) + """
SHA1:
""" + "\n".join(f" {info[2]} {info[0]} {f}" for f, info in file_info.items()) + """
SHA256:
""" + "\n".join(f" {info[3]} {info[0]} {f}" for f, info in file_info.items()) + "\n"

with open(os.path.join(OUTPUT_DIR, "Release"), "w", encoding="utf-8") as f:
    f.write(release_content)

# 6. Generate an index.html user guide
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Linux Audio Focus - APT Repository</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }}
    pre {{ background: #f4f4f7; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 14px; border: 1px solid #e1e4e8; }}
    code {{ color: #d63384; font-family: SFMono-Regular, Consolas, Monaco, monospace; }}
    pre code {{ color: #24292e; }}
    h1 {{ color: #111; }}
    .badge {{ display: inline-block; background: #0366d6; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; text-decoration: none; }}
  </style>
</head>
<body>
  <h1>Linux Audio Focus APT Repository</h1>
  <p>Official Debian/Ubuntu APT repository for <strong>Linux Audio Focus</strong>.</p>
  
  <h2>Installation Instructions</h2>
  <pre><code>echo "deb [trusted=yes] https://azmykn.github.io/linux-audio-focus/ ./" | sudo tee /etc/apt/sources.list.d/linux-audio-focus.list
sudo apt update
sudo apt install linux-audio-focus</code></pre>

  <h2>Direct Package Download</h2>
  <ul>
""" + "\n".join(f'    <li><a href="{deb}">{deb}</a></li>' for deb in deb_files) + f"""
  </ul>

  <p><a class="badge" href="https://github.com/azmykn/linux-audio-focus">View on GitHub</a></p>
</body>
</html>
"""

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print(f"==> Successfully generated APT repository in {OUTPUT_DIR}")
