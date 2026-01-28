import {
  AttitudeDynamicsCard,
  OrbitalMotionCard,
  QuaternionAttitudeCard,
  RelativeMotionCard,
} from '../components/cards';
import styles from './Dashboard.module.css';

/**
 * Dashboard - Main application view
 * 
 * The Dashboard presents all available GNC calculation cards in a
 * responsive grid layout. Each card is self-contained with its own
 * inputs, calculation logic, and result display.
 * 
 * Design Philosophy:
 * "An aerospace engineer's digital scratchpad, but clean and modern."
 * 
 * The layout uses generous spacing and a subtle engineering-paper
 * background to create a professional, technical aesthetic.
 */
export default function Dashboard() {
  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <svg
              className={styles.logoIcon}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M13 7 9 3 5 7l4 4" />
              <path d="m17 11 4 4-4 4-4-4" />
              <path d="m8 12 4 4 6-6-4-4Z" />
              <path d="m16 8 3-3" />
              <path d="M9 21a6 6 0 0 0-6-6" />
            </svg>
            <div className={styles.logoText}>
              <h1>GNC Calculations</h1>
              <span className={styles.tagline}>Spacecraft Engineering Tools</span>
            </div>
          </div>
          <nav className={styles.nav}>
            <span className={styles.version}>v0.1.0</span>
          </nav>
        </div>
      </header>

      <main className={styles.main}>
        <section className={styles.intro}>
          <h2>Engineering Calculation Cards</h2>
          <p>
            Professional-grade Guidance, Navigation, and Control calculations for
            spacecraft engineering. Each card below represents a self-contained
            calculation module with documented equations and assumptions.
          </p>
        </section>

        <div className={styles.cardGrid}>
          <AttitudeDynamicsCard />
          <QuaternionAttitudeCard />
          <OrbitalMotionCard />
          <RelativeMotionCard />
        </div>
      </main>

      <footer className={styles.footer}>
        <p>
          GNC Calculations — Built for aerospace engineers who need reliable,
          transparent calculations.
        </p>
        <p className={styles.footerNote}>
          All calculations include documented assumptions. Results should be
          validated against mission-specific requirements.
        </p>
      </footer>
    </div>
  );
}
