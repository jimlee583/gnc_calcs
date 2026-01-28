"""
Quaternion Attitude Representation and Kinematics

This module implements quaternion-based attitude representation for spacecraft
orientation tracking. Quaternions provide a singularity-free representation
of rotations, unlike Euler angles which suffer from gimbal lock.

Quaternion Convention:
    q = [q0, q1, q2, q3] = [q_scalar, q_vector]
    where q0 is the scalar part and [q1, q2, q3] is the vector part.

    Unit quaternion constraint: q0² + q1² + q2² + q3² = 1

Quaternion Kinematics:
    q̇ = (1/2) * Ω(ω) * q

    where Ω(ω) is the angular velocity matrix:
    Ω(ω) = | 0   -ωx  -ωy  -ωz |
           | ωx   0    ωz  -ωy |
           | ωy  -ωz   0    ωx |
           | ωz   ωy  -ωx   0  |

Frame Definitions:
    - Body frame: Fixed to spacecraft, origin at center of mass
    - Inertial frame: Non-rotating reference frame
    - The quaternion q represents rotation from inertial to body frame

References:
    - Wertz, "Spacecraft Attitude Determination and Control"
    - Markley & Crassidis, "Fundamentals of Spacecraft Attitude Determination and Control"
"""

import numpy as np

from app.schemas.gnc import (
    AttitudeInput,
    AttitudePropagationInput,
    AttitudePropagationOutput,
    AttitudeStatePoint,
    EulerAngles,
    QuaternionInput,
    QuaternionOutput,
)


def normalize_quaternion(q: np.ndarray) -> np.ndarray:
    """
    Normalize a quaternion to unit magnitude.

    Args:
        q: Quaternion array [q0, q1, q2, q3]

    Returns:
        Normalized quaternion with |q| = 1
    """
    norm = np.linalg.norm(q)
    if norm < 1e-10:
        # Return identity quaternion if input is near zero
        return np.array([1.0, 0.0, 0.0, 0.0])
    return q / norm


def quaternion_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """
    Multiply two quaternions: q_result = q1 ⊗ q2

    This represents the composition of rotations: first q2, then q1.

    Args:
        q1: First quaternion [q0, q1, q2, q3]
        q2: Second quaternion [q0, q1, q2, q3]

    Returns:
        Product quaternion q1 ⊗ q2
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    ])


def quaternion_conjugate(q: np.ndarray) -> np.ndarray:
    """
    Compute the conjugate of a quaternion.

    For unit quaternions, the conjugate equals the inverse and represents
    the opposite rotation.

    Args:
        q: Quaternion [q0, q1, q2, q3]

    Returns:
        Conjugate quaternion [q0, -q1, -q2, -q3]
    """
    return np.array([q[0], -q[1], -q[2], -q[3]])


def quaternion_inverse(q: np.ndarray) -> np.ndarray:
    """
    Compute the inverse of a quaternion.

    For unit quaternions: q⁻¹ = q*
    For non-unit quaternions: q⁻¹ = q* / |q|²

    Args:
        q: Quaternion [q0, q1, q2, q3]

    Returns:
        Inverse quaternion
    """
    conj = quaternion_conjugate(q)
    norm_sq = np.dot(q, q)
    if norm_sq < 1e-10:
        return np.array([1.0, 0.0, 0.0, 0.0])
    return conj / norm_sq


def quaternion_to_dcm(q: np.ndarray) -> np.ndarray:
    """
    Convert quaternion to Direction Cosine Matrix (rotation matrix).

    The DCM transforms vectors from inertial to body frame:
    v_body = C * v_inertial

    Args:
        q: Unit quaternion [q0, q1, q2, q3]

    Returns:
        3x3 rotation matrix (DCM)
    """
    q = normalize_quaternion(q)
    q0, q1, q2, q3 = q

    # DCM elements
    C = np.array([
        [q0**2 + q1**2 - q2**2 - q3**2,  2*(q1*q2 + q0*q3),              2*(q1*q3 - q0*q2)],
        [2*(q1*q2 - q0*q3),              q0**2 - q1**2 + q2**2 - q3**2,  2*(q2*q3 + q0*q1)],
        [2*(q1*q3 + q0*q2),              2*(q2*q3 - q0*q1),              q0**2 - q1**2 - q2**2 + q3**2],
    ])

    return C


def dcm_to_quaternion(C: np.ndarray) -> np.ndarray:
    """
    Convert Direction Cosine Matrix to quaternion using Shepperd's method.

    This method is numerically stable for all rotation angles.

    Args:
        C: 3x3 rotation matrix (DCM)

    Returns:
        Unit quaternion [q0, q1, q2, q3]
    """
    trace = np.trace(C)

    # Shepperd's method: choose largest component for numerical stability
    q = np.zeros(4)

    if trace > 0:
        s = 2.0 * np.sqrt(1.0 + trace)
        q[0] = 0.25 * s
        q[1] = (C[1, 2] - C[2, 1]) / s
        q[2] = (C[2, 0] - C[0, 2]) / s
        q[3] = (C[0, 1] - C[1, 0]) / s
    elif C[0, 0] > C[1, 1] and C[0, 0] > C[2, 2]:
        s = 2.0 * np.sqrt(1.0 + C[0, 0] - C[1, 1] - C[2, 2])
        q[0] = (C[1, 2] - C[2, 1]) / s
        q[1] = 0.25 * s
        q[2] = (C[0, 1] + C[1, 0]) / s
        q[3] = (C[0, 2] + C[2, 0]) / s
    elif C[1, 1] > C[2, 2]:
        s = 2.0 * np.sqrt(1.0 + C[1, 1] - C[0, 0] - C[2, 2])
        q[0] = (C[2, 0] - C[0, 2]) / s
        q[1] = (C[0, 1] + C[1, 0]) / s
        q[2] = 0.25 * s
        q[3] = (C[1, 2] + C[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + C[2, 2] - C[0, 0] - C[1, 1])
        q[0] = (C[0, 1] - C[1, 0]) / s
        q[1] = (C[0, 2] + C[2, 0]) / s
        q[2] = (C[1, 2] + C[2, 1]) / s
        q[3] = 0.25 * s

    # Ensure positive scalar part (quaternion uniqueness)
    if q[0] < 0:
        q = -q

    return normalize_quaternion(q)


def quaternion_to_euler(q: np.ndarray, sequence: str = "321") -> np.ndarray:
    """
    Convert quaternion to Euler angles.

    Default sequence is 3-2-1 (yaw-pitch-roll), common in aerospace.

    Args:
        q: Unit quaternion [q0, q1, q2, q3]
        sequence: Euler angle sequence (currently only "321" supported)

    Returns:
        Euler angles [roll, pitch, yaw] in radians
        - roll (φ): rotation about body X-axis
        - pitch (θ): rotation about body Y-axis
        - yaw (ψ): rotation about body Z-axis
    """
    q = normalize_quaternion(q)
    q0, q1, q2, q3 = q

    if sequence == "321":
        # 3-2-1 Euler angles (yaw-pitch-roll)
        # Roll (φ)
        roll = np.arctan2(2*(q0*q1 + q2*q3), 1 - 2*(q1**2 + q2**2))

        # Pitch (θ) - handle gimbal lock
        sin_pitch = 2*(q0*q2 - q3*q1)
        sin_pitch = np.clip(sin_pitch, -1.0, 1.0)  # Numerical safety
        pitch = np.arcsin(sin_pitch)

        # Yaw (ψ)
        yaw = np.arctan2(2*(q0*q3 + q1*q2), 1 - 2*(q2**2 + q3**2))

        return np.array([roll, pitch, yaw])
    else:
        raise ValueError(f"Euler sequence '{sequence}' not supported. Use '321'.")


def euler_to_quaternion(roll: float, pitch: float, yaw: float, sequence: str = "321") -> np.ndarray:
    """
    Convert Euler angles to quaternion.

    Args:
        roll: Rotation about X-axis [rad]
        pitch: Rotation about Y-axis [rad]
        yaw: Rotation about Z-axis [rad]
        sequence: Euler angle sequence (currently only "321" supported)

    Returns:
        Unit quaternion [q0, q1, q2, q3]
    """
    if sequence != "321":
        raise ValueError(f"Euler sequence '{sequence}' not supported. Use '321'.")

    # Half angles
    cr = np.cos(roll / 2)
    sr = np.sin(roll / 2)
    cp = np.cos(pitch / 2)
    sp = np.sin(pitch / 2)
    cy = np.cos(yaw / 2)
    sy = np.sin(yaw / 2)

    # 3-2-1 sequence: yaw * pitch * roll
    q0 = cr * cp * cy + sr * sp * sy
    q1 = sr * cp * cy - cr * sp * sy
    q2 = cr * sp * cy + sr * cp * sy
    q3 = cr * cp * sy - sr * sp * cy

    return normalize_quaternion(np.array([q0, q1, q2, q3]))


def quaternion_derivative(q: np.ndarray, omega: np.ndarray) -> np.ndarray:
    """
    Compute quaternion time derivative from angular velocity.

    Kinematic equation: q̇ = (1/2) * q ⊗ ω_quat
    where ω_quat = [0, ωx, ωy, ωz]

    Args:
        q: Current quaternion [q0, q1, q2, q3]
        omega: Angular velocity in body frame [ωx, ωy, ωz] [rad/s]

    Returns:
        Quaternion derivative [q̇0, q̇1, q̇2, q̇3]
    """
    # Form omega quaternion (pure quaternion with zero scalar)
    omega_quat = np.array([0.0, omega[0], omega[1], omega[2]])

    # q̇ = (1/2) * q ⊗ ω_quat
    q_dot = 0.5 * quaternion_multiply(q, omega_quat)

    return q_dot


def rotate_vector_by_quaternion(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Rotate a vector using a quaternion.

    v_rotated = q ⊗ v ⊗ q*

    This transforms v from the inertial frame to the body frame.

    Args:
        q: Unit quaternion [q0, q1, q2, q3]
        v: Vector to rotate [vx, vy, vz]

    Returns:
        Rotated vector [vx', vy', vz']
    """
    # Form pure quaternion from vector
    v_quat = np.array([0.0, v[0], v[1], v[2]])

    # Rotate: q ⊗ v ⊗ q*
    q_conj = quaternion_conjugate(q)
    result = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)

    # Extract vector part
    return result[1:4]


def propagate_attitude_rk4(
    q0: np.ndarray,
    omega0: np.ndarray,
    inertia: np.ndarray,
    torque: np.ndarray,
    dt: float,
    num_steps: int,
) -> tuple[list[np.ndarray], list[np.ndarray], list[float]]:
    """
    Propagate attitude using 4th-order Runge-Kutta integration.

    Integrates both quaternion kinematics and Euler's equations simultaneously.

    Args:
        q0: Initial quaternion [q0, q1, q2, q3]
        omega0: Initial angular velocity [ωx, ωy, ωz] [rad/s]
        inertia: Principal moments of inertia [Ix, Iy, Iz] [kg·m²]
        torque: Applied torque (constant) [Mx, My, Mz] [N·m]
        dt: Time step [s]
        num_steps: Number of integration steps

    Returns:
        Tuple of (quaternion_history, omega_history, time_history)
    """
    Ix, Iy, Iz = inertia
    Mx, My, Mz = torque

    def euler_derivative(omega: np.ndarray) -> np.ndarray:
        """Compute angular acceleration from Euler's equations."""
        wx, wy, wz = omega
        return np.array([
            ((Iy - Iz) * wy * wz + Mx) / Ix,
            ((Iz - Ix) * wz * wx + My) / Iy,
            ((Ix - Iy) * wx * wy + Mz) / Iz,
        ])

    def state_derivative(q: np.ndarray, omega: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Compute derivatives for both quaternion and angular velocity."""
        q_dot = quaternion_derivative(q, omega)
        omega_dot = euler_derivative(omega)
        return q_dot, omega_dot

    # Initialize
    q = normalize_quaternion(q0.copy())
    omega = omega0.copy()

    q_history = [q.copy()]
    omega_history = [omega.copy()]
    t_history = [0.0]

    # RK4 integration
    for step in range(num_steps):
        # k1
        k1_q, k1_w = state_derivative(q, omega)

        # k2
        q_mid1 = normalize_quaternion(q + 0.5 * dt * k1_q)
        w_mid1 = omega + 0.5 * dt * k1_w
        k2_q, k2_w = state_derivative(q_mid1, w_mid1)

        # k3
        q_mid2 = normalize_quaternion(q + 0.5 * dt * k2_q)
        w_mid2 = omega + 0.5 * dt * k2_w
        k3_q, k3_w = state_derivative(q_mid2, w_mid2)

        # k4
        q_end = normalize_quaternion(q + dt * k3_q)
        w_end = omega + dt * k3_w
        k4_q, k4_w = state_derivative(q_end, w_end)

        # Update state
        q = q + (dt / 6.0) * (k1_q + 2*k2_q + 2*k3_q + k4_q)
        omega = omega + (dt / 6.0) * (k1_w + 2*k2_w + 2*k3_w + k4_w)

        # Normalize quaternion to maintain unit constraint
        q = normalize_quaternion(q)

        # Store history
        q_history.append(q.copy())
        omega_history.append(omega.copy())
        t_history.append((step + 1) * dt)

    return q_history, omega_history, t_history


# =============================================================================
# Service Functions (called by API endpoints)
# =============================================================================


def compute_quaternion_operations(inputs: QuaternionInput) -> QuaternionOutput:
    """
    Perform quaternion operations and compute derivatives.

    Args:
        inputs: QuaternionInput with quaternion and angular velocity

    Returns:
        QuaternionOutput with normalized quaternion, derivative, and conversions
    """
    # Extract quaternion
    q = np.array([inputs.q0, inputs.q1, inputs.q2, inputs.q3])

    # Normalize
    q_norm = normalize_quaternion(q)

    # Compute derivative if angular velocity provided
    if inputs.omega_x is not None:
        omega = np.array([inputs.omega_x, inputs.omega_y, inputs.omega_z])
        q_dot = quaternion_derivative(q_norm, omega)
    else:
        omega = np.array([0.0, 0.0, 0.0])
        q_dot = np.array([0.0, 0.0, 0.0, 0.0])

    # Convert to Euler angles
    euler = quaternion_to_euler(q_norm)
    euler_deg = np.degrees(euler)

    # Convert to DCM (flatten for JSON serialization)
    dcm = quaternion_to_dcm(q_norm)

    # Compute quaternion magnitude (should be 1 for normalized)
    magnitude = np.linalg.norm(q)

    assumptions = [
        "Hamilton quaternion convention (scalar-first)",
        "Right-handed coordinate system",
        "Quaternion represents rotation from inertial to body frame",
        "3-2-1 Euler sequence (yaw-pitch-roll)",
    ]

    return QuaternionOutput(
        # Normalized quaternion
        q0=float(q_norm[0]),
        q1=float(q_norm[1]),
        q2=float(q_norm[2]),
        q3=float(q_norm[3]),
        # Quaternion derivative
        q0_dot=float(q_dot[0]),
        q1_dot=float(q_dot[1]),
        q2_dot=float(q_dot[2]),
        q3_dot=float(q_dot[3]),
        # Euler angles
        euler_angles=EulerAngles(
            roll_rad=float(euler[0]),
            pitch_rad=float(euler[1]),
            yaw_rad=float(euler[2]),
            roll_deg=float(euler_deg[0]),
            pitch_deg=float(euler_deg[1]),
            yaw_deg=float(euler_deg[2]),
        ),
        # DCM (flattened row-major)
        dcm=[float(x) for x in dcm.flatten()],
        # Magnitude
        magnitude=float(magnitude),
        is_normalized=bool(abs(magnitude - 1.0) < 1e-6),
        assumptions=assumptions,
    )


def compute_attitude_propagation(inputs: AttitudePropagationInput) -> AttitudePropagationOutput:
    """
    Propagate attitude state over time using RK4 integration.

    Integrates both quaternion kinematics and Euler's rotational dynamics.

    Args:
        inputs: AttitudePropagationInput with initial state and spacecraft parameters

    Returns:
        AttitudePropagationOutput with time history of attitude state
    """
    # Extract initial conditions
    q0 = np.array([inputs.q0, inputs.q1, inputs.q2, inputs.q3])
    q0 = normalize_quaternion(q0)

    omega0 = np.array([inputs.omega_x, inputs.omega_y, inputs.omega_z])
    inertia = np.array([inputs.inertia_x, inputs.inertia_y, inputs.inertia_z])
    torque = np.array([inputs.torque_x, inputs.torque_y, inputs.torque_z])

    # Compute time step
    dt = inputs.propagation_time / inputs.num_steps

    # Propagate
    q_history, omega_history, t_history = propagate_attitude_rk4(
        q0, omega0, inertia, torque, dt, inputs.num_steps
    )

    # Build output state points
    states: list[AttitudeStatePoint] = []

    for i, (q, omega, t) in enumerate(zip(q_history, omega_history, t_history)):
        # Convert to Euler angles
        euler = quaternion_to_euler(q)

        # Compute energy and momentum
        rotational_ke = 0.5 * np.sum(inertia * omega**2)
        H = inertia * omega
        angular_momentum = np.linalg.norm(H)

        states.append(AttitudeStatePoint(
            t=float(t),
            q0=float(q[0]),
            q1=float(q[1]),
            q2=float(q[2]),
            q3=float(q[3]),
            omega_x=float(omega[0]),
            omega_y=float(omega[1]),
            omega_z=float(omega[2]),
            roll_deg=float(np.degrees(euler[0])),
            pitch_deg=float(np.degrees(euler[1])),
            yaw_deg=float(np.degrees(euler[2])),
            rotational_kinetic_energy=float(rotational_ke),
            angular_momentum_magnitude=float(angular_momentum),
        ))

    # Check conservation (compare initial and final)
    initial_ke = states[0].rotational_kinetic_energy
    final_ke = states[-1].rotational_kinetic_energy
    initial_H = states[0].angular_momentum_magnitude
    final_H = states[-1].angular_momentum_magnitude

    # For torque-free motion, energy and momentum should be conserved
    is_torque_free = np.allclose(torque, 0)
    energy_drift = abs(final_ke - initial_ke) / max(initial_ke, 1e-10) if is_torque_free else None
    momentum_drift = abs(final_H - initial_H) / max(initial_H, 1e-10) if is_torque_free else None

    assumptions = [
        "Rigid body dynamics (Euler's equations)",
        "Principal axes aligned with body frame",
        "4th-order Runge-Kutta integration",
        "Quaternion normalization at each step",
        "Constant applied torque",
    ]

    return AttitudePropagationOutput(
        states=states,
        time_step=float(dt),
        integration_method="RK4",
        energy_conservation_error=float(energy_drift) if energy_drift is not None else None,
        momentum_conservation_error=float(momentum_drift) if momentum_drift is not None else None,
        assumptions=assumptions,
    )
