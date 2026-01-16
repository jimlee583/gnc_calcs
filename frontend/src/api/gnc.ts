/**
 * GNC API Client
 * 
 * This module provides typed functions for calling the GNC calculation
 * endpoints. All functions handle errors consistently and return typed
 * responses.
 */

import type {
  AttitudeInput,
  AttitudeOutput,
  OrbitalInput,
  OrbitalOutput,
  RelativeMotionInput,
  RelativeMotionOutput,
} from './types';

const API_BASE = '/api/gnc';

/**
 * Generic API call handler with error handling
 */
async function apiCall<TInput, TOutput>(
  endpoint: string,
  data: TInput
): Promise<TOutput> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Calculate rigid-body attitude dynamics using Euler's equations.
 * 
 * Computes instantaneous angular accelerations given inertia properties,
 * angular velocities, and applied torques.
 */
export async function calculateAttitude(
  input: AttitudeInput
): Promise<AttitudeOutput> {
  return apiCall<AttitudeInput, AttitudeOutput>('/attitude', input);
}

/**
 * Calculate two-body orbital dynamics from orbital elements.
 * 
 * Computes orbital parameters including period, velocities, and
 * specific mechanical quantities.
 */
export async function calculateOrbit(
  input: OrbitalInput
): Promise<OrbitalOutput> {
  return apiCall<OrbitalInput, OrbitalOutput>('/orbit', input);
}

/**
 * Calculate relative motion using Clohessy-Wiltshire equations.
 * 
 * Propagates relative state using linearized equations of motion
 * for proximity operations.
 */
export async function calculateRelativeMotion(
  input: RelativeMotionInput
): Promise<RelativeMotionOutput> {
  return apiCall<RelativeMotionInput, RelativeMotionOutput>('/relative', input);
}
