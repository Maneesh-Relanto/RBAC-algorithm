import React from 'react';
import Layout from '@theme/Layout';
import RBACPlayground from '@site/src/components/RBACPlayground';
import styles from './playground.module.css';

export default function Playground() {
  return (
    <Layout
      title="Interactive Playground"
      description="Try RBAC Algorithm in your browser with live code examples">
      <div className={styles.playgroundContainer}>
        <div className={styles.header}>
          <img src="/img/logo.svg" alt="RBAC Algorithm" className={styles.logo} />
          <div>
            <h1>Interactive Playground</h1>
            <p>Experiment with RBAC concepts in real-time. Try the examples below or write your own code!</p>
          </div>
        </div>
        <RBACPlayground />
      </div>
    </Layout>
  );
}
