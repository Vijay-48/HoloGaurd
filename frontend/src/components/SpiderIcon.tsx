
import React from 'react';

interface SpiderIconProps {
  size?: number;
  className?: string;
  animate?: boolean;
}

const SpiderIcon: React.FC<SpiderIconProps> = ({ 
  size = 24, 
  className = "", 
  animate = false 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={`${className} ${animate ? 'animate-pulse' : ''}`}
    >
      {/* Spider body */}
      <ellipse cx="12" cy="12" rx="3" ry="4" />
      <circle cx="12" cy="10" r="2" />
      
      {/* Spider legs */}
      <path d="M8 8l-3-3M16 8l3-3M8 16l-3 3M16 16l3 3" stroke="currentColor" strokeWidth="1" fill="none" />
      <path d="M6 12l-4 0M18 12l4 0" stroke="currentColor" strokeWidth="1" fill="none" />
      <path d="M9 6l-2-4M15 6l2-4M9 18l-2 4M15 18l2 4" stroke="currentColor" strokeWidth="1" fill="none" />
    </svg>
  );
};

export default SpiderIcon;
