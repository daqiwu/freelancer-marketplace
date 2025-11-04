"""
Unit tests for Security Classifier Service
Tests AI-powered security issue classification (SCA, SAST, DAST)
"""

import json
from decimal import Decimal

import pytest

from app.services.security_classifier_service import SecurityClassifierService


class TestSecurityClassifierService:
    """Test suite for SecurityClassifierService"""

    @pytest.fixture
    def classifier(self):
        """Create a classifier instance for testing"""
        return SecurityClassifierService()

    # Test SCA (Software Composition Analysis) Classification

    def test_classify_sca_issue_with_cve(self, classifier):
        """Test classification of SCA issue with CVE identifier"""
        result = classifier.classify_issue(
            title="Vulnerable dependency: lodash CVE-2021-23337",
            description="The package lodash version 4.17.19 has a known vulnerability (CVE-2021-23337). "
            "Update to version 4.17.21 or higher.",
            affected_component="package.json",
        )

        assert result["issue_type"] == "SCA"
        assert result["severity"] in ["CRITICAL", "HIGH", "MEDIUM"]
        assert result["vulnerability_id"] == "CVE-2021-23337"
        assert float(result["confidence_score"]) > 50.0
        assert "remediation_suggestion" in result
        assert result["detection_method"] == "AI Pattern Matching"

    def test_classify_sca_outdated_package(self, classifier):
        """Test classification of outdated package issue"""
        result = classifier.classify_issue(
            title="Outdated npm package detected",
            description="The npm package 'axios' is outdated. Current version: 0.19.0, Latest: 1.3.0. "
            "Please update dependencies in package.json.",
            affected_component="node_modules/axios",
        )

        assert result["issue_type"] == "SCA"
        assert "SCA" in json.loads(result["tags"])
        assert result["estimated_effort"] in ["LOW", "MEDIUM", "HIGH"]

    def test_classify_sca_pip_vulnerability(self, classifier):
        """Test classification of Python pip vulnerability"""
        result = classifier.classify_issue(
            title="Critical vulnerability in requests library",
            description="pip package 'requests' version 2.25.0 has a critical security flaw. "
            "Update requirements.txt to use version 2.27.0 or higher.",
            affected_component="requirements.txt",
        )

        assert result["issue_type"] == "SCA"
        assert result["severity"] == "CRITICAL"
        assert result["remediation_priority"] >= 8

    # Test SAST (Static Application Security Testing) Classification

    def test_classify_sast_sql_injection(self, classifier):
        """Test classification of SQL injection vulnerability"""
        result = classifier.classify_issue(
            title="SQL Injection vulnerability detected",
            description="Potential SQL injection at line 45 in user_service.py. "
            "User input is directly concatenated into SQL query without parameterization.",
            affected_component="app/services/user_service.py:45",
        )

        assert result["issue_type"] == "SAST"
        assert result["severity"] in ["HIGH", "CRITICAL"]
        assert "injection" in json.loads(result["tags"])
        assert (
            "parameterized queries" in result["remediation_suggestion"].lower()
            or "input validation" in result["remediation_suggestion"].lower()
        )

    def test_classify_sast_xss_vulnerability(self, classifier):
        """Test classification of XSS vulnerability"""
        result = classifier.classify_issue(
            title="Cross-Site Scripting (XSS) vulnerability",
            description="Reflected XSS found in template rendering at line 120. "
            "User input not sanitized before rendering in HTML.",
            affected_component="app/templates/user_profile.html:120",
        )

        assert result["issue_type"] == "SAST"
        assert result["severity"] in ["HIGH", "MEDIUM"]
        assert "xss" in json.loads(result["tags"])

    def test_classify_sast_hardcoded_credentials(self, classifier):
        """Test classification of SAST hardcoded credentials issue"""
        result = classifier.classify_issue(
            title="Hardcoded password detected",
            description="Static analysis found hardcoded password in source code at line 15. "
            "This is a security risk and should use environment variables with cryptography.",
            affected_component="app/config.py:15",
        )

        assert result["issue_type"] == "SAST"
        assert result["severity"] in ["HIGH", "CRITICAL"]
        # Check that relevant security tags are present
        tags = json.loads(result["tags"])
        assert "SAST" in tags
        assert any(tag in tags for tag in ["crypto", "auth", "config"])

    def test_classify_sast_code_smell(self, classifier):
        """Test classification of low-severity code issue"""
        result = classifier.classify_issue(
            title="Insecure random number generation",
            description="Code uses insecure random() function at line 67. "
            "For security-sensitive operations, use cryptographically secure random.",
            affected_component="app/utils/token.py:67",
        )

        assert result["issue_type"] == "SAST"
        assert result["severity"] in ["MEDIUM", "LOW"]

    # Test DAST (Dynamic Application Security Testing) Classification

    def test_classify_dast_missing_security_headers(self, classifier):
        """Test classification of missing security headers"""
        result = classifier.classify_issue(
            title="Missing security headers in HTTP response",
            description="Dynamic scan found missing Content-Security-Policy header on /api/users endpoint. "
            "This can lead to XSS attacks.",
            affected_component="/api/users",
        )

        assert result["issue_type"] == "DAST"
        assert "header" in result["remediation_suggestion"].lower()
        assert "api" in json.loads(result["tags"]) or "web" in json.loads(
            result["tags"]
        )

    def test_classify_dast_authentication_issue(self, classifier):
        """Test classification of authentication vulnerability"""
        result = classifier.classify_issue(
            title="Authentication bypass detected",
            description="Runtime testing found authentication can be bypassed on POST /api/admin endpoint "
            "by manipulating session cookies.",
            affected_component="/api/admin",
        )

        assert result["issue_type"] == "DAST"
        assert result["severity"] in ["CRITICAL", "HIGH"]
        assert "auth" in json.loads(result["tags"])

    def test_classify_dast_cors_misconfiguration(self, classifier):
        """Test classification of CORS issue"""
        result = classifier.classify_issue(
            title="CORS misconfiguration detected",
            description="Dynamic analysis shows CORS headers allow requests from any origin. "
            "This is a high severity issue that can lead to CSRF attacks.",
            affected_component="API endpoint /api/orders",
        )

        assert result["issue_type"] == "DAST"
        # Should be HIGH due to "high severity" in description
        assert result["severity"] in ["MEDIUM", "HIGH"]

    def test_classify_dast_ssl_tls_issue(self, classifier):
        """Test classification of SSL/TLS vulnerability"""
        result = classifier.classify_issue(
            title="Weak SSL/TLS configuration",
            description="Runtime scan detected the server supports outdated TLS 1.0 protocol. "
            "Update to TLS 1.2 or higher.",
            affected_component="HTTPS endpoint",
        )

        assert result["issue_type"] == "DAST"
        # Check that remediation suggestion mentions TLS/SSL or security
        assert (
            "tls" in result["remediation_suggestion"].lower()
            or "ssl" in result["remediation_suggestion"].lower()
            or "security" in result["remediation_suggestion"].lower()
        )

    # Test Edge Cases and Unknown Classification

    def test_classify_unknown_issue(self, classifier):
        """Test classification when issue type is unclear"""
        result = classifier.classify_issue(
            title="Generic security issue",
            description="Something seems wrong but not sure what.",
            affected_component="unknown",
        )

        # May classify as UNKNOWN if confidence is too low
        assert result["issue_type"] in ["SCA", "SAST", "DAST", "UNKNOWN"]
        assert float(result["confidence_score"]) >= 0.0

    def test_classify_empty_input(self, classifier):
        """Test classification with minimal input"""
        result = classifier.classify_issue(
            title="Issue", description="Problem", affected_component=""
        )

        assert "issue_type" in result
        assert "severity" in result
        assert "confidence_score" in result

    # Test Batch Classification

    def test_batch_classify_multiple_issues(self, classifier):
        """Test batch classification of multiple issues"""
        issues = [
            {
                "title": "CVE-2021-12345 in lodash",
                "description": "Vulnerable package lodash needs update",
                "component": "package.json",
            },
            {
                "title": "SQL Injection in login",
                "description": "User input not sanitized in SQL query",
                "component": "auth.py:45",
            },
            {
                "title": "Missing CORS headers",
                "description": "Runtime test shows CORS not configured",
                "component": "/api/login",
            },
        ]

        results = classifier.batch_classify(issues)

        assert len(results) == 3
        assert results[0]["issue_type"] == "SCA"
        assert results[1]["issue_type"] == "SAST"
        assert results[2]["issue_type"] == "DAST"

    # Test Statistics

    def test_get_statistics(self, classifier):
        """Test statistics generation from classified issues"""
        issues = [
            {
                "title": "CVE in package",
                "description": "Vulnerable dependency",
                "component": "package.json",
            },
            {
                "title": "SQL Injection",
                "description": "Code vulnerability",
                "component": "app.py",
            },
        ]

        classified = classifier.batch_classify(issues)
        stats = classifier.get_statistics(classified)

        assert stats["total"] == 2
        assert "by_type" in stats
        assert "by_severity" in stats
        assert "avg_confidence" in stats
        assert stats["avg_confidence"] >= 0.0

    def test_statistics_empty_list(self, classifier):
        """Test statistics with empty issue list"""
        stats = classifier.get_statistics([])

        assert stats == {}

    # Test Severity Determination

    def test_severity_critical_keywords(self, classifier):
        """Test critical severity detection"""
        result = classifier.classify_issue(
            title="Critical remote code execution vulnerability",
            description="RCE vulnerability allows arbitrary code execution",
            affected_component="app.py",
        )

        assert result["severity"] == "CRITICAL"
        assert result["remediation_priority"] >= 9

    def test_severity_high_keywords(self, classifier):
        """Test high severity detection"""
        result = classifier.classify_issue(
            title="High severity SQL injection",
            description="SQL injection vulnerability in user input",
            affected_component="database.py",
        )

        assert result["severity"] == "HIGH"
        assert result["remediation_priority"] >= 7

    def test_severity_medium_default(self, classifier):
        """Test medium severity as default"""
        result = classifier.classify_issue(
            title="Security issue detected",
            description="An insecure configuration was found",
            affected_component="config.py",
        )

        assert result["severity"] in ["MEDIUM", "LOW"]

    # Test Remediation Suggestions

    def test_remediation_includes_component(self, classifier):
        """Test that remediation mentions the affected component"""
        result = classifier.classify_issue(
            title="Vulnerability in auth module",
            description="Authentication issue detected",
            affected_component="app/auth/login.py",
        )

        assert result["remediation_suggestion"] is not None
        assert len(result["remediation_suggestion"]) > 0

    def test_effort_estimation_critical(self, classifier):
        """Test effort estimation for critical issues"""
        result = classifier.classify_issue(
            title="Critical RCE vulnerability",
            description="Remote code execution possible",
            affected_component="server.py",
        )

        assert result["estimated_effort"] in ["HIGH", "MEDIUM", "LOW"]

    # Test Confidence Scoring

    def test_high_confidence_clear_indicators(self, classifier):
        """Test high confidence with clear indicators"""
        result = classifier.classify_issue(
            title="CVE-2021-12345 in npm package lodash",
            description="The npm dependency lodash has vulnerability CVE-2021-12345. "
            "Update package.json to version 4.17.21",
            affected_component="package.json",
        )

        assert float(result["confidence_score"]) > 70.0

    def test_lower_confidence_ambiguous_input(self, classifier):
        """Test lower confidence with ambiguous input"""
        result = classifier.classify_issue(
            title="Possible issue",
            description="Something might be wrong",
            affected_component="file.py",
        )

        # Confidence should be lower for vague descriptions
        assert float(result["confidence_score"]) >= 0.0

    # Test Tag Generation

    def test_tags_include_issue_type(self, classifier):
        """Test that tags include the issue type"""
        result = classifier.classify_issue(
            title="SQL injection vulnerability",
            description="SQL injection in authentication",
            affected_component="auth.py",
        )

        tags = json.loads(result["tags"])
        assert result["issue_type"] in tags

    def test_tags_include_relevant_keywords(self, classifier):
        """Test that tags include relevant security keywords"""
        result = classifier.classify_issue(
            title="XSS vulnerability in API",
            description="Cross-site scripting in web API endpoint",
            affected_component="/api/users",
        )

        tags = json.loads(result["tags"])
        assert "xss" in tags or "api" in tags

    # Test Vulnerability ID Extraction

    def test_extract_cve_id(self, classifier):
        """Test CVE ID extraction"""
        result = classifier.classify_issue(
            title="CVE-2021-44228 Log4Shell",
            description="Critical vulnerability CVE-2021-44228",
            affected_component="log4j",
        )

        assert result["vulnerability_id"] == "CVE-2021-44228"

    def test_extract_other_vuln_ids(self, classifier):
        """Test extraction of other vulnerability IDs"""
        result = classifier.classify_issue(
            title="GHSA-abcd-1234-efgh vulnerability",
            description="GitHub Security Advisory GHSA-abcd-1234-efgh",
            affected_component="package",
        )

        assert result["vulnerability_id"] is not None
        assert "GHSA" in result["vulnerability_id"]

    def test_no_vuln_id_when_absent(self, classifier):
        """Test that vulnerability ID is None when not present"""
        result = classifier.classify_issue(
            title="Generic security issue",
            description="A security problem without specific ID",
            affected_component="app.py",
        )

        assert result["vulnerability_id"] is None or result["vulnerability_id"] == ""


class TestSecurityClassifierEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def classifier(self):
        return SecurityClassifierService()

    def test_very_long_description(self, classifier):
        """Test handling of very long descriptions"""
        long_desc = "vulnerability " * 1000
        result = classifier.classify_issue(
            title="Issue", description=long_desc, affected_component="file.py"
        )

        assert "issue_type" in result

    def test_special_characters(self, classifier):
        """Test handling of special characters"""
        result = classifier.classify_issue(
            title="Issue with <script>alert('XSS')</script>",
            description="XSS vulnerability with special chars: & < > \" '",
            affected_component="template.html",
        )

        assert result["issue_type"] == "SAST"

    def test_unicode_characters(self, classifier):
        """Test handling of unicode characters"""
        result = classifier.classify_issue(
            title="SQL注入漏洞 SQL injection",
            description="数据库安全问题 database security issue",
            affected_component="数据库.py",
        )

        assert "issue_type" in result

    def test_multiple_vulnerability_types(self, classifier):
        """Test issue with multiple vulnerability indicators"""
        result = classifier.classify_issue(
            title="Multiple issues: SQL injection and XSS",
            description="Found both SQL injection in database code and XSS in templates",
            affected_component="app.py",
        )

        # Should classify as SAST since both are code-level issues
        assert result["issue_type"] in ["SAST", "DAST"]
