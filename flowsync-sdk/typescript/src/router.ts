/**
 * FlowSync Router — High-level routing utilities
 */

import { FlowSync } from './client';
import type { RouteResponse, ProcessingMode, DomainId } from './types';

/**
 * High-level router for common use cases.
 *
 * Provides convenient methods for different routing scenarios
 * without needing to specify all parameters.
 */
export class Router {
  constructor(private client: FlowSync) {}

  async analyze(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'analyst',
      demigod: 'athena',
    });
  }

  async create(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'creator',
      demigod: 'apollo',
    });
  }

  async execute(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'executor',
      demigod: 'hermes',
    });
  }

  async code(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'analyst',
      domain: 'work',
      demigod: 'hephaestus',
    });
  }

  async strategy(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'analyst',
      domain: 'work',
      demigod: 'athena',
      historicalFlavor: 'sun_tzu',
    });
  }

  async innovate(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'creator',
      demigod: 'apollo',
      historicalFlavor: 'tesla',
    });
  }

  async integrate(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'sage',
      demigod: 'hermes',
      historicalFlavor: 'leonardo',
    });
  }

  async challenge(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'executor',
      domain: 'sports',
      demigod: 'ares',
    });
  }

  async focus(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'executor',
      demigod: 'artemis',
    });
  }

  async communicate(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'executor',
      demigod: 'mercury',
    });
  }

  async transcend(userId: string, message: string): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      mode: 'transcendent',
    });
  }

  async forDomain(userId: string, message: string, domain: DomainId): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      domain,
    });
  }

  async withWeights(
    userId: string,
    message: string,
    weights: { nous?: number; anima?: number; holos?: number }
  ): Promise<RouteResponse> {
    return this.client.route({
      userId,
      message,
      customWeights: weights,
    });
  }
}

/**
 * Domain-specific routing shortcuts.
 */
export class DomainRouter {
  constructor(
    private client: FlowSync,
    private userId: string
  ) {}

  async work(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'work' });
  }

  async school(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'school' });
  }

  async sports(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'sports' });
  }

  async creative(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'create' });
  }

  async spiritual(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'spiritual' });
  }

  async social(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'social' });
  }

  async health(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'health' });
  }

  async life(message: string): Promise<RouteResponse> {
    return this.client.route({ userId: this.userId, message, domain: 'life' });
  }
}
