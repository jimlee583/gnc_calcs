import { type ReactNode } from 'react';
import styles from './GncCard.module.css';

/**
 * Props for the base GncCard component
 */
interface GncCardProps {
  /** Card title displayed in the header */
  title: string;
  /** Optional subtitle or description */
  subtitle?: string;
  /** Category label (e.g., "Attitude", "Orbital") */
  category?: string;
  /** Card content */
  children: ReactNode;
  /** Whether the card is in a loading state */
  isLoading?: boolean;
  /** Error message to display */
  error?: string | null;
}

/**
 * GncCard - Base component for engineering calculation cards
 * 
 * This component provides the consistent visual structure for all
 * GNC calculation cards. It includes:
 * - Header with title, subtitle, and category badge
 * - Content area for inputs and outputs
 * - Loading and error states
 * 
 * The design follows the "aerospace engineer's digital scratchpad" aesthetic
 * with clean lines, subtle shadows, and a technical feel.
 */
export function GncCard({
  title,
  subtitle,
  category,
  children,
  isLoading = false,
  error = null,
}: GncCardProps) {
  return (
    <article className={styles.card}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          {category && <span className={styles.category}>{category}</span>}
          <h3 className={styles.title}>{title}</h3>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      </header>

      <div className={styles.content}>
        {isLoading && (
          <div className={styles.loadingOverlay}>
            <div className={styles.spinner} />
            <span>Calculating...</span>
          </div>
        )}

        {error && (
          <div className={styles.error}>
            <span className={styles.errorIcon}>!</span>
            <span>{error}</span>
          </div>
        )}

        {children}
      </div>
    </article>
  );
}

/**
 * Section within a GncCard for grouping related content
 */
interface CardSectionProps {
  title: string;
  children: ReactNode;
}

export function CardSection({ title, children }: CardSectionProps) {
  return (
    <section className={styles.section}>
      <h4 className={styles.sectionTitle}>{title}</h4>
      <div className={styles.sectionContent}>{children}</div>
    </section>
  );
}

/**
 * Input field component styled for engineering cards
 */
interface CardInputProps {
  label: string;
  unit: string;
  value: number | string;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
}

export function CardInput({
  label,
  unit,
  value,
  onChange,
  min,
  max,
  step = 0.01,
  placeholder,
}: CardInputProps) {
  return (
    <div className={styles.inputGroup}>
      <label className={styles.inputLabel}>{label}</label>
      <div className={styles.inputWrapper}>
        <input
          type="number"
          className={styles.input}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min}
          max={max}
          step={step}
          placeholder={placeholder}
        />
        <span className={styles.inputUnit}>{unit}</span>
      </div>
    </div>
  );
}

/**
 * Output/result display component styled for engineering cards
 */
interface CardOutputProps {
  label: string;
  value: number | string;
  unit: string;
  precision?: number;
}

export function CardOutput({
  label,
  value,
  unit,
  precision = 4,
}: CardOutputProps) {
  const displayValue = typeof value === 'number' 
    ? value.toExponential(precision)
    : value;

  return (
    <div className={styles.outputGroup}>
      <span className={styles.outputLabel}>{label}</span>
      <span className={styles.outputValue}>
        {displayValue}
        <span className={styles.outputUnit}>{unit}</span>
      </span>
    </div>
  );
}

/**
 * Calculate button for triggering computations
 */
interface CardButtonProps {
  onClick: () => void;
  disabled?: boolean;
  children: ReactNode;
}

export function CardButton({ onClick, disabled, children }: CardButtonProps) {
  return (
    <button
      className={styles.button}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
