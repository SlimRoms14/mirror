#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

# Clone (or update) the repository
if os.path.isdir("slim_manifest"):
    print("Updating slim_manifest repository...")
    slim_manifest = git.Repo("slim_manifest")
    slim_manifest.remote("origin").fetch()
else:
    print("Downloading slim_manifest repository...")
    slim_manifest = git.Repo.clone_from(
        "https://github.com/SlimRoms14/manifest", "slim_manifest"
    )

# Get all the refs
refs = [
    re.search(r"remotes/(\S+)", tag).group(1)
    for tag in slim_manifest.git.branch(a=True).splitlines()
    if "remotes/" in tag
]

repos = set()

# Look for repo names in each ref
for index, ref in enumerate(refs, 1):
    print("[{}/{}] Parsing `{}`...".format(index, len(refs), ref))

    xml_todo = ["slim.xml"]

    # Load the XML
    while len(xml_todo) != 0:
        xml_name = xml_todo.pop(0)
        print("  - {}".format(xml_name))

        xml = ET.fromstring(slim_manifest.git.show("{}:{}".format(ref, xml_name)))

        for child in xml:
            if child.tag == "include":
                xml_todo.append(child.attrib["name"])
                continue

            # Skip all non-project tags
            if child.tag != "project":
                continue

            # Ignore non-SlimRoms projects
            if not child.attrib["name"].startswith("SlimRoms14/"):
                continue

            repos.add(child.attrib["name"].rstrip("/"))


file = open("slim-minimal.xml", "w")
file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
file.write("<manifest>\n")
file.write("\n")
file.write('  <remote  name="github"\n')
file.write('           fetch=".." />\n')
file.write('  <default revision="main"\n')
file.write('           remote="github"\n')
file.write('           sync-j="4" />\n')
file.write("\n")

for repo in sorted(repos):
    file.write('  <project name="' + repo + '" />\n')

file.write("</manifest>\n")
file.close()
