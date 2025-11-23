/**
 * Competition Mode Example - TypeScript
 *
 * This example shows how to use Competition Brain for
 * high-stakes competition submissions with maximum quality.
 */

import CompetitionBrain, { QueryResult } from '../src/index';
import * as fs from 'fs';

async function main() {
  const client = new CompetitionBrain({
    baseUrl: 'http://localhost:3001',
    timeout: 300000, // 5 minutes for competition mode
  });

  // Competition query (complex problem)
  const query = `
    Explain the algorithmic complexity of the following problem:
    Given an array of integers, find the maximum sum of any contiguous subarray.
    Provide the optimal solution with time and space complexity analysis.
  `;

  console.log('🏆 Running Competition Mode Query\n');
  console.log(`Query: ${query.trim()}\n`);

  try {
    // Use competition preset (top 5 models, max power)
    const startTime = Date.now();

    const result: QueryResult = await client.competitionQuery(query);

    const elapsed = Date.now() - startTime;

    console.log(`✅ Query completed in ${(elapsed / 1000).toFixed(2)}s\n`);

    // Display synthesized result
    console.log('='.repeat(80));
    console.log('SYNTHESIZED ANSWER (Competition Quality)');
    console.log('='.repeat(80));
    console.log(result.synthesized);
    console.log('='.repeat(80));

    // Show detailed stats
    const stats = client.getStats(result);

    console.log('\n📊 Competition Stats:');
    console.log(`  Models Used: ${stats.totalModels}`);
    console.log(`  Successful: ${stats.successfulModels}`);
    console.log(`  Average Confidence: ${(stats.avgConfidence * 100).toFixed(1)}%`);
    console.log(`  Processing Time: ${stats.totalTime.toFixed(2)}s`);

    // Export to markdown for submission
    const markdown = client.exportMarkdown(result);
    fs.writeFileSync('./competition-submission.md', markdown);
    console.log('\n💾 Exported to: competition-submission.md');

    // Export to JSON for analysis
    const json = client.exportJSON(result);
    fs.writeFileSync('./competition-result.json', json);
    console.log('💾 Exported to: competition-result.json');

    // Quality check
    console.log('\n🔍 Quality Check:');

    const highConfidenceResponses = result.individual.filter(
      r => r.success && r.confidence >= 0.9
    );

    console.log(
      `  High Confidence Responses (≥90%): ${highConfidenceResponses.length}/${stats.successfulModels}`
    );

    if (highConfidenceResponses.length >= 3) {
      console.log('  ✅ Quality threshold met - ready for submission');
    } else {
      console.log('  ⚠️  Consider re-running with different models');
    }

    // Show model breakdown
    console.log('\n🤖 Model Performance:');
    result.individual.forEach(resp => {
      const status = resp.success ? '✅' : '❌';
      const conf = (resp.confidence * 100).toFixed(1);
      console.log(`  ${status} ${resp.model.padEnd(25)} ${conf}% (${resp.time.toFixed(2)}s)`);
    });
  } catch (error) {
    console.error('❌ Competition query failed:', error);
    throw error;
  }
}

main().catch(console.error);
