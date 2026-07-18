import React from 'react';

export const Hero: React.FC = () => {
  return (
    <header className="text-center mb-12">
      <p className="font-mono text-xs tracking-[0.15em] text-gold uppercase mb-4">
        Autonomous Trip Planning
      </p>
      <h1 className="font-display font-semibold text-4xl md:text-5xl text-ink leading-tight mb-3">
        Where to, next?
      </h1>
      <p className="text-muted text-sm md:text-base max-w-md mx-auto leading-relaxed">
        An AI agent finds real flights, hotels, and places — you just say where.
      </p>
    </header>
  );
};
