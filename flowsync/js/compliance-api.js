/**
 * FlowSync Compliance API
 * Regulatory compliance verification and reporting
 */

import {
    ComplianceAPI,
    ComplianceFramework,
    ComplianceReport,
    ComplianceCheck,
} from './flowsync.js';

// =============================================================================
// EXTENDED COMPLIANCE RULES
// =============================================================================

/**
 * Extended compliance rules database
 */
const ExtendedRules = {
    // General Data Protection Regulation (EU)
    [ComplianceFramework.GDPR]: [
        { id: 'gdpr-1', requirement: 'Data minimization', category: 'data', severity: 'high' },
        { id: 'gdpr-2', requirement: 'Right to erasure', category: 'rights', severity: 'high' },
        { id: 'gdpr-3', requirement: 'Consent management', category: 'consent', severity: 'high' },
        { id: 'gdpr-4', requirement: 'Data portability', category: 'rights', severity: 'medium' },
        { id: 'gdpr-5', requirement: 'Privacy by design', category: 'architecture', severity: 'high' },
        { id: 'gdpr-6', requirement: 'Data breach notification', category: 'incident', severity: 'critical' },
        { id: 'gdpr-7', requirement: 'DPO appointment', category: 'governance', severity: 'medium' },
        { id: 'gdpr-8', requirement: 'Records of processing', category: 'documentation', severity: 'medium' },
        { id: 'gdpr-9', requirement: 'International transfers', category: 'data', severity: 'high' },
        { id: 'gdpr-10', requirement: 'Impact assessment', category: 'risk', severity: 'high' },
    ],

    // Health Insurance Portability and Accountability Act (US)
    [ComplianceFramework.HIPAA]: [
        { id: 'hipaa-1', requirement: 'PHI encryption at rest', category: 'encryption', severity: 'critical' },
        { id: 'hipaa-2', requirement: 'PHI encryption in transit', category: 'encryption', severity: 'critical' },
        { id: 'hipaa-3', requirement: 'Access controls', category: 'access', severity: 'critical' },
        { id: 'hipaa-4', requirement: 'Audit logging', category: 'audit', severity: 'high' },
        { id: 'hipaa-5', requirement: 'Minimum necessary', category: 'data', severity: 'high' },
        { id: 'hipaa-6', requirement: 'BAA with vendors', category: 'contracts', severity: 'critical' },
        { id: 'hipaa-7', requirement: 'Workforce training', category: 'training', severity: 'medium' },
        { id: 'hipaa-8', requirement: 'Incident response', category: 'incident', severity: 'high' },
        { id: 'hipaa-9', requirement: 'Risk analysis', category: 'risk', severity: 'high' },
        { id: 'hipaa-10', requirement: 'Contingency plan', category: 'continuity', severity: 'medium' },
    ],

    // EU AI Act
    [ComplianceFramework.EU_AI_ACT]: [
        { id: 'euai-1', requirement: 'Transparency to users', category: 'transparency', severity: 'high' },
        { id: 'euai-2', requirement: 'Human oversight capability', category: 'control', severity: 'critical' },
        { id: 'euai-3', requirement: 'Risk classification', category: 'risk', severity: 'high' },
        { id: 'euai-4', requirement: 'Bias testing', category: 'fairness', severity: 'high' },
        { id: 'euai-5', requirement: 'Data governance', category: 'data', severity: 'high' },
        { id: 'euai-6', requirement: 'Technical documentation', category: 'documentation', severity: 'medium' },
        { id: 'euai-7', requirement: 'Accuracy metrics', category: 'performance', severity: 'high' },
        { id: 'euai-8', requirement: 'Robustness testing', category: 'security', severity: 'high' },
        { id: 'euai-9', requirement: 'Logging capabilities', category: 'audit', severity: 'medium' },
        { id: 'euai-10', requirement: 'Registration (high-risk)', category: 'compliance', severity: 'critical' },
    ],

    // SOC 2
    [ComplianceFramework.SOC2]: [
        { id: 'soc2-1', requirement: 'Security policies', category: 'governance', severity: 'high' },
        { id: 'soc2-2', requirement: 'Access management', category: 'access', severity: 'critical' },
        { id: 'soc2-3', requirement: 'Change management', category: 'operations', severity: 'high' },
        { id: 'soc2-4', requirement: 'Risk assessment', category: 'risk', severity: 'high' },
        { id: 'soc2-5', requirement: 'Incident response', category: 'incident', severity: 'high' },
        { id: 'soc2-6', requirement: 'Vendor management', category: 'contracts', severity: 'medium' },
        { id: 'soc2-7', requirement: 'Data classification', category: 'data', severity: 'medium' },
        { id: 'soc2-8', requirement: 'Encryption standards', category: 'encryption', severity: 'high' },
        { id: 'soc2-9', requirement: 'Availability monitoring', category: 'operations', severity: 'medium' },
        { id: 'soc2-10', requirement: 'Confidentiality controls', category: 'data', severity: 'high' },
    ],

    // PCI DSS
    [ComplianceFramework.PCI_DSS]: [
        { id: 'pci-1', requirement: 'Firewall configuration', category: 'network', severity: 'critical' },
        { id: 'pci-2', requirement: 'No default passwords', category: 'access', severity: 'critical' },
        { id: 'pci-3', requirement: 'Protect stored data', category: 'encryption', severity: 'critical' },
        { id: 'pci-4', requirement: 'Encrypt transmission', category: 'encryption', severity: 'critical' },
        { id: 'pci-5', requirement: 'Anti-malware', category: 'security', severity: 'high' },
        { id: 'pci-6', requirement: 'Secure development', category: 'development', severity: 'high' },
        { id: 'pci-7', requirement: 'Access restriction', category: 'access', severity: 'critical' },
        { id: 'pci-8', requirement: 'Unique IDs', category: 'access', severity: 'high' },
        { id: 'pci-9', requirement: 'Physical security', category: 'physical', severity: 'high' },
        { id: 'pci-10', requirement: 'Network monitoring', category: 'monitoring', severity: 'high' },
        { id: 'pci-11', requirement: 'Security testing', category: 'testing', severity: 'high' },
        { id: 'pci-12', requirement: 'Security policy', category: 'governance', severity: 'high' },
    ],
};

// =============================================================================
// COMPLIANCE CHECKER
// =============================================================================

/**
 * Automated compliance checker
 */
class ComplianceChecker {
    constructor(client) {
        this._client = client;
        this._customRules = {};
    }

    /**
     * Add custom compliance rules
     */
    addRules(frameworkId, rules) {
        this._customRules[frameworkId] = [
            ...(this._customRules[frameworkId] || []),
            ...rules,
        ];
    }

    /**
     * Get all rules for a framework
     */
    getRules(framework) {
        const base = ExtendedRules[framework] || [];
        const custom = this._customRules[framework] || [];
        return [...base, ...custom];
    }

    /**
     * Run automated checks
     */
    async autoCheck(target, options = {}) {
        const {
            frameworks = [ComplianceFramework.GDPR],
            system = {},
            code = null,
            config = null,
        } = options;

        const evidence = {};

        // Auto-detect compliance from system properties
        for (const framework of frameworks) {
            const rules = this.getRules(framework);

            for (const rule of rules) {
                const checkResult = await this._autoCheckRule(rule, {
                    system,
                    code,
                    config,
                });

                evidence[rule.id] = checkResult;
            }
        }

        // Run standard compliance check with evidence
        return await this._client.compliance.check({
            target,
            frameworks,
            evidence,
        });
    }

    async _autoCheckRule(rule, context) {
        // Auto-detection based on rule category
        switch (rule.category) {
            case 'encryption':
                return this._checkEncryption(rule, context);
            case 'access':
                return this._checkAccess(rule, context);
            case 'audit':
                return this._checkAudit(rule, context);
            case 'data':
                return this._checkDataHandling(rule, context);
            default:
                return null; // Requires manual evidence
        }
    }

    _checkEncryption(rule, context) {
        const { system, config } = context;

        // Check for encryption settings
        if (config?.encryption?.enabled) return true;
        if (system?.tls?.enabled) return true;
        if (system?.encryption?.algorithm) return true;

        return null; // Uncertain
    }

    _checkAccess(rule, context) {
        const { system, config } = context;

        if (config?.auth?.enabled) return true;
        if (system?.rbac?.enabled) return true;
        if (config?.accessControl) return true;

        return null;
    }

    _checkAudit(rule, context) {
        const { system, config } = context;

        if (config?.logging?.audit) return true;
        if (system?.audit?.enabled) return true;

        return null;
    }

    _checkDataHandling(rule, context) {
        const { config } = context;

        if (config?.data?.minimization) return true;
        if (config?.data?.retention) return true;

        return null;
    }
}

// =============================================================================
// COMPLIANCE REPORTER
// =============================================================================

/**
 * Generate compliance reports in various formats
 */
class ComplianceReporter {
    constructor() {
        this._templates = {};
    }

    /**
     * Register a report template
     */
    registerTemplate(name, template) {
        this._templates[name] = template;
    }

    /**
     * Generate HTML report
     */
    toHTML(report) {
        const summary = report.summary();

        return `
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Report - ${report.target}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #1a1a2e; color: white; padding: 20px; border-radius: 8px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; }
        .metric.passed { background: #d4edda; }
        .metric.failed { background: #f8d7da; }
        .score { font-size: 48px; font-weight: bold; }
        .checks { margin-top: 30px; }
        .check { padding: 15px; border: 1px solid #ddd; margin: 10px 0; border-radius: 4px; }
        .check.passed { border-left: 4px solid #28a745; }
        .check.failed { border-left: 4px solid #dc3545; }
        .check.warning { border-left: 4px solid #ffc107; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Compliance Report</h1>
        <p>Target: ${report.target}</p>
        <p>Generated: ${report.generatedAt}</p>
    </div>

    <div class="summary">
        <div class="metric ${summary.overallStatus}">
            <div class="score">${summary.score.toFixed(0)}%</div>
            <div>Compliance Score</div>
        </div>
        <div class="metric passed">
            <div class="score">${summary.checksByStatus?.passed || 0}</div>
            <div>Passed</div>
        </div>
        <div class="metric failed">
            <div class="score">${summary.checksByStatus?.failed || 0}</div>
            <div>Failed</div>
        </div>
        <div class="metric">
            <div class="score">${summary.checksByStatus?.warning || 0}</div>
            <div>Warnings</div>
        </div>
    </div>

    <div class="checks">
        <h2>Detailed Checks</h2>
        ${report.checks.map(check => `
            <div class="check ${check.status}">
                <strong>${check.requirement}</strong> (${check.framework})
                <p>Status: ${check.status.toUpperCase()}</p>
                <p>${check.details}</p>
                ${check.remediation ? `<p><em>Remediation: ${check.remediation}</em></p>` : ''}
            </div>
        `).join('')}
    </div>
</body>
</html>`;
    }

    /**
     * Generate JSON report
     */
    toJSON(report) {
        return JSON.stringify({
            id: report.id,
            target: report.target,
            generatedAt: report.generatedAt,
            summary: report.summary(),
            checks: report.checks.map(c => ({
                framework: c.framework,
                requirement: c.requirement,
                status: c.status,
                details: c.details,
                remediation: c.remediation,
            })),
        }, null, 2);
    }

    /**
     * Generate CSV report
     */
    toCSV(report) {
        const headers = ['Framework', 'Requirement', 'Status', 'Details', 'Remediation'];
        const rows = report.checks.map(c => [
            c.framework,
            c.requirement,
            c.status,
            c.details.replace(/,/g, ';'),
            c.remediation?.replace(/,/g, ';') || '',
        ]);

        return [
            headers.join(','),
            ...rows.map(r => r.join(',')),
        ].join('\n');
    }

    /**
     * Generate Markdown report
     */
    toMarkdown(report) {
        const summary = report.summary();

        return `# Compliance Report

## Overview
- **Target:** ${report.target}
- **Generated:** ${report.generatedAt}
- **Score:** ${summary.score.toFixed(0)}%
- **Status:** ${summary.overallStatus}

## Summary
| Status | Count |
|--------|-------|
| Passed | ${summary.checksByStatus?.passed || 0} |
| Failed | ${summary.checksByStatus?.failed || 0} |
| Warning | ${summary.checksByStatus?.warning || 0} |

## Detailed Checks

${report.checks.map(c => `### ${c.requirement}
- **Framework:** ${c.framework}
- **Status:** ${c.status}
- **Details:** ${c.details}
${c.remediation ? `- **Remediation:** ${c.remediation}` : ''}
`).join('\n')}
`;
    }
}

// =============================================================================
// COMPLIANCE MONITOR
// =============================================================================

/**
 * Continuous compliance monitoring
 */
class ComplianceMonitor {
    constructor(client) {
        this._client = client;
        this._checks = [];
        this._alerts = [];
        this._running = false;
        this._interval = null;
    }

    /**
     * Register a check to monitor
     */
    watch(target, frameworks, interval = 3600000) {
        const checkId = `watch_${Date.now()}`;
        this._checks.push({
            id: checkId,
            target,
            frameworks,
            interval,
            lastCheck: null,
            nextCheck: Date.now(),
            status: 'pending',
        });
        return checkId;
    }

    /**
     * Remove a check
     */
    unwatch(checkId) {
        const idx = this._checks.findIndex(c => c.id === checkId);
        if (idx > -1) {
            this._checks.splice(idx, 1);
            return true;
        }
        return false;
    }

    /**
     * Start monitoring
     */
    start() {
        if (this._running) return;
        this._running = true;

        this._interval = setInterval(() => this._runChecks(), 60000);
    }

    /**
     * Stop monitoring
     */
    stop() {
        this._running = false;
        if (this._interval) {
            clearInterval(this._interval);
            this._interval = null;
        }
    }

    async _runChecks() {
        const now = Date.now();

        for (const check of this._checks) {
            if (now >= check.nextCheck) {
                check.status = 'running';

                try {
                    const report = await this._client.compliance.check({
                        target: check.target,
                        frameworks: check.frameworks,
                    });

                    check.lastReport = report;
                    check.status = report.overallStatus;

                    // Generate alerts for failures
                    if (report.score < 70) {
                        this._alert({
                            type: 'compliance_failure',
                            target: check.target,
                            score: report.score,
                            timestamp: new Date(),
                        });
                    }
                } catch (error) {
                    check.status = 'error';
                    this._alert({
                        type: 'check_error',
                        target: check.target,
                        error: error.message,
                        timestamp: new Date(),
                    });
                }

                check.lastCheck = now;
                check.nextCheck = now + check.interval;
            }
        }
    }

    _alert(alert) {
        this._alerts.push(alert);
        // Could trigger webhooks, emails, etc.
    }

    /**
     * Get recent alerts
     */
    getAlerts(count = 10) {
        return this._alerts.slice(-count);
    }

    /**
     * Get monitor status
     */
    status() {
        return {
            running: this._running,
            watchedTargets: this._checks.length,
            recentAlerts: this._alerts.slice(-5),
            checks: this._checks.map(c => ({
                id: c.id,
                target: c.target,
                status: c.status,
                lastCheck: c.lastCheck,
            })),
        };
    }
}

// =============================================================================
// FACTORY FUNCTIONS
// =============================================================================

function createChecker(client) {
    return new ComplianceChecker(client);
}

function createReporter() {
    return new ComplianceReporter();
}

function createMonitor(client) {
    return new ComplianceMonitor(client);
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
    ComplianceChecker,
    ComplianceReporter,
    ComplianceMonitor,
    ExtendedRules,
    createChecker,
    createReporter,
    createMonitor,
    ComplianceAPI,
    ComplianceFramework,
    ComplianceReport,
    ComplianceCheck,
};

export default {
    ComplianceChecker,
    ComplianceReporter,
    ComplianceMonitor,
    ExtendedRules,
    createChecker,
    createReporter,
    createMonitor,
};
