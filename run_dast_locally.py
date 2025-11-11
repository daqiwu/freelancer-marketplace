#!/usr/bin/env python3
"""
Local DAST Testing Script using OWASP ZAP
Run this script to test your API endpoint locally before pushing to GitHub
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

# Configuration
TARGET_URL = 'https://u7tnmpvsm8.ap-southeast-1.awsapprunner.com'
ZAP_PROXY = 'http://localhost:8090'
ZAP_CONTAINER_NAME = 'zap-local-test'

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "━" * 60)
    print(f"  {text}")
    print("━" * 60)

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        print(f"✅ Docker found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker Desktop.")
        return False

def start_zap_container():
    """Start OWASP ZAP in Docker container"""
    print_banner("Starting OWASP ZAP Container")
    
    # Stop and remove existing container if it exists
    subprocess.run(['docker', 'stop', ZAP_CONTAINER_NAME], 
                   capture_output=True, stderr=subprocess.DEVNULL)
    subprocess.run(['docker', 'rm', ZAP_CONTAINER_NAME], 
                   capture_output=True, stderr=subprocess.DEVNULL)
    
    print("🐳 Pulling OWASP ZAP Docker image...")
    subprocess.run(['docker', 'pull', 'ghcr.io/zaproxy/zaproxy:stable'], check=True)
    
    print("🚀 Starting ZAP container...")
    cmd = [
        'docker', 'run', '-d',
        '--name', ZAP_CONTAINER_NAME,
        '-u', 'zap',
        '-p', '8090:8080',
        'ghcr.io/zaproxy/zaproxy:stable',
        'zap.sh', '-daemon',
        '-host', '0.0.0.0',
        '-port', '8080',
        '-config', 'api.disablekey=true',
        '-config', 'api.addrs.addr.name=.*',
        '-config', 'api.addrs.addr.regex=true'
    ]
    
    subprocess.run(cmd, check=True)
    
    print("⏳ Waiting for ZAP to start (30 seconds)...")
    for i in range(30, 0, -1):
        print(f"   {i} seconds remaining...", end='\r')
        time.sleep(1)
    
    # Verify ZAP is running
    try:
        response = requests.get(f'{ZAP_PROXY}/', timeout=5)
        print("\n✅ ZAP is running and accessible")
        return True
    except Exception as e:
        print(f"\n⚠️  ZAP might not be fully ready: {e}")
        return False

def test_security_headers():
    """Test security headers on the target"""
    print_banner("Security Headers Validation")
    
    headers_to_check = [
        'Strict-Transport-Security',
        'X-Content-Type-Options',
        'X-Frame-Options',
        'Content-Security-Policy',
        'X-XSS-Protection',
        'Referrer-Policy',
        'Permissions-Policy'
    ]
    
    try:
        response = requests.get(f"{TARGET_URL}/health", timeout=10)
        print(f"🎯 Testing: {TARGET_URL}/health")
        print(f"📊 Status Code: {response.status_code}\n")
        
        missing_headers = []
        for header in headers_to_check:
            if header in response.headers:
                value = response.headers[header][:60]
                print(f"   ✅ {header}: {value}")
            else:
                print(f"   ❌ {header}: MISSING")
                missing_headers.append(header)
        
        if not missing_headers:
            print("\n✅ All security headers present!")
        else:
            print(f"\n⚠️  Missing {len(missing_headers)} security header(s)")
        
        return len(missing_headers) == 0
    
    except Exception as e:
        print(f"❌ Error testing headers: {e}")
        return False

def test_endpoints():
    """Test common API endpoints"""
    print_banner("API Endpoints Testing")
    
    endpoints = [
        '/health',
        '/docs',
        '/openapi.json',
        '/api/v1/',
        '/auth/login',
        '/auth/register'
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            url = f"{TARGET_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            status_emoji = "✅" if response.status_code < 500 else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            results.append((endpoint, response.status_code))
        except Exception as e:
            print(f"   ⚠️  {endpoint}: {str(e)[:50]}")
            results.append((endpoint, 'ERROR'))
    
    return results

def run_zap_spider():
    """Run ZAP spider scan"""
    print_banner("ZAP Spider Scan")
    
    try:
        # Start spider scan
        print(f"🕷️  Starting spider scan on {TARGET_URL}...")
        resp = requests.get(
            f"{ZAP_PROXY}/JSON/spider/action/scan/",
            params={'url': TARGET_URL},
            timeout=10
        )
        scan_id = resp.json()['scan']
        print(f"   Scan ID: {scan_id}")
        
        # Monitor progress
        while True:
            resp = requests.get(
                f"{ZAP_PROXY}/JSON/spider/view/status/",
                params={'scanId': scan_id},
                timeout=10
            )
            status = int(resp.json()['status'])
            print(f"   Progress: {status}%", end='\r')
            
            if status >= 100:
                break
            time.sleep(3)
        
        print("\n✅ Spider scan completed")
        
        # Get URLs found
        resp = requests.get(f"{ZAP_PROXY}/JSON/core/view/urls/", timeout=10)
        urls = resp.json()['urls']
        print(f"   📍 URLs found: {len(urls)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Spider scan error: {e}")
        return False

def run_zap_active_scan():
    """Run ZAP active scan"""
    print_banner("ZAP Active Scan")
    
    try:
        print(f"⚡ Starting active scan on {TARGET_URL}...")
        print("⚠️  This may take several minutes...")
        
        resp = requests.get(
            f"{ZAP_PROXY}/JSON/ascan/action/scan/",
            params={'url': TARGET_URL},
            timeout=10
        )
        scan_id = resp.json()['scan']
        print(f"   Scan ID: {scan_id}")
        
        # Monitor progress
        while True:
            resp = requests.get(
                f"{ZAP_PROXY}/JSON/ascan/view/status/",
                params={'scanId': scan_id},
                timeout=10
            )
            status = int(resp.json()['status'])
            print(f"   Progress: {status}%", end='\r')
            
            if status >= 100:
                break
            time.sleep(5)
        
        print("\n✅ Active scan completed")
        return True
    
    except Exception as e:
        print(f"❌ Active scan error: {e}")
        return False

def get_zap_alerts():
    """Get ZAP alerts and generate report"""
    print_banner("Security Alerts Summary")
    
    try:
        resp = requests.get(
            f"{ZAP_PROXY}/JSON/core/view/alerts/",
            params={'baseurl': TARGET_URL},
            timeout=10
        )
        alerts = resp.json()['alerts']
        
        # Count by severity
        severity_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}
        for alert in alerts:
            risk = alert.get('risk', 'Informational')
            severity_counts[risk] = severity_counts.get(risk, 0) + 1
        
        print(f"   🔴 High: {severity_counts.get('High', 0)}")
        print(f"   🟡 Medium: {severity_counts.get('Medium', 0)}")
        print(f"   🟢 Low: {severity_counts.get('Low', 0)}")
        print(f"   ℹ️  Informational: {severity_counts.get('Informational', 0)}")
        print(f"   📋 Total Alerts: {len(alerts)}")
        
        # Save detailed alerts
        report_file = f'zap_local_alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        print(f"\n💾 Detailed alerts saved to: {report_file}")
        
        # Generate HTML report
        try:
            resp = requests.get(f"{ZAP_PROXY}/OTHER/core/other/htmlreport/", timeout=30)
            html_file = f'zap_local_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(f"📄 HTML report saved to: {html_file}")
        except Exception as e:
            print(f"⚠️  Could not generate HTML report: {e}")
        
        return alerts, severity_counts
    
    except Exception as e:
        print(f"❌ Error getting alerts: {e}")
        return [], {}

def stop_zap_container():
    """Stop and remove ZAP container"""
    print_banner("Cleanup")
    print("🧹 Stopping ZAP container...")
    subprocess.run(['docker', 'stop', ZAP_CONTAINER_NAME], 
                   capture_output=True, stderr=subprocess.DEVNULL)
    subprocess.run(['docker', 'rm', ZAP_CONTAINER_NAME], 
                   capture_output=True, stderr=subprocess.DEVNULL)
    print("✅ Cleanup completed")

def main():
    """Main execution flow"""
    print_banner("Local DAST Testing - OWASP ZAP")
    print(f"🎯 Target: {TARGET_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check prerequisites
        if not check_docker():
            sys.exit(1)
        
        # Start ZAP
        if not start_zap_container():
            print("⚠️  ZAP may not be fully ready, but continuing...")
        
        # Run tests
        test_security_headers()
        test_endpoints()
        
        # ZAP scans
        if run_zap_spider():
            # Wait for passive scan
            print("\n⏳ Waiting for passive scan to complete (15 seconds)...")
            time.sleep(15)
        
        # Ask user if they want to run active scan (takes longer)
        print("\n" + "━" * 60)
        response = input("⚡ Run active scan? This may take 5-10 minutes (y/n): ").lower()
        if response == 'y':
            run_zap_active_scan()
        else:
            print("⏭️  Skipping active scan")
        
        # Get results
        alerts, severity = get_zap_alerts()
        
        # Final summary
        print_banner("DAST Testing Complete")
        print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if severity.get('High', 0) > 0:
            print("\n❌ HIGH SEVERITY ISSUES DETECTED!")
            print("   Review the generated reports before deploying.")
            return_code = 1
        else:
            print("\n✅ No high severity issues detected")
            print("   Review reports for medium/low issues.")
            return_code = 0
        
        print("\n📁 Reports generated:")
        print("   - zap_local_alerts_*.json (detailed findings)")
        print("   - zap_local_report_*.html (visual report)")
        print("\n🚀 Next steps:")
        print("   1. Review the generated reports")
        print("   2. Fix any high/medium severity issues")
        print("   3. Push to GitHub to run automated DAST in CI/CD")
        
        return return_code
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        stop_zap_container()

if __name__ == '__main__':
    sys.exit(main())
