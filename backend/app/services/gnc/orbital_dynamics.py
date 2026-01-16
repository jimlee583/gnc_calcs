"""
Orbital Dynamics Service - Two-Body Keplerian Motion

This module implements classical two-body orbital mechanics calculations.
These form the foundation for spacecraft trajectory analysis.

Key Equations:
    Vis-viva equation:     v² = μ * (2/r - 1/a)
    Orbital period:        T = 2π * √(a³/μ)
    Orbit equation:        r = a * (1 - e²) / (1 + e * cos(ν))
    Specific energy:       ε = -μ / (2a)
    Angular momentum:      h = √(μ * a * (1 - e²))

Where:
    μ = Gravitational parameter [km³/s²]
    a = Semi-major axis [km]
    e = Eccentricity [dimensionless]
    ν = True anomaly [rad]
    r = Orbital radius [km]
    v = Orbital velocity [km/s]
    T = Orbital period [s]

Assumptions:
    - Two-body problem (no perturbations)
    - Point masses
    - Elliptical orbits only (0 ≤ e < 1)
    
TODO: Add hyperbolic orbit support (e ≥ 1)
TODO: Add J2 perturbation corrections
TODO: Add atmospheric drag at low altitudes
TODO: Add third-body perturbations (Sun, Moon)
"""

import numpy as np

from app.schemas.gnc import OrbitalInput, OrbitalOutput


def compute_orbital_dynamics(inputs: OrbitalInput) -> OrbitalOutput:
    """
    Compute orbital parameters from classical orbital elements.
    
    This function calculates key orbital characteristics including
    velocities, periods, and specific mechanical quantities.
    
    Args:
        inputs: OrbitalInput containing orbital elements and central body parameters
        
    Returns:
        OrbitalOutput with computed orbital parameters
    """
    # Extract inputs
    a = inputs.semi_major_axis  # km
    e = inputs.eccentricity
    mu = inputs.gravitational_parameter  # km³/s²
    R_body = inputs.central_body_radius  # km
    nu = np.radians(inputs.true_anomaly)  # Convert to radians

    # Semi-latus rectum (parameter)
    # p = a * (1 - e²)
    p = a * (1 - e**2)

    # Orbital period from Kepler's third law
    # T = 2π * √(a³/μ)
    orbital_period = 2 * np.pi * np.sqrt(a**3 / mu)

    # Mean motion
    # n = √(μ/a³) = 2π/T
    mean_motion = np.sqrt(mu / a**3)

    # Radius at given true anomaly (orbit equation)
    # r = p / (1 + e * cos(ν))
    radius = p / (1 + e * np.cos(nu))

    # Velocity at given true anomaly (vis-viva equation)
    # v = √(μ * (2/r - 1/a))
    velocity = np.sqrt(mu * (2 / radius - 1 / a))

    # Periapsis and apoapsis radii
    # r_p = a * (1 - e)
    # r_a = a * (1 + e)
    periapsis_radius = a * (1 - e)
    apoapsis_radius = a * (1 + e)

    # Altitudes above central body surface
    periapsis_altitude = periapsis_radius - R_body
    apoapsis_altitude = apoapsis_radius - R_body

    # Velocities at apses (vis-viva at r_p and r_a)
    periapsis_velocity = np.sqrt(mu * (2 / periapsis_radius - 1 / a))
    apoapsis_velocity = np.sqrt(mu * (2 / apoapsis_radius - 1 / a))

    # Specific orbital energy (constant of motion)
    # ε = -μ / (2a)
    specific_energy = -mu / (2 * a)

    # Specific angular momentum (constant of motion)
    # h = √(μ * p) = √(μ * a * (1 - e²))
    specific_angular_momentum = np.sqrt(mu * p)

    assumptions = [
        "Two-body problem (central body + spacecraft only)",
        "Point mass approximation for both bodies",
        "No atmospheric drag",
        "No solar radiation pressure",
        "No gravitational harmonics (J2, etc.)",
        "Elliptical orbit (eccentricity < 1)",
    ]

    return OrbitalOutput(
        orbital_period=float(orbital_period),
        mean_motion=float(mean_motion),
        radius=float(radius),
        velocity=float(velocity),
        periapsis_radius=float(periapsis_radius),
        apoapsis_radius=float(apoapsis_radius),
        periapsis_altitude=float(periapsis_altitude),
        apoapsis_altitude=float(apoapsis_altitude),
        periapsis_velocity=float(periapsis_velocity),
        apoapsis_velocity=float(apoapsis_velocity),
        specific_orbital_energy=float(specific_energy),
        specific_angular_momentum=float(specific_angular_momentum),
        assumptions=assumptions,
    )
