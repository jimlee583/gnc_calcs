import { useState } from 'react';
import { calculateQuaternion, propagateAttitude } from '../../api/gnc';
import type {
  QuaternionInput,
  QuaternionOutput,
  AttitudePropagationInput,
  AttitudePropagationOutput,
} from '../../api/types';
import { TrajectoryPlot } from '../TrajectoryPlot';
import {
  GncCard,
  CardSection,
  CardInput,
  CardOutput,
  CardButton,
} from './GncCard';
import styles from './CalculationCard.module.css';
import quaternionStyles from './QuaternionAttitudeCard.module.css';

/**
 * QuaternionAttitudeCard - Quaternion Attitude Operations and Propagation
 *
 * This card provides two main capabilities:
 * 1. Convert Quaternion: Quick conversion to Euler angles and DCM
 * 2. Propagate Attitude: Full time propagation with RK4 integration
 *
 * Quaternion convention: q = [q0, q1, q2, q3] = [scalar, vector]
 * where q0 is the scalar part and [q1, q2, q3] is the vector part.
 */
export function QuaternionAttitudeCard() {
  // Input state - identity quaternion as default
  const [inputs, setInputs] = useState<AttitudePropagationInput>({
    q0: 1.0,
    q1: 0.0,
    q2: 0.0,
    q3: 0.0,
    omega_x: 0.01,
    omega_y: 0.005,
    omega_z: 0.002,
    inertia_x: 100,
    inertia_y: 150,
    inertia_z: 200,
    torque_x: 0,
    torque_y: 0,
    torque_z: 0,
    propagation_time: 100,
    num_steps: 200,
  });

  const [quaternionResult, setQuaternionResult] = useState<QuaternionOutput | null>(null);
  const [propagationResult, setPropagationResult] = useState<AttitudePropagationOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'convert' | 'propagate'>('convert');

  const updateInput = <K extends keyof AttitudePropagationInput>(
    key: K,
    value: AttitudePropagationInput[K]
  ) => {
    setInputs((prev) => ({ ...prev, [key]: value }));
  };

  const handleConvertQuaternion = async () => {
    setIsLoading(true);
    setError(null);
    setActiveTab('convert');
    try {
      const qInput: QuaternionInput = {
        q0: inputs.q0 ?? 1.0,
        q1: inputs.q1 ?? 0.0,
        q2: inputs.q2 ?? 0.0,
        q3: inputs.q3 ?? 0.0,
        omega_x: inputs.omega_x,
        omega_y: inputs.omega_y,
        omega_z: inputs.omega_z,
      };
      const output = await calculateQuaternion(qInput);
      setQuaternionResult(output);
      setPropagationResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Conversion failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePropagateAttitude = async () => {
    setIsLoading(true);
    setError(null);
    setActiveTab('propagate');
    try {
      const output = await propagateAttitude(inputs);
      setPropagationResult(output);
      setQuaternionResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Propagation failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Format DCM as 3x3 matrix
  const formatDCM = (dcm: number[]): string[][] => {
    const rows: string[][] = [];
    for (let i = 0; i < 3; i++) {
      rows.push(dcm.slice(i * 3, i * 3 + 3).map((v) => v.toFixed(6)));
    }
    return rows;
  };

  // Transform propagation states to trajectory points for plotting
  const getEulerTrajectoryPoints = () => {
    if (!propagationResult) return [];
    return propagationResult.states.map((state) => ({
      x: state.t,
      y: state.roll_deg,
      t: state.t,
    }));
  };

  const getPitchTrajectoryPoints = () => {
    if (!propagationResult) return [];
    return propagationResult.states.map((state) => ({
      x: state.t,
      y: state.pitch_deg,
      t: state.t,
    }));
  };

  const getYawTrajectoryPoints = () => {
    if (!propagationResult) return [];
    return propagationResult.states.map((state) => ({
      x: state.t,
      y: state.yaw_deg,
      t: state.t,
    }));
  };

  return (
    <GncCard
      title="Quaternion Attitude"
      subtitle="Quaternion operations, conversions, and attitude propagation"
      category="Attitude"
      isLoading={isLoading}
      error={error}
    >
      <div className={styles.layout}>
        <div className={styles.inputPanel}>
          <CardSection title="Quaternion (Scalar-First)">
            <CardInput
              label="q₀ (w)"
              unit=""
              value={inputs.q0 ?? 1.0}
              onChange={(v) => updateInput('q0', v)}
              step={0.1}
            />
            <CardInput
              label="q₁ (x)"
              unit=""
              value={inputs.q1 ?? 0.0}
              onChange={(v) => updateInput('q1', v)}
              step={0.1}
            />
            <CardInput
              label="q₂ (y)"
              unit=""
              value={inputs.q2 ?? 0.0}
              onChange={(v) => updateInput('q2', v)}
              step={0.1}
            />
            <CardInput
              label="q₃ (z)"
              unit=""
              value={inputs.q3 ?? 0.0}
              onChange={(v) => updateInput('q3', v)}
              step={0.1}
            />
          </CardSection>

          <CardSection title="Angular Velocity">
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

          <CardSection title="Spacecraft Inertia">
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

          <CardSection title="Applied Torque (Optional)">
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

          <CardSection title="Propagation Settings">
            <CardInput
              label="Time"
              unit="s"
              value={inputs.propagation_time}
              onChange={(v) => updateInput('propagation_time', v)}
              min={0.1}
            />
            <CardInput
              label="Steps"
              unit=""
              value={inputs.num_steps ?? 200}
              onChange={(v) => updateInput('num_steps', Math.round(v))}
              min={10}
              max={10000}
              step={10}
            />
          </CardSection>

          <div className={quaternionStyles.buttonRow}>
            <CardButton onClick={handleConvertQuaternion} disabled={isLoading}>
              Convert Quaternion
            </CardButton>
            <CardButton onClick={handlePropagateAttitude} disabled={isLoading}>
              Propagate Attitude
            </CardButton>
          </div>
        </div>

        {(quaternionResult || propagationResult) && (
          <div className={styles.outputPanel}>
            {activeTab === 'convert' && quaternionResult && (
              <>
                <CardSection title="Normalized Quaternion">
                  <CardOutput label="q₀" value={quaternionResult.q0} unit="" precision={6} />
                  <CardOutput label="q₁" value={quaternionResult.q1} unit="" precision={6} />
                  <CardOutput label="q₂" value={quaternionResult.q2} unit="" precision={6} />
                  <CardOutput label="q₃" value={quaternionResult.q3} unit="" precision={6} />
                  <div className={quaternionStyles.statusRow}>
                    <span className={quaternionStyles.statusLabel}>Magnitude:</span>
                    <span className={quaternionResult.is_normalized ? quaternionStyles.statusGood : quaternionStyles.statusWarning}>
                      {quaternionResult.magnitude.toFixed(6)}
                      {quaternionResult.is_normalized ? ' (normalized)' : ' (was renormalized)'}
                    </span>
                  </div>
                </CardSection>

                <CardSection title="Euler Angles (3-2-1)">
                  <CardOutput
                    label="Roll (φ)"
                    value={quaternionResult.euler_angles.roll_deg}
                    unit="deg"
                    precision={4}
                  />
                  <CardOutput
                    label="Pitch (θ)"
                    value={quaternionResult.euler_angles.pitch_deg}
                    unit="deg"
                    precision={4}
                  />
                  <CardOutput
                    label="Yaw (ψ)"
                    value={quaternionResult.euler_angles.yaw_deg}
                    unit="deg"
                    precision={4}
                  />
                </CardSection>

                <CardSection title="Direction Cosine Matrix">
                  <div className={quaternionStyles.dcmMatrix}>
                    {formatDCM(quaternionResult.dcm).map((row, i) => (
                      <div key={i} className={quaternionStyles.dcmRow}>
                        {row.map((val, j) => (
                          <span key={j} className={quaternionStyles.dcmCell}>
                            {val}
                          </span>
                        ))}
                      </div>
                    ))}
                  </div>
                </CardSection>

                <div className={styles.assumptions}>
                  <h5 className={styles.assumptionsTitle}>Conventions</h5>
                  <ul className={styles.assumptionsList}>
                    {quaternionResult.assumptions.map((assumption, i) => (
                      <li key={i}>{assumption}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}

            {activeTab === 'propagate' && propagationResult && (
              <>
                <CardSection title="Final State">
                  <CardOutput
                    label="Roll"
                    value={propagationResult.states[propagationResult.states.length - 1].roll_deg}
                    unit="deg"
                    precision={4}
                  />
                  <CardOutput
                    label="Pitch"
                    value={propagationResult.states[propagationResult.states.length - 1].pitch_deg}
                    unit="deg"
                    precision={4}
                  />
                  <CardOutput
                    label="Yaw"
                    value={propagationResult.states[propagationResult.states.length - 1].yaw_deg}
                    unit="deg"
                    precision={4}
                  />
                </CardSection>

                {(propagationResult.energy_conservation_error !== null ||
                  propagationResult.momentum_conservation_error !== null) && (
                  <CardSection title="Conservation Errors">
                    {propagationResult.energy_conservation_error !== null && (
                      <div className={quaternionStyles.statusRow}>
                        <span className={quaternionStyles.statusLabel}>Energy Error:</span>
                        <span
                          className={
                            Math.abs(propagationResult.energy_conservation_error) < 1e-6
                              ? quaternionStyles.statusGood
                              : quaternionStyles.statusWarning
                          }
                        >
                          {propagationResult.energy_conservation_error.toExponential(4)}
                        </span>
                      </div>
                    )}
                    {propagationResult.momentum_conservation_error !== null && (
                      <div className={quaternionStyles.statusRow}>
                        <span className={quaternionStyles.statusLabel}>Momentum Error:</span>
                        <span
                          className={
                            Math.abs(propagationResult.momentum_conservation_error) < 1e-6
                              ? quaternionStyles.statusGood
                              : quaternionStyles.statusWarning
                          }
                        >
                          {propagationResult.momentum_conservation_error.toExponential(4)}
                        </span>
                      </div>
                    )}
                  </CardSection>
                )}

                <CardSection title="Euler Angle Time History">
                  <div className={quaternionStyles.plotGrid}>
                    <TrajectoryPlot
                      points={getEulerTrajectoryPoints()}
                      width={280}
                      height={180}
                      title="Roll"
                      xLabel="Time [s]"
                      yLabel="Roll [deg]"
                      showOrigin={false}
                      showEndpoints={false}
                      lineColor="#3B82F6"
                    />
                    <TrajectoryPlot
                      points={getPitchTrajectoryPoints()}
                      width={280}
                      height={180}
                      title="Pitch"
                      xLabel="Time [s]"
                      yLabel="Pitch [deg]"
                      showOrigin={false}
                      showEndpoints={false}
                      lineColor="#10B981"
                    />
                    <TrajectoryPlot
                      points={getYawTrajectoryPoints()}
                      width={280}
                      height={180}
                      title="Yaw"
                      xLabel="Time [s]"
                      yLabel="Yaw [deg]"
                      showOrigin={false}
                      showEndpoints={false}
                      lineColor="#F59E0B"
                    />
                  </div>
                </CardSection>

                <div className={styles.assumptions}>
                  <h5 className={styles.assumptionsTitle}>Assumptions</h5>
                  <ul className={styles.assumptionsList}>
                    {propagationResult.assumptions.map((assumption, i) => (
                      <li key={i}>{assumption}</li>
                    ))}
                    <li>Integration method: {propagationResult.integration_method}</li>
                    <li>Time step: {propagationResult.time_step.toFixed(4)} s</li>
                  </ul>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </GncCard>
  );
}
