import React from 'react';
import Footer from '@theme-original/Footer';
import useBaseUrl from '@docusaurus/useBaseUrl';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

export default function FooterWrapper(props) {
  return (
    <>
      <div className={styles.customFooterBanner}>
        <div className={styles.container}>
          <img src={useBaseUrl('/img/logo.svg')} alt="RBAC Algorithm" className={styles.footerLogo} />
          <div className={styles.footerContent}>
            <h3>Ready to Implement Enterprise-Grade Access Control?</h3>
            <p>Get started with RBAC Algorithm in minutes with our comprehensive documentation and examples.</p>
            <div className={styles.footerButtons}>
              <a href="/docs/getting-started/installation" className="button button--primary button--lg">
                Get Started →
              </a>
              <a href="https://github.com/your-org/rbac-algorithm" className="button button--outline button--secondary button--lg" style={{marginLeft: '1rem'}}>
                ⭐ Star on GitHub
              </a>
            </div>
          </div>
        </div>
      </div>
      <Footer {...props} />
    </>
  );
}
