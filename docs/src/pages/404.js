import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './404.module.css';

export default function NotFound() {
  return (
    <Layout title="Page Not Found">
      <div className={styles.notFoundContainer}>
        <img src={useBaseUrl('/img/logo.svg')} alt="RBAC Algorithm Logo" className={styles.logo} />
        <h1 className={styles.title}>404</h1>
        <h2 className={styles.subtitle}>Access Denied... Just Kidding!</h2>
        <p className={styles.message}>
          The page you're looking for doesn't exist. Even our RBAC system couldn't authorize this route.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--primary button--lg"
            to="/">
            ← Back to Home
          </Link>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro"
            style={{marginLeft: '1rem'}}>
            View Documentation
          </Link>
        </div>
      </div>
    </Layout>
  );
}
