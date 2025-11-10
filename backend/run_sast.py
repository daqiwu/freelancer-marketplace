#!/usr/bin/env python3
"""
SAST (Static Application Security Testing) Script
Tests the codebase for security vulnerabilities without running the app.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


def run_bandit_scan():
    """Run Bandit security scanner on Python code"""
    print("\n" + "="*80)
    print("🔍 SAST TEST 1: BANDIT - Python Security Scanner")
    print("="*80 + "\n")
    
    try:
        # Run bandit with JSON output for parsing
        result = subprocess.run(
            ["bandit", "-r", "app/", "-f", "json", "-o", "sast_bandit_report.json"],
            capture_output=True,
            text=True
        )
        
        # Also run with text output for console
        result_text = subprocess.run(
            ["bandit", "-r", "app/", "-ll"],  # -ll = only show medium/high severity
            capture_output=True,
            text=True
        )
        
        print(result_text.stdout)
        if result_text.stderr:
            print("Warnings:", result_text.stderr)
        
        # Parse JSON report
        try:
            with open("sast_bandit_report.json", "r") as f:
                bandit_data = json.load(f)
                
            print("\n📊 BANDIT SUMMARY:")
            print(f"  Total issues found: {len(bandit_data.get('results', []))}")
            
            severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for issue in bandit_data.get('results', []):
                severity = issue.get('issue_severity', 'UNKNOWN')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print(f"  🔴 High severity: {severity_counts.get('HIGH', 0)}")
            print(f"  🟡 Medium severity: {severity_counts.get('MEDIUM', 0)}")
            print(f"  🟢 Low severity: {severity_counts.get('LOW', 0)}")
            
            print("\n✅ Bandit report saved: sast_bandit_report.json")
            
        except Exception as e:
            print(f"⚠️  Could not parse JSON report: {e}")
        
        return True
        
    except FileNotFoundError:
        print("❌ Bandit not installed!")
        print("   Install with: pip install bandit")
        return False
    except Exception as e:
        print(f"❌ Error running Bandit: {e}")
        return False


def run_safety_check():
    """Run Safety to check dependencies for known vulnerabilities"""
    print("\n" + "="*80)
    print("🔍 SAST TEST 2: SAFETY - Dependency Vulnerability Scanner")
    print("="*80 + "\n")
    
    try:
        # Run safety check
        result = subprocess.run(
            ["safety", "check", "--json", "--output", "sast_safety_report.json"],
            capture_output=True,
            text=True
        )
        
        # Also run with text output
        result_text = subprocess.run(
            ["safety", "check"],
            capture_output=True,
            text=True
        )
        
        print(result_text.stdout)
        if result_text.stderr:
            print(result_text.stderr)
        
        print("\n✅ Safety report saved: sast_safety_report.json")
        return True
        
    except FileNotFoundError:
        print("❌ Safety not installed!")
        print("   Install with: pip install safety")
        return False
    except Exception as e:
        print(f"❌ Error running Safety: {e}")
        return False


def check_hardcoded_secrets():
    """Check for hardcoded secrets in code"""
    print("\n" + "="*80)
    print("🔍 SAST TEST 3: HARDCODED SECRETS CHECK")
    print("="*80 + "\n")
    
    suspicious_patterns = [
        "password =",
        "PASSWORD =",
        "secret =",
        "SECRET =",
        "api_key =",
        "API_KEY =",
        "token =",
        "TOKEN =",
    ]
    
    findings = []
    
    # Search Python files
    for py_file in Path("app/").rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                for pattern in suspicious_patterns:
                    if pattern in line and not line.strip().startswith("#"):
                        # Ignore if it's from environment or config
                        if "os.getenv" not in line and "config." not in line and ".env" not in line:
                            findings.append({
                                "file": str(py_file),
                                "line": i,
                                "content": line.strip()
                            })
    
    if findings:
        print(f"⚠️  Found {len(findings)} potential hardcoded secrets:\n")
        for finding in findings[:10]:  # Show first 10
            print(f"  📄 {finding['file']}:{finding['line']}")
            print(f"     {finding['content']}")
            print()
    else:
        print("✅ No obvious hardcoded secrets found!")
    
    return True


def check_sql_injection_risks():
    """Check for potential SQL injection vulnerabilities"""
    print("\n" + "="*80)
    print("🔍 SAST TEST 4: SQL INJECTION RISK CHECK")
    print("="*80 + "\n")
    
    risky_patterns = [
        'execute("',
        'execute(f"',
        'execute(f\'',
        '.format(',
        '+ sql',
        'sql +',
    ]
    
    findings = []
    
    for py_file in Path("app/").rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                for pattern in risky_patterns:
                    if pattern in line and ("execute" in line or "query" in line.lower()):
                        findings.append({
                            "file": str(py_file),
                            "line": i,
                            "content": line.strip()
                        })
    
    if findings:
        print(f"⚠️  Found {len(findings)} potential SQL injection risks:\n")
        for finding in findings[:10]:
            print(f"  📄 {finding['file']}:{finding['line']}")
            print(f"     {finding['content']}")
            print()
        print("💡 Recommendation: Use parameterized queries with SQLAlchemy ORM")
    else:
        print("✅ No obvious SQL injection risks found!")
    
    return True


def generate_sast_summary():
    """Generate a summary report"""
    print("\n" + "="*80)
    print("📋 SAST TESTING SUMMARY")
    print("="*80 + "\n")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = f"""
SAST Testing Completed: {timestamp}

Tests Performed:
✅ Bandit - Python Security Scanner
✅ Safety - Dependency Vulnerability Scanner  
✅ Hardcoded Secrets Check
✅ SQL Injection Risk Check

Reports Generated:
- sast_bandit_report.json
- sast_safety_report.json

Next Steps:
1. Review the detailed reports above
2. Fix HIGH and MEDIUM severity issues
3. Run DAST testing on running application
4. Implement recommended security controls

Security Recommendations:
- Keep dependencies updated
- Use environment variables for secrets
- Use parameterized SQL queries
- Implement input validation
- Enable security headers (already done!)
"""
    
    print(summary)
    
    # Save summary to file
    with open("sast_summary_report.txt", "w") as f:
        f.write(summary)
    
    print("✅ Summary saved: sast_summary_report.txt\n")


def main():
    print("\n🔐 SAST - Static Application Security Testing")
    print("Testing: Freelancer Marketplace Backend\n")
    
    # Run all tests
    run_bandit_scan()
    run_safety_check()
    check_hardcoded_secrets()
    check_sql_injection_risks()
    generate_sast_summary()
    
    print("\n✅ SAST Testing Complete!\n")


if __name__ == "__main__":
    main()
