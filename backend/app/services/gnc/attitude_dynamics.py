"""
Attitude Dynamics Service - Euler's Equations of Rotational Motion

This module implements rigid-body attitude dynamics calculations using
Euler's equations. These equations describe the rotational motion of a
rigid body about its center of mass.

Reference Equations (Principal Axes):
    I_x * ω̇_x = (I_y - I_z) * ω_y * ω_z + M_x
    I_y * ω̇_y = (I_z - I_x) * ω_z * ω_x + M_y
    I_z * ω̇_z = (I_x - I_y) * ω_x * ω_y + M_z

Where:
    I_x, I_y, I_z = Principal moments of inertia [kg·m²]
    ω_x, ω_y, ω_z = Angular velocity components [rad/s]
    M_x, M_y, M_z = External torque components [N·m]
    ω̇_x, ω̇_y, ω̇_z = Angular acceleration components [rad/s²]

Assumptions:
    - Rigid body (no flexure)
    - Principal axes aligned with body frame
    - No products of inertia (diagonal inertia tensor)

See Also:
    - quaternion.py: Quaternion attitude representation and propagation

TODO: Add support for non-principal axis inertia tensors
TODO: Add gravity gradient torque model
"""

import numpy as np

from app.schemas.gnc import AttitudeInput, AttitudeOutput


def compute_attitude_dynamics(inputs: AttitudeInput) -> AttitudeOutput:
    """
    Compute angular accelerations using Euler's equations.
    
    This function solves for the instantaneous angular accelerations
    given the current angular velocity state and applied torques.
    
    Args:
        inputs: AttitudeInput containing inertias, angular velocities, and torques
        
    Returns:
        AttitudeOutput with angular accelerations and derived quantities
    """
    # Extract inputs for readability
    Ix, Iy, Iz = inputs.inertia_x, inputs.inertia_y, inputs.inertia_z
    wx, wy, wz = inputs.omega_x, inputs.omega_y, inputs.omega_z
    Mx, My, Mz = inputs.torque_x, inputs.torque_y, inputs.torque_z

    # Euler's equations solved for angular accelerations
    # ω̇_x = [(I_y - I_z) * ω_y * ω_z + M_x] / I_x
    omega_dot_x = ((Iy - Iz) * wy * wz + Mx) / Ix
    omega_dot_y = ((Iz - Ix) * wz * wx + My) / Iy
    omega_dot_z = ((Ix - Iy) * wx * wy + Mz) / Iz

    # Compute rotational kinetic energy
    # T = (1/2) * (I_x * ω_x² + I_y * ω_y² + I_z * ω_z²)
    rotational_ke = 0.5 * (Ix * wx**2 + Iy * wy**2 + Iz * wz**2)

    # Compute angular momentum vector and magnitude
    # H = [I_x * ω_x, I_y * ω_y, I_z * ω_z]
    Hx, Hy, Hz = Ix * wx, Iy * wy, Iz * wz
    angular_momentum_mag = np.sqrt(Hx**2 + Hy**2 + Hz**2)

    assumptions = [
        "Rigid body assumption (no structural flexure)",
        "Principal axes aligned with body-fixed frame",
        "Diagonal inertia tensor (no products of inertia)",
        "Instantaneous calculation (no time integration)",
    ]

    return AttitudeOutput(
        omega_dot_x=float(omega_dot_x),
        omega_dot_y=float(omega_dot_y),
        omega_dot_z=float(omega_dot_z),
        rotational_kinetic_energy=float(rotational_ke),
        angular_momentum_magnitude=float(angular_momentum_mag),
        assumptions=assumptions,
    )
