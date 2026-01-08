import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Simple & Intuitive',
    icon: '🎯',
    description: (
      <>
        Clean, well-documented API that follows industry standards.
        Get started in minutes with comprehensive guides and examples.
      </>
    ),
  },
  {
    title: 'Enterprise-Grade',
    icon: '🏢',
    description: (
      <>
        Built for production with multi-tenancy, audit logging, and
        performance optimizations. Scales from startups to enterprises.
      </>
    ),
  },
  {
    title: 'Language Agnostic',
    icon: '🌐',
    description: (
      <>
        Protocol-based architecture with adapters for Python, JavaScript,
        Go, Java, C#, and more. Use the same concepts across your stack.
      </>
    ),
  },
  {
    title: 'ABAC Support',
    icon: '🔐',
    description: (
      <>
        Powerful attribute-based access control with conditions, operators,
        and dynamic evaluation. Fine-grained permissions made easy.
      </>
    ),
  },
  {
    title: 'Role Hierarchies',
    icon: '📊',
    description: (
      <>
        Build complex organizational structures with role inheritance.
        Automatic permission propagation with circular dependency detection.
      </>
    ),
  },
  {
    title: 'Extensible',
    icon: '🔧',
    description: (
      <>
        Plugin architecture for custom storage backends, policy evaluators,
        and authorization engines. Build what you need.
      </>
    ),
  },
];

function Feature({icon, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center" style={{fontSize: '4rem'}}>
        {icon}
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
