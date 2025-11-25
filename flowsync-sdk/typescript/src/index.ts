/**
 * FlowSync SDK — The 0r8 Developer Interface
 * Route through 3i-ATLAS. Summon Demigods. Build the future.
 *
 * @example
 * ```typescript
 * import { FlowSync } from '@0r8/flowsync';
 *
 * const client = new FlowSync({ apiKey: 'your-api-key' });
 * const response = await client.route({
 *   userId: 'user-123',
 *   message: 'Help me build a business plan',
 *   mode: 'analyst',
 *   demigod: 'athena'
 * });
 * ```
 */

export { FlowSync } from './client';
export { Router, DomainRouter } from './router';
export { DemigodSelector, DEMIGODS } from './demigods';
export * from './types';
