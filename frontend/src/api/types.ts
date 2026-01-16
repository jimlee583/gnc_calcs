/**
 * TypeScript type definitions for GNC API requests and responses.
 * 
 * These types mirror the Pydantic schemas in the backend and provide
 * type safety for all API interactions.
 */

// =============================================================================
// Attitude Dynamics Types
// =============================================================================

/**
 * Input for rigid-body attitude dynamics calculation.
 * Uses Euler's equations for rotational motion.
 */
export interface AttitudeInput {
  /** Principal moment of inertia about X-axis [kg·m²] */
  inertia_x: number;
  /** Principal moment of inertia about Y-axis [kg·m²] */
  inertia_y: number;
  /** Principal moment of inertia about Z-axis [kg·m²] */
  inertia_z: number;
  /** Angular velocity about X-axis [rad/s] */
  omega_x: number;
  /** Angular velocity about Y-axis [rad/s] */
  omega_y: number;
  /** Angular velocity about Z-axis [rad/s] */
  omega_z: number;
  /** External torque about X-axis [N·m] */
  torque_x?: number;
  /** External torque about Y-axis [N·m] */
  torque_y?: number;
  /** External torque about Z-axis [N·m] */
  torque_z?: number;
}

/**
 * Output from attitude dynamics calculation.
 */
export interface AttitudeOutput {
  /** Angular acceleration about X-axis [rad/s²] */
  omega_dot_x: number;
  /** Angular acceleration about Y-axis [rad/s²] */
  omega_dot_y: number;
  /** Angular acceleration about Z-axis [rad/s²] */
  omega_dot_z: number;
  /** Rotational kinetic energy [J] */
  rotational_kinetic_energy: number;
  /** Total angular momentum magnitude [kg·m²/s] */
  angular_momentum_magnitude: number;
  /** Assumptions used in calculation */
  assumptions: string[];
}

// =============================================================================
// Orbital Dynamics Types
// =============================================================================

/**
 * Input for two-body orbital dynamics calculation.
 */
export interface OrbitalInput {
  /** Semi-major axis [km] */
  semi_major_axis: number;
  /** Orbital eccentricity [dimensionless] */
  eccentricity: number;
  /** Gravitational parameter μ [km³/s²] (defaults to Earth) */
  gravitational_parameter?: number;
  /** Central body equatorial radius [km] (defaults to Earth) */
  central_body_radius?: number;
  /** True anomaly [deg] */
  true_anomaly?: number;
}

/**
 * Output from orbital dynamics calculation.
 */
export interface OrbitalOutput {
  /** Orbital period [s] */
  orbital_period: number;
  /** Mean motion [rad/s] */
  mean_motion: number;
  /** Orbital radius at true anomaly [km] */
  radius: number;
  /** Orbital velocity at true anomaly [km/s] */
  velocity: number;
  /** Periapsis radius [km] */
  periapsis_radius: number;
  /** Apoapsis radius [km] */
  apoapsis_radius: number;
  /** Periapsis altitude above surface [km] */
  periapsis_altitude: number;
  /** Apoapsis altitude above surface [km] */
  apoapsis_altitude: number;
  /** Velocity at periapsis [km/s] */
  periapsis_velocity: number;
  /** Velocity at apoapsis [km/s] */
  apoapsis_velocity: number;
  /** Specific orbital energy [km²/s²] */
  specific_orbital_energy: number;
  /** Specific angular momentum [km²/s] */
  specific_angular_momentum: number;
  /** Assumptions used in calculation */
  assumptions: string[];
}

// =============================================================================
// Relative Motion Types
// =============================================================================

/**
 * Input for Clohessy-Wiltshire relative motion calculation.
 */
export interface RelativeMotionInput {
  /** Chief orbit semi-major axis [km] */
  chief_semi_major_axis: number;
  /** Gravitational parameter μ [km³/s²] (defaults to Earth) */
  gravitational_parameter?: number;
  /** Initial radial position [km] */
  x0: number;
  /** Initial in-track position [km] */
  y0: number;
  /** Initial cross-track position [km] */
  z0: number;
  /** Initial radial velocity [km/s] */
  x_dot0: number;
  /** Initial in-track velocity [km/s] */
  y_dot0: number;
  /** Initial cross-track velocity [km/s] */
  z_dot0: number;
  /** Time to propagate [s] */
  propagation_time: number;
}

/**
 * Output from relative motion calculation.
 */
export interface RelativeMotionOutput {
  /** Final radial position [km] */
  x: number;
  /** Final in-track position [km] */
  y: number;
  /** Final cross-track position [km] */
  z: number;
  /** Final radial velocity [km/s] */
  x_dot: number;
  /** Final in-track velocity [km/s] */
  y_dot: number;
  /** Final cross-track velocity [km/s] */
  z_dot: number;
  /** Range from chief to deputy [km] */
  range_magnitude: number;
  /** Range rate [km/s] */
  range_rate: number;
  /** Mean motion of chief orbit [rad/s] */
  mean_motion: number;
  /** Whether relative motion is bounded (no drift) */
  is_bounded: boolean;
  /** Secular drift rate in y-direction [km/orbit] */
  drift_rate: number;
  /** Assumptions used in calculation */
  assumptions: string[];
}

// =============================================================================
// API Error Type
// =============================================================================

export interface ApiError {
  detail: string;
}
