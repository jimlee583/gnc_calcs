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
  AttitudePropagationInput,
  AttitudePropagationOutput,
  OrbitalInput,
  OrbitalOutput,
  OrbitalTrajectoryInput,
  OrbitalTrajectoryOutput,
  QuaternionInput,
  QuaternionOutput,
  RelativeMotionInput,
  RelativeMotionOutput,
  RelativeTrajectoryInput,
  RelativeTrajectoryOutput,
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

/**
 * Generate orbital trajectory points for visualization.
 */
export async function getOrbitalTrajectory(
  input: OrbitalTrajectoryInput
): Promise<OrbitalTrajectoryOutput> {
  return apiCall<OrbitalTrajectoryInput, OrbitalTrajectoryOutput>('/orbit/trajectory', input);
}

/**
 * Generate relative motion trajectory points for visualization.
 */
export async function getRelativeTrajectory(
  input: RelativeTrajectoryInput
): Promise<RelativeTrajectoryOutput> {
  return apiCall<RelativeTrajectoryInput, RelativeTrajectoryOutput>('/relative/trajectory', input);
}

/**
 * Perform quaternion operations and conversions.
 *
 * Takes a quaternion (optionally with angular velocity) and returns
 * normalized quaternion, Euler angles, and DCM.
 */
export async function calculateQuaternion(
  input: QuaternionInput
): Promise<QuaternionOutput> {
  return apiCall<QuaternionInput, QuaternionOutput>('/attitude/quaternion', input);
}

/**
 * Propagate spacecraft attitude over time using RK4 integration.
 *
 * Returns a time history of attitude states including quaternion,
 * angular velocity, Euler angles, and conservation quantities.
 */
export async function propagateAttitude(
  input: AttitudePropagationInput
): Promise<AttitudePropagationOutput> {
  return apiCall<AttitudePropagationInput, AttitudePropagationOutput>('/attitude/propagate', input);
}
