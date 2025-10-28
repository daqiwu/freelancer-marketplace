"""
AI-powered Security Issue Classifier Service
Classifies security testing issues (SCA, SAST, DAST) and provides remediation suggestions
"""

import re
from typing import Dict, List, Tuple
from decimal import Decimal
import json


class SecurityClassifierService:
    """
    AI-based security issue classifier using rule-based ML patterns
    and keyword analysis for SCA, SAST, and DAST classification
    """
    
    # Classification patterns for each security testing type
    SCA_PATTERNS = {
        'keywords': [
            'dependency', 'package', 'library', 'npm', 'pip', 'maven', 'gradle',
            'third-party', 'outdated', 'vulnerable package', 'CVE', 'version',
            'requirements.txt', 'package.json', 'pom.xml', 'composer', 'cargo'
        ],
        'indicators': [
            r'CVE-\d{4}-\d+',
            r'version\s+[\d\.]+',
            r'dependency.*vulnerability',
            r'package.*outdated',
            r'npm audit|pip check|safety check',
        ]
    }
    
    SAST_PATTERNS = {
        'keywords': [
            'code', 'source code', 'static analysis', 'hardcoded', 'sql injection',
            'xss', 'cross-site scripting', 'buffer overflow', 'integer overflow',
            'command injection', 'path traversal', 'insecure deserialization',
            'weak cryptography', 'insecure random', 'race condition', 'code smell',
            'security hotspot', 'taint analysis', 'data flow'
        ],
        'indicators': [
            r'line\s+\d+',
            r'function.*vulnerable',
            r'insecure.*code',
            r'hardcoded.*(password|secret|key|token)',
            r'SQL.*injection',
            r'XSS|cross-site',
        ]
    }
    
    DAST_PATTERNS = {
        'keywords': [
            'runtime', 'dynamic', 'http', 'endpoint', 'api', 'request', 'response',
            'authentication', 'authorization', 'session', 'cookie', 'header',
            'ssl', 'tls', 'certificate', 'cors', 'csrf', 'clickjacking',
            'security header', 'penetration test', 'fuzzing', 'web application'
        ],
        'indicators': [
            r'HTTP/\d\.\d',
            r'GET|POST|PUT|DELETE|PATCH',
            r'endpoint.*vulnerable',
            r'/api/.*',
            r'status code \d{3}',
            r'header.*missing',
        ]
    }
    
    # Severity scoring patterns
    SEVERITY_KEYWORDS = {
        'CRITICAL': ['critical', 'remote code execution', 'rce', 'authentication bypass', 'privilege escalation'],
        'HIGH': ['high', 'sql injection', 'xss', 'command injection', 'xxe', 'ssrf'],
        'MEDIUM': ['medium', 'information disclosure', 'weak', 'insecure', 'outdated'],
        'LOW': ['low', 'minor', 'informational', 'best practice'],
        'INFO': ['info', 'informational', 'notice', 'suggestion']
    }
    
    # Remediation templates
    REMEDIATION_TEMPLATES = {
        'SCA': {
            'CRITICAL': "URGENT: Update {component} to version {recommended_version} or higher immediately. This dependency has a critical vulnerability (CVE rated 9.0+). Consider implementing a security patch or finding an alternative package.",
            'HIGH': "Update {component} to the latest stable version. Review breaking changes and test thoroughly before deploying. Consider using dependency scanning tools in CI/CD.",
            'MEDIUM': "Schedule an update for {component}. Review the changelog and plan migration. Add this to the next sprint.",
            'LOW': "Consider updating {component} when convenient. Monitor for security advisories.",
        },
        'SAST': {
            'CRITICAL': "Immediate code fix required for {component}. This vulnerability allows {vulnerability_type}. Recommended fix: {fix_suggestion}. Code review and security testing required before deployment.",
            'HIGH': "Fix the security issue in {component} at line {line_number}. Use parameterized queries, input validation, or secure coding patterns. Deploy with thorough testing.",
            'MEDIUM': "Refactor {component} to follow secure coding practices. Consider using security linters and code review.",
            'LOW': "Code improvement suggested for {component}. Follow security best practices and coding standards.",
        },
        'DAST': {
            'CRITICAL': "Critical runtime vulnerability detected in {component}. Immediately review authentication/authorization logic. Apply security patches and restrict access.",
            'HIGH': "Configure proper security headers for {component}. Implement {security_control} and validate all inputs at runtime.",
            'MEDIUM': "Improve security configuration for {component}. Add missing security headers, enable HTTPS, or update SSL/TLS settings.",
            'LOW': "Enhance security posture of {component}. Review security headers and implement defense-in-depth.",
        }
    }
    
    def classify_issue(self, title: str, description: str, affected_component: str = "") -> Dict:
        """
        Classify a security issue using AI-based pattern matching
        
        Args:
            title: Issue title
            description: Issue description
            affected_component: Component affected by the issue
            
        Returns:
            Dictionary with classification results
        """
        combined_text = f"{title} {description} {affected_component}".lower()
        
        # Calculate scores for each type
        sca_score = self._calculate_type_score(combined_text, self.SCA_PATTERNS)
        sast_score = self._calculate_type_score(combined_text, self.SAST_PATTERNS)
        dast_score = self._calculate_type_score(combined_text, self.DAST_PATTERNS)
        
        # Determine issue type and confidence
        issue_type, confidence = self._determine_type(sca_score, sast_score, dast_score)
        
        # Determine severity
        severity = self._determine_severity(combined_text)
        
        # Extract vulnerability details
        vuln_id = self._extract_vulnerability_id(combined_text)
        
        # Generate tags
        tags = self._generate_tags(combined_text, issue_type)
        
        # Generate remediation suggestion
        remediation = self._generate_remediation(
            issue_type, severity, title, affected_component
        )
        
        # Calculate priority (1-10)
        priority = self._calculate_priority(severity, confidence)
        
        # Estimate effort
        effort = self._estimate_effort(severity, issue_type)
        
        return {
            'issue_type': issue_type,
            'severity': severity,
            'confidence_score': Decimal(str(round(confidence, 2))),
            'vulnerability_id': vuln_id,
            'tags': json.dumps(tags),
            'remediation_suggestion': remediation,
            'remediation_priority': priority,
            'estimated_effort': effort,
            'detection_method': 'AI Pattern Matching'
        }
    
    def _calculate_type_score(self, text: str, patterns: Dict) -> float:
        """Calculate matching score for a specific issue type"""
        score = 0.0
        
        # Keyword matching
        keyword_matches = sum(1 for kw in patterns['keywords'] if kw in text)
        score += keyword_matches * 2
        
        # Pattern matching (regex)
        pattern_matches = sum(1 for pattern in patterns['indicators'] if re.search(pattern, text, re.IGNORECASE))
        score += pattern_matches * 3
        
        return score
    
    def _determine_type(self, sca_score: float, sast_score: float, dast_score: float) -> Tuple[str, float]:
        """Determine issue type based on scores"""
        max_score = max(sca_score, sast_score, dast_score)
        
        if max_score == 0:
            return 'UNKNOWN', 0.0
        
        # Calculate confidence (0-100)
        total_score = sca_score + sast_score + dast_score
        confidence = (max_score / total_score * 100) if total_score > 0 else 0
        
        # Minimum confidence threshold
        if confidence < 30:
            return 'UNKNOWN', confidence
        
        if max_score == sca_score:
            return 'SCA', confidence
        elif max_score == sast_score:
            return 'SAST', confidence
        else:
            return 'DAST', confidence
    
    def _determine_severity(self, text: str) -> str:
        """Determine severity based on keywords"""
        for severity, keywords in self.SEVERITY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return severity
        return 'MEDIUM'  # Default
    
    def _extract_vulnerability_id(self, text: str) -> str:
        """Extract CVE or vulnerability ID"""
        cve_match = re.search(r'CVE-\d{4}-\d+', text, re.IGNORECASE)
        if cve_match:
            return cve_match.group(0).upper()
        
        # Look for other common vulnerability IDs
        vuln_match = re.search(r'(GHSA|SNYK|OSV)-[\w-]+', text, re.IGNORECASE)
        if vuln_match:
            return vuln_match.group(0).upper()
        
        return None
    
    def _generate_tags(self, text: str, issue_type: str) -> List[str]:
        """Generate relevant tags for the issue"""
        tags = [issue_type]
        
        # Common security tags
        tag_keywords = {
            'injection': 'injection',
            'xss': 'xss',
            'authentication': 'auth',
            'authorization': 'authz',
            'cryptography': 'crypto',
            'dependency': 'dependencies',
            'configuration': 'config',
            'api': 'api',
            'web': 'web'
        }
        
        for keyword, tag in tag_keywords.items():
            if keyword in text:
                tags.append(tag)
        
        return list(set(tags))  # Remove duplicates
    
    def _generate_remediation(self, issue_type: str, severity: str, 
                             title: str, component: str) -> str:
        """Generate AI-based remediation suggestion"""
        template = self.REMEDIATION_TEMPLATES.get(issue_type, {}).get(severity, 
            "Review and fix the security issue in {component}. Follow security best practices.")
        
        # Extract specific details for more targeted suggestions
        vulnerability_type = "security vulnerability"
        if 'sql injection' in title.lower():
            vulnerability_type = "SQL injection attacks"
        elif 'xss' in title.lower() or 'cross-site' in title.lower():
            vulnerability_type = "cross-site scripting attacks"
        elif 'rce' in title.lower() or 'remote code' in title.lower():
            vulnerability_type = "remote code execution"
        
        # Format the template
        remediation = template.format(
            component=component or "the affected component",
            vulnerability_type=vulnerability_type,
            recommended_version="latest stable",
            line_number="[detected]",
            fix_suggestion="implement input validation and use secure APIs",
            security_control="proper authentication and authorization"
        )
        
        return remediation
    
    def _calculate_priority(self, severity: str, confidence: float) -> int:
        """Calculate remediation priority (1-10)"""
        severity_scores = {
            'CRITICAL': 10,
            'HIGH': 8,
            'MEDIUM': 5,
            'LOW': 3,
            'INFO': 1
        }
        
        base_priority = severity_scores.get(severity, 5)
        
        # Adjust by confidence
        if confidence < 50:
            base_priority = max(1, base_priority - 2)
        elif confidence > 80:
            base_priority = min(10, base_priority + 1)
        
        return base_priority
    
    def _estimate_effort(self, severity: str, issue_type: str) -> str:
        """Estimate fix effort"""
        if severity in ['CRITICAL', 'HIGH']:
            return 'HIGH'
        elif severity == 'MEDIUM':
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def batch_classify(self, issues: List[Dict]) -> List[Dict]:
        """
        Classify multiple issues in batch
        
        Args:
            issues: List of issue dictionaries with 'title', 'description', 'component'
            
        Returns:
            List of classification results
        """
        results = []
        for issue in issues:
            result = self.classify_issue(
                issue.get('title', ''),
                issue.get('description', ''),
                issue.get('component', '')
            )
            results.append({**issue, **result})
        
        return results
    
    def get_statistics(self, classified_issues: List[Dict]) -> Dict:
        """
        Get statistics from classified issues
        
        Args:
            classified_issues: List of classified issue dictionaries
            
        Returns:
            Statistics dictionary
        """
        total = len(classified_issues)
        if total == 0:
            return {}
        
        type_counts = {'SCA': 0, 'SAST': 0, 'DAST': 0, 'UNKNOWN': 0}
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        
        for issue in classified_issues:
            issue_type = issue.get('issue_type', 'UNKNOWN')
            severity = issue.get('severity', 'MEDIUM')
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total': total,
            'by_type': type_counts,
            'by_severity': severity_counts,
            'avg_confidence': sum(float(i.get('confidence_score', 0)) for i in classified_issues) / total
        }

