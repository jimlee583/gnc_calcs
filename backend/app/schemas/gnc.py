"""
Pydantic schemas for GNC calculation inputs and outputs.

These schemas define the API contract for all GNC endpoints.
All physical quantities include units in their descriptions.
"""

from pydantic import BaseModel, Field


# =============================================================================
# Attitude Dynamics Schemas (Euler's Equations of Rotational Motion)
# =============================================================================


class AttitudeInput(BaseModel):
    """
    Input parameters for rigid-body attitude dynamics calculation.
    
    Uses Euler's equations for rotational motion of a rigid body:
    I_x * ω̇_x - (I_y - I_z) * ω_y * ω_z = M_x
    I_y * ω̇_y - (I_z - I_x) * ω_z * ω_x = M_y
    I_z * ω̇_z - (I_x - I_y) * ω_x * ω_y = M_z
    """

    # Principal moments of inertia [kg·m²]
    inertia_x: float = Field(..., description="Principal moment of inertia about X-axis [kg·m²]", gt=0)
    inertia_y: float = Field(..., description="Principal moment of inertia about Y-axis [kg·m²]", gt=0)
    inertia_z: float = Field(..., description="Principal moment of inertia about Z-axis [kg·m²]", gt=0)

    # Angular velocities [rad/s]
    omega_x: float = Field(..., description="Angular velocity about X-axis [rad/s]")
    omega_y: float = Field(..., description="Angular velocity about Y-axis [rad/s]")
    omega_z: float = Field(..., description="Angular velocity about Z-axis [rad/s]")

    # External torques [N·m]
    torque_x: float = Field(0.0, description="External torque about X-axis [N·m]")
    torque_y: float = Field(0.0, description="External torque about Y-axis [N·m]")
    torque_z: float = Field(0.0, description="External torque about Z-axis [N·m]")


class AttitudeOutput(BaseModel):
    """Output from attitude dynamics calculation."""

    # Angular accelerations [rad/s²]
    omega_dot_x: float = Field(..., description="Angular acceleration about X-axis [rad/s²]")
    omega_dot_y: float = Field(..., description="Angular acceleration about Y-axis [rad/s²]")
    omega_dot_z: float = Field(..., description="Angular acceleration about Z-axis [rad/s²]")

    # Derived quantities
    rotational_kinetic_energy: float = Field(..., description="Rotational kinetic energy [J]")
    angular_momentum_magnitude: float = Field(..., description="Total angular momentum magnitude [kg·m²/s]")

    # Metadata
    assumptions: list[str] = Field(default_factory=list, description="Assumptions used in calculation")


# =============================================================================
# Orbital Dynamics Schemas (Two-Body Problem)
# =============================================================================


class OrbitalInput(BaseModel):
    """
    Input parameters for two-body orbital dynamics.
    
    Uses the vis-viva equation and Keplerian orbital mechanics:
    v² = μ * (2/r - 1/a)
    T = 2π * √(a³/μ)
    """

    # Orbital elements
    semi_major_axis: float = Field(..., description="Semi-major axis [km]", gt=0)
    eccentricity: float = Field(..., description="Orbital eccentricity [dimensionless]", ge=0, lt=1)

    # Central body parameters (defaults to Earth)
    gravitational_parameter: float = Field(
        398600.4418, description="Gravitational parameter μ [km³/s²]", gt=0
    )
    central_body_radius: float = Field(
        6378.137, description="Central body equatorial radius [km]", gt=0
    )

    # True anomaly for specific position calculation
    true_anomaly: float = Field(0.0, description="True anomaly [deg]", ge=0, lt=360)


class OrbitalOutput(BaseModel):
    """Output from orbital dynamics calculation."""

    # Orbital parameters
    orbital_period: float = Field(..., description="Orbital period [s]")
    mean_motion: float = Field(..., description="Mean motion [rad/s]")

    # Position and velocity at given true anomaly
    radius: float = Field(..., description="Orbital radius at true anomaly [km]")
    velocity: float = Field(..., description="Orbital velocity at true anomaly [km/s]")

    # Apses
    periapsis_radius: float = Field(..., description="Periapsis radius [km]")
    apoapsis_radius: float = Field(..., description="Apoapsis radius [km]")
    periapsis_altitude: float = Field(..., description="Periapsis altitude above surface [km]")
    apoapsis_altitude: float = Field(..., description="Apoapsis altitude above surface [km]")

    # Velocities at apses
    periapsis_velocity: float = Field(..., description="Velocity at periapsis [km/s]")
    apoapsis_velocity: float = Field(..., description="Velocity at apoapsis [km/s]")

    # Energy and momentum
    specific_orbital_energy: float = Field(..., description="Specific orbital energy [km²/s²]")
    specific_angular_momentum: float = Field(..., description="Specific angular momentum [km²/s]")

    assumptions: list[str] = Field(default_factory=list, description="Assumptions used in calculation")


# =============================================================================
# Relative Motion Schemas (Clohessy-Wiltshire / Hill Equations)
# =============================================================================


class RelativeMotionInput(BaseModel):
    """
    Input parameters for relative motion using Clohessy-Wiltshire equations.
    
    The CW equations describe the motion of a deputy spacecraft relative to
    a chief spacecraft in a circular reference orbit. LVLH frame is used:
    - x: radial (outward)
    - y: in-track (velocity direction)
    - z: cross-track (normal to orbital plane)
    """

    # Chief orbit parameters
    chief_semi_major_axis: float = Field(..., description="Chief orbit semi-major axis [km]", gt=0)
    gravitational_parameter: float = Field(
        398600.4418, description="Gravitational parameter μ [km³/s²]", gt=0
    )

    # Initial relative state (deputy w.r.t. chief in LVLH frame)
    x0: float = Field(..., description="Initial radial position [km]")
    y0: float = Field(..., description="Initial in-track position [km]")
    z0: float = Field(..., description="Initial cross-track position [km]")
    x_dot0: float = Field(..., description="Initial radial velocity [km/s]")
    y_dot0: float = Field(..., description="Initial in-track velocity [km/s]")
    z_dot0: float = Field(..., description="Initial cross-track velocity [km/s]")

    # Propagation time
    propagation_time: float = Field(..., description="Time to propagate [s]", ge=0)


class RelativeMotionOutput(BaseModel):
    """Output from relative motion calculation."""

    # Final relative state
    x: float = Field(..., description="Final radial position [km]")
    y: float = Field(..., description="Final in-track position [km]")
    z: float = Field(..., description="Final cross-track position [km]")
    x_dot: float = Field(..., description="Final radial velocity [km/s]")
    y_dot: float = Field(..., description="Final in-track velocity [km/s]")
    z_dot: float = Field(..., description="Final cross-track velocity [km/s]")

    # Derived quantities
    range_magnitude: float = Field(..., description="Range from chief to deputy [km]")
    range_rate: float = Field(..., description="Range rate [km/s]")
    mean_motion: float = Field(..., description="Mean motion of chief orbit [rad/s]")

    # Trajectory characterization
    is_bounded: bool = Field(..., description="Whether relative motion is bounded (no drift)")
    drift_rate: float = Field(..., description="Secular drift rate in y-direction [km/orbit]")

    assumptions: list[str] = Field(default_factory=list, description="Assumptions used in calculation")
