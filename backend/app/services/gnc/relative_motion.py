"""
Relative Motion Service - Clohessy-Wiltshire (Hill) Equations

This module implements the linearized equations of relative motion for
spacecraft proximity operations. The CW equations describe the motion of
a deputy spacecraft relative to a chief spacecraft in a circular orbit.

Reference Frame (LVLH - Local Vertical Local Horizontal):
    x: Radial direction (outward from central body)
    y: In-track direction (velocity direction of chief)
    z: Cross-track direction (normal to orbital plane, completes right-hand system)

Clohessy-Wiltshire Equations (linearized):
    ẍ - 2nẏ - 3n²x = 0
    ÿ + 2nẋ = 0
    z̈ + n²z = 0

Where:
    n = Mean motion of chief orbit = √(μ/a³) [rad/s]
    x, y, z = Relative position components [km]
    
Closed-form solutions exist for these linear equations, enabling
analytical propagation without numerical integration.

Assumptions:
    - Chief orbit is circular (e = 0)
    - Small relative distances (linearization valid)
    - No differential perturbations
    - No thrust or external forces
    
TODO: Add Yamanaka-Ankersen state transition matrix for eccentric orbits
TODO: Add J2 differential drag model
TODO: Add continuous thrust relative motion
TODO: Add collision avoidance constraints
"""

import numpy as np

from app.schemas.gnc import RelativeMotionInput, RelativeMotionOutput


def compute_relative_motion(inputs: RelativeMotionInput) -> RelativeMotionOutput:
    """
    Propagate relative motion using Clohessy-Wiltshire state transition matrix.
    
    The CW equations have closed-form solutions that can be expressed as a
    6x6 state transition matrix (STM) that maps initial state to final state.
    
    Args:
        inputs: RelativeMotionInput with chief orbit and initial relative state
        
    Returns:
        RelativeMotionOutput with propagated state and derived quantities
    """
    # Extract inputs
    a = inputs.chief_semi_major_axis
    mu = inputs.gravitational_parameter
    t = inputs.propagation_time

    # Initial state vector [x, y, z, ẋ, ẏ, ż]
    x0 = inputs.x0
    y0 = inputs.y0
    z0 = inputs.z0
    xd0 = inputs.x_dot0
    yd0 = inputs.y_dot0
    zd0 = inputs.z_dot0

    # Mean motion of chief orbit
    # n = √(μ/a³)
    n = np.sqrt(mu / a**3)

    # Precompute trigonometric terms
    nt = n * t
    cos_nt = np.cos(nt)
    sin_nt = np.sin(nt)

    # CW State Transition Matrix (6x6)
    # The matrix is partitioned into position and velocity blocks
    # [r(t)]   [Φ_rr  Φ_rv] [r(0)]
    # [v(t)] = [Φ_vr  Φ_vv] [v(0)]

    # In-plane motion (x, y coupled)
    # x(t) = (4 - 3*cos(nt))*x0 + sin(nt)/n*xd0 + 2*(1 - cos(nt))/n*yd0
    x = (4 - 3 * cos_nt) * x0 + sin_nt / n * xd0 + 2 * (1 - cos_nt) / n * yd0

    # y(t) = 6*(sin(nt) - nt)*x0 + y0 + 2*(cos(nt) - 1)/n*xd0 + (4*sin(nt) - 3*nt)/n*yd0
    y = 6 * (sin_nt - nt) * x0 + y0 - 2 * (1 - cos_nt) / n * xd0 + (4 * sin_nt - 3 * nt) / n * yd0

    # Cross-track motion (z decoupled - simple harmonic oscillator)
    # z(t) = z0*cos(nt) + zd0/n*sin(nt)
    z = z0 * cos_nt + zd0 / n * sin_nt

    # Velocities (time derivatives of position solutions)
    # ẋ(t) = 3*n*sin(nt)*x0 + cos(nt)*xd0 + 2*sin(nt)*yd0
    x_dot = 3 * n * sin_nt * x0 + cos_nt * xd0 + 2 * sin_nt * yd0

    # ẏ(t) = 6*n*(cos(nt) - 1)*x0 + 2*sin(nt)*xd0 + (4*cos(nt) - 3)*yd0
    y_dot = 6 * n * (cos_nt - 1) * x0 + 2 * sin_nt * xd0 + (4 * cos_nt - 3) * yd0

    # ż(t) = -z0*n*sin(nt) + zd0*cos(nt)
    z_dot = -z0 * n * sin_nt + zd0 * cos_nt

    # Range and range rate
    range_mag = np.sqrt(x**2 + y**2 + z**2)

    # Range rate = d/dt(|r|) = (r · v) / |r|
    if range_mag > 1e-10:
        range_rate = (x * x_dot + y * y_dot + z * z_dot) / range_mag
    else:
        range_rate = 0.0

    # Check for bounded motion (no secular drift)
    # For CW equations, bounded motion requires: ẏ0 = -2n*x0
    # This is the "closing rate" condition
    drift_per_orbit = 6 * np.pi * x0 + 4 * yd0 / n  # Secular drift in y per orbit
    is_bounded = abs(drift_per_orbit) < 1e-6  # Threshold for numerical tolerance

    assumptions = [
        "Chief orbit is circular (zero eccentricity)",
        "Relative distances small compared to orbital radius",
        "Linearized equations of motion (first-order expansion)",
        "No differential perturbations (J2, drag, SRP)",
        "No thrust or external forces on either vehicle",
        "Instantaneous propagation (no integration error)",
    ]

    return RelativeMotionOutput(
        x=float(x),
        y=float(y),
        z=float(z),
        x_dot=float(x_dot),
        y_dot=float(y_dot),
        z_dot=float(z_dot),
        range_magnitude=float(range_mag),
        range_rate=float(range_rate),
        mean_motion=float(n),
        is_bounded=bool(is_bounded),
        drift_rate=float(drift_per_orbit),
        assumptions=assumptions,
    )
