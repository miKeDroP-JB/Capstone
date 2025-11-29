/**
 * FlowSync Agent API
 * Create and manage AI agents
 */

import { AgentCapability, Agent, AgentAPI } from './flowsync.js';

// =============================================================================
// EXTENDED AGENT CAPABILITIES
// =============================================================================

/**
 * Create a specialized agent builder
 */
class AgentBuilder {
    constructor(client) {
        this._client = client;
        this._config = {
            name: 'unnamed-agent',
            capabilities: [],
            memory: true,
            metadata: {},
            hooks: {},
        };
    }

    name(name) {
        this._config.name = name;
        return this;
    }

    withNLP() {
        this._config.capabilities.push(AgentCapability.NLP);
        return this;
    }

    withCodeGen() {
        this._config.capabilities.push(AgentCapability.CODE_GEN);
        return this;
    }

    withDataAnalysis() {
        this._config.capabilities.push(AgentCapability.DATA_ANALYSIS);
        return this;
    }

    withWebSearch() {
        this._config.capabilities.push(AgentCapability.WEB_SEARCH);
        return this;
    }

    withReasoning() {
        this._config.capabilities.push(AgentCapability.REASONING);
        return this;
    }

    withMemory() {
        this._config.memory = true;
        return this;
    }

    withoutMemory() {
        this._config.memory = false;
        return this;
    }

    withCapability(capability) {
        this._config.capabilities.push(capability);
        return this;
    }

    withMetadata(metadata) {
        this._config.metadata = { ...this._config.metadata, ...metadata };
        return this;
    }

    onBeforeTask(hook) {
        this._config.hooks.beforeTask = hook;
        return this;
    }

    onAfterTask(hook) {
        this._config.hooks.afterTask = hook;
        return this;
    }

    onError(hook) {
        this._config.hooks.onError = hook;
        return this;
    }

    async build() {
        const agent = await this._client.agents.create({
            name: this._config.name,
            capabilities: this._config.capabilities,
            memory: this._config.memory,
            metadata: this._config.metadata,
        });

        // Attach hooks
        if (this._config.hooks.beforeTask) {
            agent._hooks = agent._hooks || {};
            agent._hooks.beforeTask = this._config.hooks.beforeTask;
        }
        if (this._config.hooks.afterTask) {
            agent._hooks = agent._hooks || {};
            agent._hooks.afterTask = this._config.hooks.afterTask;
        }
        if (this._config.hooks.onError) {
            agent._hooks = agent._hooks || {};
            agent._hooks.onError = this._config.hooks.onError;
        }

        return agent;
    }
}

/**
 * Agent Pool for managing multiple agents
 */
class AgentPool {
    constructor(client) {
        this._client = client;
        this._agents = new Map();
        this._taskQueue = [];
        this._processing = false;
    }

    async add(agentOrBuilder) {
        let agent = agentOrBuilder;
        if (agentOrBuilder instanceof AgentBuilder) {
            agent = await agentOrBuilder.build();
        }
        this._agents.set(agent.id, agent);
        return agent;
    }

    async remove(agentId) {
        return this._agents.delete(agentId);
    }

    get(agentId) {
        return this._agents.get(agentId);
    }

    all() {
        return Array.from(this._agents.values());
    }

    idle() {
        return this.all().filter(a => a.status === 'idle');
    }

    busy() {
        return this.all().filter(a => a.status === 'busy');
    }

    async dispatch(task, context = {}) {
        // Find best available agent for task
        const idleAgents = this.idle();
        if (idleAgents.length === 0) {
            // Queue task
            return new Promise((resolve, reject) => {
                this._taskQueue.push({ task, context, resolve, reject });
            });
        }

        // Pick best agent based on capabilities
        const agent = this._selectBestAgent(idleAgents, task);
        agent.status = 'busy';

        try {
            const result = await agent.execute(task, context);
            agent.status = 'idle';

            // Process queue
            this._processQueue();

            return result;
        } catch (error) {
            agent.status = 'idle';
            throw error;
        }
    }

    _selectBestAgent(agents, task) {
        // Simple selection - could be more sophisticated
        const taskLower = task.toLowerCase();

        if (taskLower.includes('code') || taskLower.includes('program')) {
            const codeAgent = agents.find(a =>
                a.capabilities.includes(AgentCapability.CODE_GEN)
            );
            if (codeAgent) return codeAgent;
        }

        if (taskLower.includes('analyze') || taskLower.includes('data')) {
            const analysisAgent = agents.find(a =>
                a.capabilities.includes(AgentCapability.DATA_ANALYSIS)
            );
            if (analysisAgent) return analysisAgent;
        }

        if (taskLower.includes('search') || taskLower.includes('find')) {
            const searchAgent = agents.find(a =>
                a.capabilities.includes(AgentCapability.WEB_SEARCH)
            );
            if (searchAgent) return searchAgent;
        }

        // Default to first available
        return agents[0];
    }

    async _processQueue() {
        if (this._processing || this._taskQueue.length === 0) return;

        this._processing = true;
        while (this._taskQueue.length > 0 && this.idle().length > 0) {
            const { task, context, resolve, reject } = this._taskQueue.shift();
            try {
                const result = await this.dispatch(task, context);
                resolve(result);
            } catch (error) {
                reject(error);
            }
        }
        this._processing = false;
    }

    async broadcast(task, context = {}) {
        // Send task to all agents in parallel
        const promises = this.all().map(agent =>
            agent.execute(task, context)
        );
        return Promise.all(promises);
    }

    stats() {
        const agents = this.all();
        return {
            total: agents.length,
            idle: this.idle().length,
            busy: this.busy().length,
            queuedTasks: this._taskQueue.length,
            capabilityBreakdown: this._capabilityBreakdown(agents),
        };
    }

    _capabilityBreakdown(agents) {
        const breakdown = {};
        for (const agent of agents) {
            for (const cap of agent.capabilities) {
                breakdown[cap] = (breakdown[cap] || 0) + 1;
            }
        }
        return breakdown;
    }
}

/**
 * Create agent builder
 */
function createAgent(client) {
    return new AgentBuilder(client);
}

/**
 * Create agent pool
 */
function createPool(client) {
    return new AgentPool(client);
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
    AgentBuilder,
    AgentPool,
    createAgent,
    createPool,
    AgentCapability,
    Agent,
    AgentAPI,
};

export default {
    AgentBuilder,
    AgentPool,
    createAgent,
    createPool,
};
