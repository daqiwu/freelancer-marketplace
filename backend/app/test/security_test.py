# app/test/security_test.py
import pytest
from app.services.security_classifier_service import SecurityClassifierService


class TestSecurityClassifier:
    """安全分类器测试"""

    def test_detect_phone_number(self):
        """测试检测电话号码"""
        service = SecurityClassifierService()
        assert service.has_sensitive_info("我的电话是13812345678") is True
        assert service.has_sensitive_info("请联系15987654321") is True
        assert service.has_sensitive_info("正常文本") is False

    def test_detect_email(self):
        """测试检测邮箱"""
        service = SecurityClassifierService()
        assert service.has_sensitive_info("联系我 test@example.com") is True
        assert service.has_sensitive_info("发邮件到 user@domain.com") is True
        assert service.has_sensitive_info("正常文本") is False

    def test_detect_id_card(self):
        """测试检测身份证号"""
        service = SecurityClassifierService()
        assert service.has_sensitive_info("身份证号 110101199001011234") is True
        assert service.has_sensitive_info("正常文本") is False

    def test_detect_bank_card(self):
        """测试检测银行卡号"""
        service = SecurityClassifierService()
        # app/test/security_test.py
"""
Tests for Security Classifier Service
Tests the AI-powered security issue classification system
"""
import pytest
from app.services.security_classifier_service import SecurityClassifierService


class TestSecurityClassifier:
    """安全问题分类器测试"""

    def test_classify_sca_issue(self):
        """测试分类SCA(软件组件分析)问题"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            title="Vulnerable npm package detected",
            description="Package lodash version 4.17.15 has known CVE-2020-8203 vulnerability"
        )
        assert result["issue_type"] == "SCA"
        assert result["confidence_score"] > 0.5

    def test_classify_sast_issue(self):
        """测试分类SAST(静态应用安全测试)问题"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            title="SQL Injection vulnerability",
            description="Hardcoded SQL query at line 45 allows SQL injection attack"
        )
        assert result["issue_type"] == "SAST"
        assert result["confidence_score"] > 0.5

    def test_classify_dast_issue(self):
        """测试分类DAST(动态应用安全测试)问题"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            title="Missing security headers",
            description="API endpoint /api/users missing CORS and CSRF protection headers"
        )
        assert result["issue_type"] == "DAST"
        assert result["confidence_score"] > 0.5

    def test_severity_calculation(self):
        """测试严重程度计算"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            title="Critical SQL injection vulnerability",
            description="SQL injection allows unauthorized database access with CVE reference"
        )
        assert result["severity"] in ["critical", "high", "medium", "low", "info"]

    def test_remediation_suggestion(self):
        """测试修复建议生成"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            title="Outdated dependency",
            description="Update npm package to fix CVE-2021-12345"
        )
        assert "remediation_suggestion" in result
        assert result["remediation_suggestion"] is not None

    def test_confidence_score_range(self):
        """测试置信度分数范围"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            title="Security issue",
            description="Some security problem"
        )
        assert 0.0 <= result["confidence_score"] <= 1.0