#!/usr/bin/env python
"""
Test to reproduce the issue with missing hostname and timestamp in JUnit XML reports.

This test will:
1. Create a simple test file
2. Run pytest with --junitxml option
3. Parse the generated XML file
4. Check if hostname and timestamp attributes are present in the testsuite element
"""
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import tempfile
import shutil

def test_hostname_timestamp_in_junit_xml():
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple test file
        test_file = os.path.join(tmpdir, "test_example.py")
        with open(test_file, "w") as f:
            f.write("""
def test_pass():
    assert True

def test_fail():
    assert False
""")

        # Create a path for the JUnit XML output
        xml_file = os.path.join(tmpdir, "junit-report.xml")

        # Run pytest with JUnit XML output
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            test_file,
            "--junitxml", xml_file,
            "-v"
        ], capture_output=True, text=True)

        # Check that pytest ran successfully (we expect some failures)
        if result.returncode not in [0, 1]:  # 0 = all passed, 1 = some failed
            print(f"pytest failed with return code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        # Parse the generated XML file
        if not os.path.exists(xml_file):
            print(f"XML file not created: {xml_file}")
            return False

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Find the testsuite element
        testsuite = None
        for elem in root:
            if elem.tag.endswith("testsuite"):
                testsuite = elem
                break

        if testsuite is None:
            print("No testsuite element found in XML")
            return False

        # Check for hostname attribute
        hostname = testsuite.get("hostname")
        if hostname is None:
            print("FAIL: hostname attribute is missing from testsuite element")
            print(f"testsuite attributes: {testsuite.attrib}")
            return False
        else:
            print(f"PASS: hostname attribute found: {hostname}")

        # Check for timestamp attribute
        timestamp = testsuite.get("timestamp")
        if timestamp is None:
            print("FAIL: timestamp attribute is missing from testsuite element")
            print(f"testsuite attributes: {testsuite.attrib}")
            return False
        else:
            print(f"PASS: timestamp attribute found: {timestamp}")

        return True

if __name__ == "__main__":
    success = test_hostname_timestamp_in_junit_xml()
    if success:
        print("\nTest PASSED - hostname and timestamp attributes are present")
        sys.exit(0)
    else:
        print("\nTest FAILED - hostname and/or timestamp attributes are missing")
        sys.exit(1)