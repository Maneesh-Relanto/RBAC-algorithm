import React, { useEffect, useRef, useState } from 'react';
import styles from './styles.module.css';

const RoleHierarchyVisualizer = () => {
  const canvasRef = useRef(null);
  const [selectedExample, setSelectedExample] = useState('basic');

  const examples = {
    basic: {
      title: 'Simple Hierarchy',
      roles: [
        { id: 'viewer', name: 'Viewer', permissions: ['read'], level: 0 },
        { id: 'editor', name: 'Editor', permissions: ['read', 'write'], parent: 'viewer', level: 1 },
        { id: 'admin', name: 'Admin', permissions: ['read', 'write', 'delete'], parent: 'editor', level: 2 },
      ]
    },
    org: {
      title: 'Organization Structure',
      roles: [
        { id: 'employee', name: 'Employee', permissions: ['view_profile'], level: 0 },
        { id: 'team_lead', name: 'Team Lead', permissions: ['view_profile', 'manage_team'], parent: 'employee', level: 1 },
        { id: 'manager', name: 'Manager', permissions: ['view_profile', 'manage_team', 'approve_budget'], parent: 'team_lead', level: 2 },
        { id: 'director', name: 'Director', permissions: ['view_profile', 'manage_team', 'approve_budget', 'strategic_planning'], parent: 'manager', level: 3 },
      ]
    },
    multi: {
      title: 'Multiple Paths',
      roles: [
        { id: 'user', name: 'User', permissions: ['read'], level: 0 },
        { id: 'contributor', name: 'Contributor', permissions: ['read', 'comment'], parent: 'user', level: 1 },
        { id: 'author', name: 'Author', permissions: ['read', 'write'], parent: 'user', level: 1 },
        { id: 'moderator', name: 'Moderator', permissions: ['read', 'comment', 'moderate'], parent: 'contributor', level: 2 },
        { id: 'editor', name: 'Editor', permissions: ['read', 'write', 'edit_all'], parent: 'author', level: 2 },
        { id: 'admin', name: 'Admin', permissions: ['read', 'write', 'comment', 'moderate', 'edit_all', 'delete'], parent: 'moderator', level: 3 },
      ]
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const roles = examples[selectedExample].roles;

    // Clear canvas
    canvas.width = canvas.offsetWidth;
    canvas.height = 400;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate positions
    const levelHeight = canvas.height / (Math.max(...roles.map(r => r.level)) + 2);
    const positions = {};

    // Group by level
    const levels = {};
    roles.forEach(role => {
      if (!levels[role.level]) levels[role.level] = [];
      levels[role.level].push(role);
    });

    // Calculate positions
    Object.keys(levels).forEach(level => {
      const rolesInLevel = levels[level];
      const spacing = canvas.width / (rolesInLevel.length + 1);
      rolesInLevel.forEach((role, idx) => {
        positions[role.id] = {
          x: spacing * (idx + 1),
          y: levelHeight * (parseInt(level) + 1)
        };
      });
    });

    // Draw connections
    ctx.strokeStyle = '#667eea';
    ctx.lineWidth = 2;
    roles.forEach(role => {
      if (role.parent && positions[role.parent]) {
        const from = positions[role.parent];
        const to = positions[role.id];
        
        ctx.beginPath();
        ctx.moveTo(from.x, from.y + 25);
        ctx.lineTo(to.x, to.y - 25);
        ctx.stroke();

        // Draw arrow
        const angle = Math.atan2(to.y - from.y, to.x - from.x);
        const arrowLength = 10;
        ctx.beginPath();
        ctx.moveTo(to.x, to.y - 25);
        ctx.lineTo(
          to.x - arrowLength * Math.cos(angle - Math.PI / 6),
          to.y - 25 - arrowLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(to.x, to.y - 25);
        ctx.lineTo(
          to.x - arrowLength * Math.cos(angle + Math.PI / 6),
          to.y - 25 - arrowLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.stroke();
      }
    });

    // Draw roles
    roles.forEach(role => {
      const pos = positions[role.id];
      
      // Draw circle
      ctx.fillStyle = '#667eea';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 25, 0, 2 * Math.PI);
      ctx.fill();

      // Draw name
      ctx.fillStyle = '#000';
      ctx.font = 'bold 14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(role.name, pos.x, pos.y - 35);

      // Draw permission count
      ctx.fillStyle = '#fff';
      ctx.font = '12px sans-serif';
      ctx.fillText(role.permissions.length.toString(), pos.x, pos.y + 5);
    });

  }, [selectedExample]);

  return (
    <div className={styles.visualizer}>
      <div className={styles.header}>
        <h3>📊 Role Hierarchy Visualizer</h3>
        <div className={styles.exampleSelector}>
          {Object.keys(examples).map(key => (
            <button
              key={key}
              className={`${styles.exampleBtn} ${selectedExample === key ? styles.active : ''}`}
              onClick={() => setSelectedExample(key)}
            >
              {examples[key].title}
            </button>
          ))}
        </div>
      </div>

      <canvas ref={canvasRef} className={styles.canvas}></canvas>

      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <div className={styles.legendCircle}></div>
          <span>Role (number shows permission count)</span>
        </div>
        <div className={styles.legendItem}>
          <div className={styles.legendArrow}></div>
          <span>Inherits from (child → parent)</span>
        </div>
      </div>

      <div className={styles.details}>
        <h4>Roles in "{examples[selectedExample].title}":</h4>
        <div className={styles.roleCards}>
          {examples[selectedExample].roles.map(role => (
            <div key={role.id} className={styles.roleCard}>
              <strong>{role.name}</strong>
              {role.parent && <div className={styles.parent}>↑ Inherits from: {examples[selectedExample].roles.find(r => r.id === role.parent)?.name}</div>}
              <div className={styles.permissions}>
                <strong>Permissions ({role.permissions.length}):</strong>
                <ul>
                  {role.permissions.map(perm => (
                    <li key={perm}>{perm}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RoleHierarchyVisualizer;
