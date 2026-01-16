import { useState } from 'react';
import { calculateAttitude } from '../../api/gnc';
import type { AttitudeInput, AttitudeOutput } from '../../api/types';
import {
  GncCard,
  CardSection,
  CardInput,
  CardOutput,
  CardButton,
} from './GncCard';
import styles from './CalculationCard.module.css';

/**
 * AttitudeDynamicsCard - Euler's Equations of Rotational Motion
 * 
 * This card computes instantaneous angular accelerations for a rigid body
 * given its inertia properties, angular velocity state, and applied torques.
 * 
 * Governing Equations (Euler's Equations):
 *   I_x * ω̇_x = (I_y - I_z) * ω_y * ω_z + M_x
 *   I_y * ω̇_y = (I_z - I_x) * ω_z * ω_x + M_y
 *   I_z * ω̇_z = (I_x - I_y) * ω_x * ω_y + M_z
 * 
 * TODO: Add quaternion attitude representation
 * TODO: Add gravity gradient torque model
 * TODO: Add reaction wheel momentum management
 */
export function AttitudeDynamicsCard() {
  // Input state - typical small satellite values as defaults
  const [inputs, setInputs] = useState<AttitudeInput>({
    inertia_x: 100,      // kg·m²
    inertia_y: 150,      // kg·m²
    inertia_z: 200,      // kg·m²
    omega_x: 0.01,       // rad/s
    omega_y: 0.005,      // rad/s
    omega_z: 0.002,      // rad/s
    torque_x: 0,         // N·m
    torque_y: 0,         // N·m
    torque_z: 0,         // N·m
  });

  const [result, setResult] = useState<AttitudeOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateInput = <K extends keyof AttitudeInput>(
    key: K,
    value: AttitudeInput[K]
  ) => {
    setInputs((prev) => ({ ...prev, [key]: value }));
  };

  const handleCalculate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const output = await calculateAttitude(inputs);
      setResult(output);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <GncCard
      title="Attitude Dynamics"
      subtitle="Euler's equations for rigid-body rotational motion"
      category="Attitude"
      isLoading={isLoading}
      error={error}
    >
      <div className={styles.layout}>
        <div className={styles.inputPanel}>
          <CardSection title="Principal Moments of Inertia">
            <CardInput
              label="I_x"
              unit="kg·m²"
              value={inputs.inertia_x}
              onChange={(v) => updateInput('inertia_x', v)}
              min={0.001}
            />
            <CardInput
              label="I_y"
              unit="kg·m²"
              value={inputs.inertia_y}
              onChange={(v) => updateInput('inertia_y', v)}
              min={0.001}
            />
            <CardInput
              label="I_z"
              unit="kg·m²"
              value={inputs.inertia_z}
              onChange={(v) => updateInput('inertia_z', v)}
              min={0.001}
            />
          </CardSection>

          <CardSection title="Angular Velocities">
            <CardInput
              label="ω_x"
              unit="rad/s"
              value={inputs.omega_x}
              onChange={(v) => updateInput('omega_x', v)}
            />
            <CardInput
              label="ω_y"
              unit="rad/s"
              value={inputs.omega_y}
              onChange={(v) => updateInput('omega_y', v)}
            />
            <CardInput
              label="ω_z"
              unit="rad/s"
              value={inputs.omega_z}
              onChange={(v) => updateInput('omega_z', v)}
            />
          </CardSection>

          <CardSection title="External Torques">
            <CardInput
              label="M_x"
              unit="N·m"
              value={inputs.torque_x ?? 0}
              onChange={(v) => updateInput('torque_x', v)}
            />
            <CardInput
              label="M_y"
              unit="N·m"
              value={inputs.torque_y ?? 0}
              onChange={(v) => updateInput('torque_y', v)}
            />
            <CardInput
              label="M_z"
              unit="N·m"
              value={inputs.torque_z ?? 0}
              onChange={(v) => updateInput('torque_z', v)}
            />
          </CardSection>

          <div className={styles.buttonRow}>
            <CardButton onClick={handleCalculate} disabled={isLoading}>
              Calculate
            </CardButton>
          </div>
        </div>

        {result && (
          <div className={styles.outputPanel}>
            <CardSection title="Angular Accelerations">
              <CardOutput
                label="ω̇_x"
                value={result.omega_dot_x}
                unit="rad/s²"
              />
              <CardOutput
                label="ω̇_y"
                value={result.omega_dot_y}
                unit="rad/s²"
              />
              <CardOutput
                label="ω̇_z"
                value={result.omega_dot_z}
                unit="rad/s²"
              />
            </CardSection>

            <CardSection title="Derived Quantities">
              <CardOutput
                label="Kinetic Energy"
                value={result.rotational_kinetic_energy}
                unit="J"
              />
              <CardOutput
                label="|H|"
                value={result.angular_momentum_magnitude}
                unit="kg·m²/s"
              />
            </CardSection>

            <div className={styles.assumptions}>
              <h5 className={styles.assumptionsTitle}>Assumptions</h5>
              <ul className={styles.assumptionsList}>
                {result.assumptions.map((assumption, i) => (
                  <li key={i}>{assumption}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </GncCard>
  );
}
