"""
GNC API Router - Guidance, Navigation, and Control Endpoints

This router provides HTTP endpoints for GNC calculations. Each endpoint
delegates to the corresponding service module for computation.

All calculations are stateless and deterministic - given the same inputs,
the outputs will always be identical. This design supports:
    - Easy testing and validation
    - Caching of results
    - Future agent/tool integration
"""

from fastapi import APIRouter, HTTPException

from app.schemas.gnc import (
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
)
from app.services.gnc.attitude_dynamics import compute_attitude_dynamics
from app.services.gnc.orbital_dynamics import compute_orbital_dynamics
from app.services.gnc.quaternion import compute_attitude_propagation, compute_quaternion_operations
from app.services.gnc.relative_motion import compute_relative_motion
from app.services.gnc.trajectory import generate_orbital_trajectory, generate_relative_trajectory

router = APIRouter()


@router.post("/attitude", response_model=AttitudeOutput)
async def calculate_attitude_dynamics(inputs: AttitudeInput) -> AttitudeOutput:
    """
    Calculate rigid-body attitude dynamics using Euler's equations.

    Computes instantaneous angular accelerations given the spacecraft's
    inertia properties, current angular velocity, and applied torques.

    Returns angular accelerations and derived quantities including
    rotational kinetic energy and angular momentum magnitude.
    """
    try:
        return compute_attitude_dynamics(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/attitude/quaternion", response_model=QuaternionOutput)
async def calculate_quaternion_operations(inputs: QuaternionInput) -> QuaternionOutput:
    """
    Perform quaternion operations and conversions.

    Takes a quaternion (optionally with angular velocity) and returns:
    - Normalized quaternion
    - Quaternion time derivative (if angular velocity provided)
    - Equivalent Euler angles (3-2-1 sequence)
    - Direction Cosine Matrix (DCM)

    The quaternion convention is scalar-first: q = [q0, q1, q2, q3]
    where q0 is the scalar part and [q1, q2, q3] is the vector part.
    """
    try:
        return compute_quaternion_operations(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/attitude/propagate", response_model=AttitudePropagationOutput)
async def propagate_attitude(inputs: AttitudePropagationInput) -> AttitudePropagationOutput:
    """
    Propagate spacecraft attitude over time.

    Integrates both quaternion kinematics and Euler's rotational dynamics
    using 4th-order Runge-Kutta (RK4) integration.

    Returns a time history of:
    - Quaternion attitude state
    - Angular velocity
    - Euler angles (for visualization)
    - Rotational kinetic energy
    - Angular momentum magnitude

    For torque-free motion, also reports conservation errors to assess
    integration accuracy.
    """
    try:
        return compute_attitude_propagation(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Propagation error: {str(e)}")


@router.post("/orbit", response_model=OrbitalOutput)
async def calculate_orbital_dynamics(inputs: OrbitalInput) -> OrbitalOutput:
    """
    Calculate two-body orbital dynamics from classical orbital elements.
    
    Computes orbital parameters including period, velocities at apses,
    and specific mechanical quantities (energy, angular momentum).
    
    Position and velocity at a specific true anomaly can be computed
    by providing that angle in the input.
    """
    try:
        return compute_orbital_dynamics(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/relative", response_model=RelativeMotionOutput)
async def calculate_relative_motion(inputs: RelativeMotionInput) -> RelativeMotionOutput:
    """
    Calculate relative motion using Clohessy-Wiltshire equations.
    
    Propagates the relative state of a deputy spacecraft with respect to
    a chief spacecraft in a circular orbit. Uses the closed-form solution
    to the linearized equations of relative motion.
    
    Returns the propagated state, range/range-rate, and drift analysis.
    """
    try:
        return compute_relative_motion(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


# =============================================================================
# Trajectory Visualization Endpoints
# =============================================================================


@router.post("/orbit/trajectory", response_model=OrbitalTrajectoryOutput)
async def get_orbital_trajectory(inputs: OrbitalTrajectoryInput) -> OrbitalTrajectoryOutput:
    """
    Generate trajectory points for orbital visualization.
    
    Returns an array of (x, y) points tracing the orbit in the orbital plane,
    along with geometric parameters for plotting the central body.
    """
    try:
        return generate_orbital_trajectory(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trajectory generation error: {str(e)}")


@router.post("/relative/trajectory", response_model=RelativeTrajectoryOutput)
async def get_relative_trajectory(inputs: RelativeTrajectoryInput) -> RelativeTrajectoryOutput:
    """
    Generate trajectory points for relative motion visualization.
    
    Returns an array of (x, y, z) points in the LVLH frame showing the
    deputy's path relative to the chief spacecraft over multiple orbits.
    """
    try:
        return generate_relative_trajectory(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trajectory generation error: {str(e)}")
