/**
 * FlowSync Workflow API
 * Define, execute, and monitor workflows
 */

import { Workflow, WorkflowAPI, WorkflowRun, StepType } from './flowsync.js';

// =============================================================================
// WORKFLOW BUILDER
// =============================================================================

/**
 * Fluent workflow builder
 */
class WorkflowBuilder {
    constructor(client) {
        this._client = client;
        this._config = {
            name: 'unnamed-workflow',
            description: '',
            steps: [],
            metadata: {},
            triggers: [],
            errorHandlers: [],
        };
    }

    name(name) {
        this._config.name = name;
        return this;
    }

    description(desc) {
        this._config.description = desc;
        return this;
    }

    /**
     * Add an action step
     */
    action(name, action, options = {}) {
        this._config.steps.push({
            name,
            type: StepType.ACTION,
            action,
            input: options.input || '',
            output: options.output || '',
            timeout: options.timeout || 60,
            retries: options.retries || 1,
        });
        return this;
    }

    /**
     * Add an agent call step
     */
    agent(name, agentId, options = {}) {
        this._config.steps.push({
            name,
            type: StepType.AGENT_CALL,
            agentId,
            input: options.input || '',
            output: options.output || '',
            timeout: options.timeout || 120,
        });
        return this;
    }

    /**
     * Add a condition step
     */
    condition(name, conditionExpr, options = {}) {
        this._config.steps.push({
            name,
            type: StepType.CONDITION,
            condition: conditionExpr,
            onSuccess: options.onSuccess || null,
            onFailure: options.onFailure || null,
        });
        return this;
    }

    /**
     * Add a parallel execution step
     */
    parallel(name, tasks) {
        this._config.steps.push({
            name,
            type: StepType.PARALLEL,
            tasks,
        });
        return this;
    }

    /**
     * Add a loop step
     */
    loop(name, options = {}) {
        this._config.steps.push({
            name,
            type: StepType.LOOP,
            collection: options.over || '',
            itemVar: options.as || 'item',
            body: options.do || [],
        });
        return this;
    }

    /**
     * Add a human-in-the-loop step
     */
    humanApproval(name, options = {}) {
        this._config.steps.push({
            name,
            type: StepType.HUMAN_IN_LOOP,
            prompt: options.prompt || 'Approval required',
            approvers: options.approvers || [],
            timeout: options.timeout || 3600, // 1 hour default
        });
        return this;
    }

    /**
     * Add a checkpoint step
     */
    checkpoint(name) {
        this._config.steps.push({
            name,
            type: StepType.CHECKPOINT,
        });
        return this;
    }

    /**
     * Add metadata
     */
    withMetadata(metadata) {
        this._config.metadata = { ...this._config.metadata, ...metadata };
        return this;
    }

    /**
     * Add trigger
     */
    trigger(type, config = {}) {
        this._config.triggers.push({ type, config });
        return this;
    }

    /**
     * Add error handler
     */
    onError(handler) {
        this._config.errorHandlers.push(handler);
        return this;
    }

    /**
     * Build the workflow
     */
    async build() {
        return await this._client.workflows.create({
            name: this._config.name,
            description: this._config.description,
            steps: this._config.steps,
            metadata: {
                ...this._config.metadata,
                triggers: this._config.triggers,
                errorHandlers: this._config.errorHandlers.length,
            },
        });
    }
}

// =============================================================================
// WORKFLOW TEMPLATES
// =============================================================================

/**
 * Pre-built workflow templates
 */
const WorkflowTemplates = {
    /**
     * Simple sequential workflow
     */
    sequential(client, name, actions) {
        const builder = new WorkflowBuilder(client).name(name);
        for (const [stepName, action] of Object.entries(actions)) {
            builder.action(stepName, action);
        }
        return builder;
    },

    /**
     * Data processing pipeline
     */
    dataPipeline(client, name) {
        return new WorkflowBuilder(client)
            .name(name)
            .description('Data processing pipeline')
            .action('extract', 'extract_data', { output: 'raw_data' })
            .action('transform', 'transform_data', { input: '$raw_data', output: 'clean_data' })
            .action('validate', 'validate_data', { input: '$clean_data', output: 'valid_data' })
            .action('load', 'load_data', { input: '$valid_data' })
            .checkpoint('pipeline_complete');
    },

    /**
     * Approval workflow
     */
    approvalFlow(client, name, approvers) {
        return new WorkflowBuilder(client)
            .name(name)
            .description('Multi-stage approval workflow')
            .action('prepare', 'prepare_request', { output: 'request' })
            .humanApproval('manager_approval', {
                prompt: 'Manager approval required',
                approvers: approvers.slice(0, 1),
            })
            .condition('check_amount', 'request.amount > 10000', {
                onSuccess: 'executive_approval',
            })
            .humanApproval('executive_approval', {
                prompt: 'Executive approval required for large amounts',
                approvers: approvers.slice(1),
            })
            .action('execute', 'execute_request', { input: '$request' });
    },

    /**
     * Agent-powered workflow
     */
    agentPowered(client, name, agentIds) {
        const builder = new WorkflowBuilder(client)
            .name(name)
            .description('Multi-agent workflow');

        if (agentIds.analyst) {
            builder.agent('analyze', agentIds.analyst, {
                input: '$query',
                output: 'analysis',
            });
        }

        if (agentIds.generator) {
            builder.agent('generate', agentIds.generator, {
                input: '$analysis',
                output: 'output',
            });
        }

        if (agentIds.reviewer) {
            builder.agent('review', agentIds.reviewer, {
                input: '$output',
                output: 'final_output',
            });
        }

        return builder;
    },

    /**
     * Retry workflow
     */
    withRetry(client, name, action, maxRetries = 3) {
        return new WorkflowBuilder(client)
            .name(name)
            .action('attempt', action, { retries: maxRetries, output: 'result' })
            .condition('check_success', 'result.success')
            .checkpoint('completed');
    },
};

// =============================================================================
// WORKFLOW SCHEDULER
// =============================================================================

/**
 * Schedule workflow executions
 */
class WorkflowScheduler {
    constructor() {
        this._schedules = new Map();
        this._running = false;
        this._intervals = [];
    }

    /**
     * Schedule a workflow to run at intervals
     */
    every(workflow, intervalMs, inputs = {}) {
        const scheduleId = `sched_${Date.now()}`;
        this._schedules.set(scheduleId, {
            workflow,
            intervalMs,
            inputs,
            lastRun: null,
            nextRun: Date.now() + intervalMs,
            runs: 0,
        });
        return scheduleId;
    }

    /**
     * Schedule a workflow to run once at a specific time
     */
    at(workflow, date, inputs = {}) {
        const scheduleId = `once_${Date.now()}`;
        const runTime = date instanceof Date ? date.getTime() : date;

        this._schedules.set(scheduleId, {
            workflow,
            runAt: runTime,
            inputs,
            once: true,
        });
        return scheduleId;
    }

    /**
     * Schedule using cron-like expression (simplified)
     */
    cron(workflow, cronExpr, inputs = {}) {
        // Simplified cron - just support basic intervals
        const scheduleId = `cron_${Date.now()}`;
        let intervalMs = 60000; // Default 1 minute

        if (cronExpr.includes('hour')) intervalMs = 3600000;
        if (cronExpr.includes('day')) intervalMs = 86400000;
        if (cronExpr.includes('week')) intervalMs = 604800000;

        return this.every(workflow, intervalMs, inputs);
    }

    /**
     * Cancel a schedule
     */
    cancel(scheduleId) {
        return this._schedules.delete(scheduleId);
    }

    /**
     * Start the scheduler
     */
    start() {
        if (this._running) return;
        this._running = true;

        const checkInterval = setInterval(() => {
            this._check();
        }, 1000); // Check every second

        this._intervals.push(checkInterval);
    }

    /**
     * Stop the scheduler
     */
    stop() {
        this._running = false;
        for (const interval of this._intervals) {
            clearInterval(interval);
        }
        this._intervals = [];
    }

    async _check() {
        const now = Date.now();

        for (const [scheduleId, schedule] of this._schedules.entries()) {
            if (schedule.once) {
                if (now >= schedule.runAt) {
                    await this._execute(schedule);
                    this._schedules.delete(scheduleId);
                }
            } else {
                if (now >= schedule.nextRun) {
                    await this._execute(schedule);
                    schedule.lastRun = now;
                    schedule.nextRun = now + schedule.intervalMs;
                    schedule.runs++;
                }
            }
        }
    }

    async _execute(schedule) {
        try {
            await schedule.workflow.run(schedule.inputs);
        } catch (error) {
            console.error(`Scheduled workflow failed: ${error.message}`);
        }
    }

    /**
     * Get scheduler stats
     */
    stats() {
        const schedules = Array.from(this._schedules.values());
        return {
            running: this._running,
            totalSchedules: schedules.length,
            onceSchedules: schedules.filter(s => s.once).length,
            recurringSchedules: schedules.filter(s => !s.once).length,
            totalRuns: schedules.reduce((sum, s) => sum + (s.runs || 0), 0),
        };
    }
}

// =============================================================================
// WORKFLOW MONITOR
// =============================================================================

/**
 * Monitor workflow executions
 */
class WorkflowMonitor {
    constructor() {
        this._runs = [];
        this._listeners = [];
    }

    /**
     * Track a workflow run
     */
    track(run) {
        this._runs.push({
            ...run,
            trackedAt: new Date(),
        });

        // Notify listeners
        for (const listener of this._listeners) {
            listener(run);
        }
    }

    /**
     * Subscribe to run updates
     */
    onRun(callback) {
        this._listeners.push(callback);
        return () => {
            const idx = this._listeners.indexOf(callback);
            if (idx > -1) this._listeners.splice(idx, 1);
        };
    }

    /**
     * Get runs by status
     */
    byStatus(status) {
        return this._runs.filter(r => r.status === status);
    }

    /**
     * Get runs by workflow ID
     */
    byWorkflow(workflowId) {
        return this._runs.filter(r => r.workflowId === workflowId);
    }

    /**
     * Get recent runs
     */
    recent(count = 10) {
        return this._runs.slice(-count);
    }

    /**
     * Get statistics
     */
    stats() {
        const total = this._runs.length;
        const completed = this._runs.filter(r => r.status === 'completed').length;
        const failed = this._runs.filter(r => r.status === 'failed').length;

        const durations = this._runs
            .filter(r => r.completedAt && r.startedAt)
            .map(r => new Date(r.completedAt) - new Date(r.startedAt));

        const avgDuration = durations.length > 0
            ? durations.reduce((a, b) => a + b, 0) / durations.length
            : 0;

        return {
            total,
            completed,
            failed,
            pending: total - completed - failed,
            successRate: total > 0 ? (completed / total) * 100 : 0,
            avgDurationMs: avgDuration,
        };
    }

    /**
     * Clear history
     */
    clear() {
        this._runs = [];
    }
}

// =============================================================================
// FACTORY FUNCTIONS
// =============================================================================

function createWorkflow(client) {
    return new WorkflowBuilder(client);
}

function createScheduler() {
    return new WorkflowScheduler();
}

function createMonitor() {
    return new WorkflowMonitor();
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
    WorkflowBuilder,
    WorkflowTemplates,
    WorkflowScheduler,
    WorkflowMonitor,
    createWorkflow,
    createScheduler,
    createMonitor,
    Workflow,
    WorkflowAPI,
    WorkflowRun,
    StepType,
};

export default {
    WorkflowBuilder,
    WorkflowTemplates,
    WorkflowScheduler,
    WorkflowMonitor,
    createWorkflow,
    createScheduler,
    createMonitor,
};
