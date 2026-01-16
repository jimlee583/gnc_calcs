"""
Trajectory Generation Service

This module generates trajectory points for visualization purposes.
It extends the single-point calculations to produce arrays of positions
over time or true anomaly.
"""

import numpy as np

from app.schemas.gnc import (
    OrbitalTrajectoryInput,
    OrbitalTrajectoryOutput,
    RelativeTrajectoryInput,
    RelativeTrajectoryOutput,
    TrajectoryPoint,
)


def generate_orbital_trajectory(inputs: OrbitalTrajectoryInput) -> OrbitalTrajectoryOutput:
    """
    Generate trajectory points for an orbital path.
    
    Creates points around the orbit by varying true anomaly from 0 to 360 degrees.
    The trajectory is in the orbital plane with:
    - x: pointing toward periapsis
    - y: perpendicular in orbital plane
    
    Args:
        inputs: Orbital parameters and number of points
        
    Returns:
        OrbitalTrajectoryOutput with trajectory points and orbit geometry
    """
    a = inputs.semi_major_axis
    e = inputs.eccentricity
    n_points = inputs.num_points
    
    # Semi-latus rectum
    p = a * (1 - e**2)
    
    # Semi-minor axis: b = a * sqrt(1 - e²)
    b = a * np.sqrt(1 - e**2)
    
    # Generate true anomaly values (0 to 2π)
    true_anomalies = np.linspace(0, 2 * np.pi, n_points)
    
    points: list[TrajectoryPoint] = []
    
    for i, nu in enumerate(true_anomalies):
        # Orbital radius at this true anomaly
        r = p / (1 + e * np.cos(nu))
        
        # Position in perifocal frame (x toward periapsis, y perpendicular)
        x = r * np.cos(nu)
        y = r * np.sin(nu)
        
        # Time is represented as fraction of orbit (0 to 1)
        t = float(i) / (n_points - 1)
        
        points.append(TrajectoryPoint(x=float(x), y=float(y), z=None, t=t))
    
    # Apses
    periapsis_radius = a * (1 - e)
    apoapsis_radius = a * (1 + e)
    
    return OrbitalTrajectoryOutput(
        points=points,
        semi_major_axis=float(a),
        semi_minor_axis=float(b),
        periapsis_radius=float(periapsis_radius),
        apoapsis_radius=float(apoapsis_radius),
        central_body_radius=float(inputs.central_body_radius),
    )


def generate_relative_trajectory(inputs: RelativeTrajectoryInput) -> RelativeTrajectoryOutput:
    """
    Generate trajectory points for relative motion visualization.
    
    Propagates the Clohessy-Wiltshire equations over the specified number
    of orbits to create a trajectory in the LVLH frame.
    
    The characteristic CW trajectories include:
    - "Football" shaped bounded orbits
    - Drifting trajectories when not energy-matched
    - Cross-track oscillations
    
    Args:
        inputs: Initial state and propagation parameters
        
    Returns:
        RelativeTrajectoryOutput with trajectory points and characterization
    """
    a = inputs.chief_semi_major_axis
    mu = inputs.gravitational_parameter
    n_points = inputs.num_points
    num_orbits = inputs.num_orbits
    
    # Initial state
    x0 = inputs.x0
    y0 = inputs.y0
    z0 = inputs.z0
    xd0 = inputs.x_dot0
    yd0 = inputs.y_dot0
    zd0 = inputs.z_dot0
    
    # Mean motion
    n = np.sqrt(mu / a**3)
    
    # Orbital period
    orbital_period = 2 * np.pi / n
    
    # Total propagation time
    total_time = num_orbits * orbital_period
    
    # Time array
    times = np.linspace(0, total_time, n_points)
    
    points: list[TrajectoryPoint] = []
    max_range = 0.0
    
    for t in times:
        # Precompute trig terms
        nt = n * t
        cos_nt = np.cos(nt)
        sin_nt = np.sin(nt)
        
        # CW closed-form solutions
        # In-plane motion (x, y coupled)
        x = (4 - 3 * cos_nt) * x0 + sin_nt / n * xd0 + 2 * (1 - cos_nt) / n * yd0
        y = 6 * (sin_nt - nt) * x0 + y0 - 2 * (1 - cos_nt) / n * xd0 + (4 * sin_nt - 3 * nt) / n * yd0
        
        # Cross-track motion (decoupled simple harmonic)
        z = z0 * cos_nt + zd0 / n * sin_nt
        
        # Track maximum range
        range_val = np.sqrt(x**2 + y**2 + z**2)
        max_range = max(max_range, range_val)
        
        points.append(TrajectoryPoint(
            x=float(x),
            y=float(y),
            z=float(z),
            t=float(t),
        ))
    
    # Check for bounded motion
    drift_per_orbit = 6 * np.pi * x0 + 4 * yd0 / n
    is_bounded = abs(drift_per_orbit) < 0.001  # Small threshold
    
    return RelativeTrajectoryOutput(
        points=points,
        orbital_period=float(orbital_period),
        is_bounded=bool(is_bounded),
        max_range=float(max_range),
    )
