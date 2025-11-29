/**
 * FLOWSYNC SDK - JavaScript
 * The Developer Moat for Web Applications
 *
 * Love - Loyalty - Honor - Everybody Eats
 */

const VERSION = '0.1.0';

// =============================================================================
// CONFIGURATION
// =============================================================================

class FlowSyncConfig {
    constructor(options = {}) {
        this.apiKey = options.apiKey || process.env?.FLOWSYNC_API_KEY || '';
        this.apiSecret = options.apiSecret || process.env?.FLOWSYNC_API_SECRET || '';
        this.endpoint = options.endpoint || 'http://localhost:8080';
        this.network = options.network || 'testnet';
        this.timeout = options.timeout || 30000;
        this.retryCount = options.retryCount || 3;
        this.debug = options.debug || false;
    }
}

// =============================================================================
// MAIN CLIENT
// =============================================================================

class FlowSync {
    constructor(options = {}) {
        if (typeof options === 'string') {
            options = { apiKey: options };
        }

        this.config = new FlowSyncConfig(options);
        this._sessionId = this._generateSessionId();
        this._connected = false;

        // Initialize sub-modules
        this._agents = new AgentAPI(this);
        this._workflows = new WorkflowAPI(this);
        this._compliance = new ComplianceAPI(this);
        this._economy = new EconomyAPI(this);
    }

    _generateSessionId() {
        const data = `${Date.now()}-${this.config.apiKey}`;
        return this._hash(data).slice(0, 16);
    }

    _hash(str) {
        // Simple hash for browser compatibility
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16).padStart(16, '0');
    }

    get agents() { return this._agents; }
    get workflows() { return this._workflows; }
    get compliance() { return this._compliance; }
    get economy() { return this._economy; }

    async connect() {
        if (this.config.debug) {
            console.log(`FlowSync SDK v${VERSION} connecting...`);
        }

        if (!this.config.apiKey) {
            throw new Error('API key required');
        }

        this._connected = true;
        return true;
    }

    async disconnect() {
        this._connected = false;
    }

    signRequest(data) {
        // HMAC signature for API authentication
        const payload = JSON.stringify(data, Object.keys(data).sort());
        return this._hash(this.config.apiSecret + payload);
    }

    async request(method, path, data = null) {
        const url = `${this.config.endpoint}${path}`;
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.config.apiKey,
            'X-Session-ID': this._sessionId,
        };

        if (data) {
            headers['X-Signature'] = this.signRequest(data);
        }

        const options = {
            method,
            headers,
            timeout: this.config.timeout,
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        // Retry logic
        for (let attempt = 0; attempt < this.config.retryCount; attempt++) {
            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                if (attempt === this.config.retryCount - 1) {
                    throw error;
                }
                await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
            }
        }
    }
}

// =============================================================================
// AGENT API
// =============================================================================

const AgentCapability = {
    NLP: 'nlp',
    CODE_GEN: 'code-gen',
    DATA_ANALYSIS: 'data-analysis',
    WEB_SEARCH: 'web-search',
    FILE_OPS: 'file-ops',
    API_CALLS: 'api-calls',
    REASONING: 'reasoning',
    MEMORY: 'memory',
    VISION: 'vision',
    AUDIO: 'audio',
};

class Agent {
    constructor(data, client) {
        this.id = data.id;
        this.name = data.name;
        this.capabilities = data.capabilities || [];
        this.status = data.status || 'idle';
        this.memoryId = data.memoryId;
        this.createdAt = data.createdAt || new Date();
        this.metadata = data.metadata || {};
        this._client = client;
        this._taskCount = 0;
    }

    async execute(task, context = {}) {
        this._taskCount++;
        const start = Date.now();

        const result = {
            agentId: this.id,
            task,
            context,
            result: null,
            success: false,
            executionTime: 0,
        };

        try {
            if (this.capabilities.includes(AgentCapability.CODE_GEN)) {
                result.result = `// Generated code for: ${task}\n`;
            } else if (this.capabilities.includes(AgentCapability.DATA_ANALYSIS)) {
                result.result = { analysis: task, insights: [] };
            } else {
                result.result = `Processed: ${task}`;
            }
            result.success = true;
        } catch (error) {
            result.error = error.message;
        }

        result.executionTime = (Date.now() - start) / 1000;
        return result;
    }

    async remember(key, value) {
        if (this.memoryId && this._client) {
            // Connect to memory system
        }
    }

    async recall(key) {
        if (this.memoryId && this._client) {
            // Connect to memory system
        }
        return null;
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            capabilities: this.capabilities,
            status: this.status,
            memoryId: this.memoryId,
            createdAt: this.createdAt,
            metadata: this.metadata,
        };
    }
}

class AgentAPI {
    constructor(client) {
        this._client = client;
        this._agents = new Map();
    }

    async create(options = {}) {
        const {
            name,
            capabilities = ['nlp'],
            memory = true,
            metadata = {},
        } = options;

        const agentId = this._client._hash(`${name}-${Date.now()}`).slice(0, 12);
        const memoryId = memory ? `mem_${agentId}` : null;

        const agent = new Agent({
            id: agentId,
            name,
            capabilities,
            memoryId,
            metadata,
        }, this._client);

        this._agents.set(agentId, agent);
        return agent;
    }

    async get(agentId) {
        return this._agents.get(agentId) || null;
    }

    async list() {
        return Array.from(this._agents.values());
    }

    async delete(agentId) {
        return this._agents.delete(agentId);
    }

    async clone(agentId, newName) {
        const original = this._agents.get(agentId);
        if (!original) return null;

        return await this.create({
            name: newName,
            capabilities: [...original.capabilities],
            memory: !!original.memoryId,
            metadata: { ...original.metadata },
        });
    }
}

// =============================================================================
// WORKFLOW API
// =============================================================================

const StepType = {
    ACTION: 'action',
    CONDITION: 'condition',
    LOOP: 'loop',
    PARALLEL: 'parallel',
    AGENT_CALL: 'agent_call',
    HUMAN_IN_LOOP: 'human_in_loop',
    CHECKPOINT: 'checkpoint',
};

class WorkflowRun {
    constructor(data) {
        this.id = data.id;
        this.workflowId = data.workflowId;
        this.status = data.status;
        this.currentStep = data.currentStep || 0;
        this.inputs = data.inputs || {};
        this.outputs = data.outputs || {};
        this.startedAt = data.startedAt || new Date();
        this.completedAt = data.completedAt;
        this.error = data.error;
        this.stepResults = data.stepResults || [];
    }
}

class Workflow {
    constructor(data, client) {
        this.id = data.id;
        this.name = data.name;
        this.description = data.description || '';
        this.steps = data.steps || [];
        this.version = data.version || '1.0.0';
        this.createdAt = data.createdAt || new Date();
        this.metadata = data.metadata || {};
        this._client = client;
        this._runs = [];
    }

    async run(inputs = {}) {
        const runId = this._client._hash(`${this.id}-${Date.now()}`).slice(0, 12);

        const run = new WorkflowRun({
            id: runId,
            workflowId: this.id,
            status: 'running',
            inputs,
            startedAt: new Date(),
        });

        this._runs.push(run);

        const context = { ...inputs };

        try {
            for (let i = 0; i < this.steps.length; i++) {
                run.currentStep = i;
                const step = this.steps[i];

                const stepResult = await this._executeStep(step, context);
                run.stepResults.push(stepResult);

                if (step.output) {
                    context[step.output] = stepResult.result;
                }

                if (step.type === StepType.CONDITION && !stepResult.passed) {
                    break;
                }
            }

            run.status = 'completed';
            run.outputs = context;
        } catch (error) {
            run.status = 'failed';
            run.error = error.message;
        }

        run.completedAt = new Date();
        return run;
    }

    async _executeStep(step, context) {
        const result = {
            step: step.name,
            type: step.type || StepType.ACTION,
            success: false,
            result: null,
        };

        let inputValue = step.input;
        if (inputValue && inputValue.startsWith('$')) {
            const varName = inputValue.slice(1);
            inputValue = context[varName] || inputValue;
        }

        switch (step.type || StepType.ACTION) {
            case StepType.ACTION:
                result.result = `Executed ${step.action} with ${inputValue}`;
                result.success = true;
                break;

            case StepType.AGENT_CALL:
                if (this._client && step.agentId) {
                    const agent = await this._client.agents.get(step.agentId);
                    if (agent) {
                        const agentResult = await agent.execute(inputValue, context);
                        result.result = agentResult.result;
                        result.success = agentResult.success;
                    }
                }
                break;

            case StepType.CONDITION:
                try {
                    // Safe condition evaluation
                    result.passed = Boolean(context[step.condition]);
                    result.success = true;
                } catch {
                    result.passed = false;
                }
                break;

            case StepType.CHECKPOINT:
                result.checkpointData = { ...context };
                result.success = true;
                break;

            default:
                result.success = true;
        }

        return result;
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            steps: this.steps,
            version: this.version,
            createdAt: this.createdAt,
        };
    }
}

class WorkflowAPI {
    constructor(client) {
        this._client = client;
        this._workflows = new Map();
    }

    async create(options = {}) {
        const {
            name,
            steps = [],
            description = '',
            metadata = {},
        } = options;

        const workflowId = this._client._hash(`${name}-${Date.now()}`).slice(0, 12);

        const workflow = new Workflow({
            id: workflowId,
            name,
            description,
            steps,
            metadata,
        }, this._client);

        this._workflows.set(workflowId, workflow);
        return workflow;
    }

    async get(workflowId) {
        return this._workflows.get(workflowId) || null;
    }

    async list() {
        return Array.from(this._workflows.values());
    }

    async delete(workflowId) {
        return this._workflows.delete(workflowId);
    }
}

// =============================================================================
// COMPLIANCE API
// =============================================================================

const ComplianceFramework = {
    GDPR: 'gdpr',
    HIPAA: 'hipaa',
    SOC2: 'soc2',
    PCI_DSS: 'pci-dss',
    EU_AI_ACT: 'eu-ai-act',
    CCPA: 'ccpa',
    ISO_27001: 'iso-27001',
};

class ComplianceCheck {
    constructor(data) {
        this.framework = data.framework;
        this.requirement = data.requirement;
        this.status = data.status;
        this.details = data.details;
        this.remediation = data.remediation || '';
        this.evidence = data.evidence || {};
    }
}

class ComplianceReport {
    constructor(data) {
        this.id = data.id;
        this.target = data.target;
        this.frameworks = data.frameworks;
        this.checks = data.checks;
        this.overallStatus = data.overallStatus;
        this.score = data.score;
        this.generatedAt = data.generatedAt || new Date();
    }

    summary() {
        const byStatus = {};
        for (const check of this.checks) {
            byStatus[check.status] = (byStatus[check.status] || 0) + 1;
        }

        return {
            target: this.target,
            frameworks: this.frameworks,
            overallStatus: this.overallStatus,
            score: this.score,
            checksByStatus: byStatus,
            totalChecks: this.checks.length,
        };
    }
}

class ComplianceAPI {
    static RULES = {
        [ComplianceFramework.GDPR]: [
            { id: 'gdpr-1', requirement: 'Data minimization', check: 'Collect only necessary data' },
            { id: 'gdpr-2', requirement: 'Right to erasure', check: 'Provide data deletion mechanism' },
            { id: 'gdpr-3', requirement: 'Consent management', check: 'Obtain explicit consent' },
            { id: 'gdpr-4', requirement: 'Data portability', check: 'Allow data export' },
        ],
        [ComplianceFramework.HIPAA]: [
            { id: 'hipaa-1', requirement: 'PHI encryption', check: 'Encrypt all PHI' },
            { id: 'hipaa-2', requirement: 'Access controls', check: 'Implement RBAC for PHI' },
            { id: 'hipaa-3', requirement: 'Audit logging', check: 'Log all PHI access' },
        ],
        [ComplianceFramework.EU_AI_ACT]: [
            { id: 'euai-1', requirement: 'Transparency', check: 'Disclose AI usage' },
            { id: 'euai-2', requirement: 'Human oversight', check: 'Human-in-loop controls' },
            { id: 'euai-3', requirement: 'Risk assessment', check: 'Document AI risk level' },
            { id: 'euai-4', requirement: 'Bias mitigation', check: 'Test for bias' },
        ],
    };

    constructor(client) {
        this._client = client;
        this._reports = [];
    }

    async check(options = {}) {
        const {
            target,
            frameworks = [ComplianceFramework.GDPR],
            evidence = {},
        } = options;

        const checks = [];

        for (const framework of frameworks) {
            const rules = ComplianceAPI.RULES[framework] || [];
            for (const rule of rules) {
                const checkResult = this._runCheck(rule, evidence);
                checks.push(new ComplianceCheck({
                    framework,
                    requirement: rule.requirement,
                    status: checkResult.status,
                    details: checkResult.details,
                    remediation: checkResult.remediation,
                    evidence: checkResult.evidence,
                }));
            }
        }

        const passed = checks.filter(c => c.status === 'passed').length;
        const total = checks.length;
        const score = (passed / Math.max(1, total)) * 100;

        let overallStatus;
        if (score === 100) overallStatus = 'compliant';
        else if (score >= 70) overallStatus = 'partial';
        else overallStatus = 'non_compliant';

        const reportId = this._client._hash(`${target}-${Date.now()}`).slice(0, 12);

        const report = new ComplianceReport({
            id: reportId,
            target,
            frameworks,
            checks,
            overallStatus,
            score,
        });

        this._reports.push(report);
        return report;
    }

    _runCheck(rule, evidence) {
        if (rule.id in evidence) {
            return {
                status: evidence[rule.id] ? 'passed' : 'failed',
                details: `Evidence provided: ${evidence[rule.id]}`,
                evidence: { [rule.id]: evidence[rule.id] },
            };
        }

        return {
            status: 'warning',
            details: `No evidence provided for: ${rule.check}`,
            remediation: `Provide evidence for ${rule.requirement}`,
        };
    }

    async getReport(reportId) {
        return this._reports.find(r => r.id === reportId) || null;
    }

    async listReports() {
        return this._reports;
    }

    getRequirements(framework) {
        return ComplianceAPI.RULES[framework] || [];
    }
}

// =============================================================================
// ECONOMY API
// =============================================================================

const TokenType = {
    ORB: 'orb',
    COMPUTE: 'compute',
    STORAGE: 'storage',
    API_CALL: 'api_call',
};

class Wallet {
    constructor(data) {
        this.id = data.id;
        this.owner = data.owner;
        this.balances = data.balances || {
            [TokenType.ORB]: 0,
            [TokenType.COMPUTE]: 0,
            [TokenType.STORAGE]: 0,
            [TokenType.API_CALL]: 0,
        };
        this.createdAt = data.createdAt || new Date();
    }

    balance(token) {
        return this.balances[token] || 0;
    }

    toJSON() {
        return {
            id: this.id,
            owner: this.owner,
            balances: this.balances,
            createdAt: this.createdAt,
        };
    }
}

class Transaction {
    constructor(data) {
        this.id = data.id;
        this.fromWallet = data.fromWallet;
        this.toWallet = data.toWallet;
        this.token = data.token;
        this.amount = data.amount;
        this.fee = data.fee;
        this.status = data.status;
        this.timestamp = data.timestamp || new Date();
        this.metadata = data.metadata || {};
    }
}

class Stake {
    constructor(data) {
        this.id = data.id;
        this.walletId = data.walletId;
        this.amount = data.amount;
        this.nodeType = data.nodeType;
        this.lockedUntil = data.lockedUntil;
        this.rewardsEarned = data.rewardsEarned || 0;
        this.createdAt = data.createdAt || new Date();
    }
}

class EconomyAPI {
    static FEES = {
        transfer: 0.001,
        stake: 0,
        unstake: 0.005,
        apiCall: 0.0001,
    };

    static STAKING_REWARDS = {
        compute: 0.12,
        storage: 0.08,
        validator: 0.15,
    };

    constructor(client) {
        this._client = client;
        this._wallets = new Map();
        this._transactions = [];
        this._stakes = [];
    }

    async createWallet(owner) {
        const walletId = this._client._hash(`${owner}-${Date.now()}`).slice(0, 12);

        const wallet = new Wallet({
            id: walletId,
            owner,
        });

        this._wallets.set(walletId, wallet);
        return wallet;
    }

    async getWallet(walletId) {
        return this._wallets.get(walletId) || null;
    }

    async transfer(fromWallet, toWallet, token, amount) {
        const sender = this._wallets.get(fromWallet);
        const receiver = this._wallets.get(toWallet);

        if (!sender || !receiver) {
            throw new Error('Invalid wallet ID');
        }

        const fee = amount * EconomyAPI.FEES.transfer;
        const total = amount + fee;

        if (sender.balance(token) < total) {
            throw new Error('Insufficient balance');
        }

        sender.balances[token] -= total;
        receiver.balances[token] = (receiver.balances[token] || 0) + amount;

        const txId = this._client._hash(`${fromWallet}-${toWallet}-${Date.now()}`).slice(0, 12);

        const tx = new Transaction({
            id: txId,
            fromWallet,
            toWallet,
            token,
            amount,
            fee,
            status: 'confirmed',
        });

        this._transactions.push(tx);
        return tx;
    }

    async stake(walletId, amount, nodeType, durationDays = 30) {
        const wallet = this._wallets.get(walletId);
        if (!wallet) {
            throw new Error('Invalid wallet ID');
        }

        if (wallet.balance(TokenType.ORB) < amount) {
            throw new Error('Insufficient balance');
        }

        wallet.balances[TokenType.ORB] -= amount;

        const stakeId = this._client._hash(`${walletId}-stake-${Date.now()}`).slice(0, 12);

        const lockedUntil = new Date();
        lockedUntil.setDate(lockedUntil.getDate() + durationDays);

        const stake = new Stake({
            id: stakeId,
            walletId,
            amount,
            nodeType,
            lockedUntil,
        });

        this._stakes.push(stake);
        return stake;
    }

    async unstake(stakeId) {
        const stakeIndex = this._stakes.findIndex(s => s.id === stakeId);
        if (stakeIndex === -1) {
            throw new Error('Stake not found');
        }

        const stake = this._stakes[stakeIndex];

        if (new Date() < new Date(stake.lockedUntil)) {
            throw new Error('Stake still locked');
        }

        const wallet = this._wallets.get(stake.walletId);
        if (wallet) {
            const total = stake.amount + stake.rewardsEarned;
            const fee = total * EconomyAPI.FEES.unstake;
            wallet.balances[TokenType.ORB] += (total - fee);
        }

        this._stakes.splice(stakeIndex, 1);
        return total - fee;
    }

    async calculateRewards(stakeId) {
        const stake = this._stakes.find(s => s.id === stakeId);
        if (!stake) return 0;

        const daysStaked = Math.floor(
            (Date.now() - new Date(stake.createdAt).getTime()) / (1000 * 60 * 60 * 24)
        );
        const apy = EconomyAPI.STAKING_REWARDS[stake.nodeType] || 0.05;
        return stake.amount * (apy / 365) * daysStaked;
    }

    async getPrice(token) {
        const prices = {
            [TokenType.ORB]: 1.50,
            [TokenType.COMPUTE]: 0.10,
            [TokenType.STORAGE]: 0.05,
            [TokenType.API_CALL]: 0.001,
        };
        return prices[token] || 0;
    }

    async purchaseCredits(walletId, creditType, amount) {
        const wallet = this._wallets.get(walletId);
        if (!wallet) {
            throw new Error('Invalid wallet ID');
        }

        const orbPrice = await this.getPrice(TokenType.ORB);
        const creditPrice = await this.getPrice(creditType);
        const orbCost = (amount * creditPrice) / orbPrice;

        if (wallet.balance(TokenType.ORB) < orbCost) {
            throw new Error('Insufficient ORB balance');
        }

        wallet.balances[TokenType.ORB] -= orbCost;
        wallet.balances[creditType] = (wallet.balances[creditType] || 0) + amount;

        const txId = this._client._hash(`purchase-${walletId}-${Date.now()}`).slice(0, 12);

        const tx = new Transaction({
            id: txId,
            fromWallet: walletId,
            toWallet: 'treasury',
            token: TokenType.ORB,
            amount: orbCost,
            fee: 0,
            status: 'confirmed',
            metadata: { creditType, creditAmount: amount },
        });

        this._transactions.push(tx);
        return tx;
    }

    getStats() {
        const totalStaked = this._stakes.reduce((sum, s) => sum + s.amount, 0);

        return {
            totalWallets: this._wallets.size,
            totalStaked,
            totalTransactions: this._transactions.length,
            activeStakes: this._stakes.length,
        };
    }
}

// =============================================================================
// EXPORTS
// =============================================================================

// For Node.js/CommonJS
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        FlowSync,
        FlowSyncConfig,
        Agent,
        AgentAPI,
        AgentCapability,
        Workflow,
        WorkflowAPI,
        WorkflowRun,
        StepType,
        ComplianceAPI,
        ComplianceFramework,
        ComplianceReport,
        ComplianceCheck,
        EconomyAPI,
        Wallet,
        Transaction,
        Stake,
        TokenType,
        VERSION,
    };
}

// For ES Modules
export {
    FlowSync,
    FlowSyncConfig,
    Agent,
    AgentAPI,
    AgentCapability,
    Workflow,
    WorkflowAPI,
    WorkflowRun,
    StepType,
    ComplianceAPI,
    ComplianceFramework,
    ComplianceReport,
    ComplianceCheck,
    EconomyAPI,
    Wallet,
    Transaction,
    Stake,
    TokenType,
    VERSION,
};

export default FlowSync;
