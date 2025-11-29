#!/usr/bin/env node
/**
 * FlowSync SDK Demo
 * Demonstrates all major SDK features
 */

import {
    FlowSync,
    AgentCapability,
    StepType,
    ComplianceFramework,
    TokenType,
} from './flowsync.js';

import { createAgent, createPool } from './agent-api.js';
import { createWorkflow, WorkflowTemplates, createScheduler } from './workflow-api.js';
import { createChecker, createReporter } from './compliance-api.js';
import { createMarketplace, createGovernance, Tokenomics } from './economy-api.js';

async function main() {
    console.log('\n' + '='.repeat(60));
    console.log('FLOWSYNC SDK DEMO');
    console.log('='.repeat(60) + '\n');

    // Initialize client
    const client = new FlowSync({ apiKey: 'demo-key', debug: true });
    await client.connect();

    // =========================================================================
    // SECTION 1: AGENTS
    // =========================================================================
    console.log('\n[1] AGENT API\n' + '-'.repeat(40));

    // Create agent using builder pattern
    const codeAgent = await createAgent(client)
        .name('code-assistant')
        .withCodeGen()
        .withReasoning()
        .withMemory()
        .withMetadata({ purpose: 'code generation' })
        .onBeforeTask((task) => console.log(`  Starting: ${task}`))
        .onAfterTask((result) => console.log(`  Completed: ${result.success}`))
        .build();

    console.log(`Created agent: ${codeAgent.name} (${codeAgent.id})`);

    // Execute task
    const result = await codeAgent.execute('Write a function to sort an array');
    console.log(`Task result: ${result.success ? 'SUCCESS' : 'FAILED'}`);

    // Create agent pool
    const pool = createPool(client);
    await pool.add(codeAgent);

    const analysisAgent = await createAgent(client)
        .name('data-analyst')
        .withDataAnalysis()
        .withNLP()
        .build();
    await pool.add(analysisAgent);

    console.log(`Agent pool stats:`, pool.stats());

    // =========================================================================
    // SECTION 2: WORKFLOWS
    // =========================================================================
    console.log('\n[2] WORKFLOW API\n' + '-'.repeat(40));

    // Create workflow using builder
    const workflow = await createWorkflow(client)
        .name('code-review-workflow')
        .description('Automated code review process')
        .action('fetch', 'fetch_code', { input: '$repository', output: 'code' })
        .agent('analyze', codeAgent.id, { input: '$code', output: 'analysis' })
        .condition('check_quality', 'analysis.score > 70')
        .action('approve', 'mark_approved', { input: '$analysis' })
        .checkpoint('review_complete')
        .build();

    console.log(`Created workflow: ${workflow.name}`);

    // Run workflow
    const run = await workflow.run({ repository: 'github.com/example/repo' });
    console.log(`Workflow run: ${run.status}`);
    console.log(`Steps completed: ${run.stepResults.length}`);

    // Use template
    const dataPipeline = await WorkflowTemplates.dataPipeline(client, 'etl-pipeline').build();
    console.log(`Created template workflow: ${dataPipeline.name}`);

    // =========================================================================
    // SECTION 3: COMPLIANCE
    // =========================================================================
    console.log('\n[3] COMPLIANCE API\n' + '-'.repeat(40));

    // Create compliance checker
    const checker = createChecker(client);

    // Run compliance check with evidence
    const report = await client.compliance.check({
        target: 'code-assistant',
        frameworks: [ComplianceFramework.GDPR, ComplianceFramework.EU_AI_ACT],
        evidence: {
            'gdpr-1': true,
            'gdpr-2': true,
            'gdpr-3': true,
            'euai-1': true,
            'euai-2': true,
        },
    });

    console.log(`Compliance score: ${report.score.toFixed(1)}%`);
    console.log(`Status: ${report.overallStatus}`);

    // Generate report
    const reporter = createReporter();
    const markdown = reporter.toMarkdown(report);
    console.log(`Report generated (${markdown.length} chars)`);

    // =========================================================================
    // SECTION 4: ECONOMY
    // =========================================================================
    console.log('\n[4] ECONOMY API\n' + '-'.repeat(40));

    // Create wallets
    const wallet1 = await client.economy.createWallet('user1');
    const wallet2 = await client.economy.createWallet('user2');

    // Fund wallet (simulated)
    wallet1.balances[TokenType.ORB] = 10000;
    console.log(`Wallet 1 balance: ${wallet1.balance(TokenType.ORB)} ORB`);

    // Transfer
    const tx = await client.economy.transfer(
        wallet1.id,
        wallet2.id,
        TokenType.ORB,
        100
    );
    console.log(`Transfer: ${tx.amount} ORB (fee: ${tx.fee})`);

    // Stake
    const stake = await client.economy.stake(wallet1.id, 1000, 'compute', 30);
    console.log(`Staked: ${stake.amount} ORB for ${stake.nodeType}`);

    // Economy stats
    console.log(`Economy stats:`, client.economy.getStats());

    // Tokenomics info
    console.log(`Total supply: ${Tokenomics.TOTAL_SUPPLY.toLocaleString()} ORB`);
    console.log(`Staking APY (compute): ${Tokenomics.STAKING.compute.apy * 100}%`);

    // =========================================================================
    // SECTION 5: MARKETPLACE
    // =========================================================================
    console.log('\n[5] MARKETPLACE\n' + '-'.repeat(40));

    const marketplace = createMarketplace(client.economy);

    // Create listing
    const listing = await marketplace.createListing({
        seller: wallet1.id,
        nodeType: 'compute',
        capacity: 8, // 8 vCPUs
        price: 0.10, // ORB per hour
    });
    console.log(`Created listing: ${listing.id}`);

    // Search listings
    const listings = await marketplace.search({ nodeType: 'compute' });
    console.log(`Found ${listings.length} compute listings`);

    // Marketplace stats
    console.log(`Marketplace stats:`, marketplace.stats());

    // =========================================================================
    // SECTION 6: GOVERNANCE
    // =========================================================================
    console.log('\n[6] GOVERNANCE\n' + '-'.repeat(40));

    const governance = createGovernance(client.economy);

    // Create proposal
    const proposal = await governance.createProposal({
        creator: wallet1.id,
        title: 'Increase compute staking rewards',
        description: 'Proposal to increase compute node staking APY from 12% to 15%',
        type: 'parameter',
    });
    console.log(`Created proposal: ${proposal.title}`);

    // Vote
    await governance.vote(proposal.id, wallet1.id, true, 1000);
    await governance.vote(proposal.id, wallet2.id, true, 100);
    console.log(`Votes cast: For=${proposal.votesFor}, Against=${proposal.votesAgainst}`);

    // =========================================================================
    // SUMMARY
    // =========================================================================
    console.log('\n' + '='.repeat(60));
    console.log('DEMO COMPLETE');
    console.log('='.repeat(60));

    console.log('\nSDK Features Demonstrated:');
    console.log('  - Agent creation with builder pattern');
    console.log('  - Agent pools for task dispatch');
    console.log('  - Workflow creation and execution');
    console.log('  - Workflow templates');
    console.log('  - Compliance checking (GDPR, EU AI Act)');
    console.log('  - Report generation (Markdown, HTML, CSV)');
    console.log('  - Wallet management');
    console.log('  - Token transfers and staking');
    console.log('  - Marketplace listings');
    console.log('  - Governance proposals and voting');

    console.log('\nNext steps:');
    console.log('  1. Set FLOWSYNC_API_KEY environment variable');
    console.log('  2. Import SDK in your project');
    console.log('  3. Build amazing AI-powered applications!\n');

    await client.disconnect();
}

main().catch(console.error);
