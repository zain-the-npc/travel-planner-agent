import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export const LoadingState: React.FC = () => {
  const messages = [
    "Calling flight tools...",
    "Checking hotel prices...",
    "Calculating your budget..."
  ];

  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % messages.length);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-12 max-w-xl mx-auto space-y-4">
      <p className="font-mono text-xs text-gold tracking-wide">
        {messages[messageIndex]}
      </p>
      <motion.div
        className="h-[2px] w-24 bg-gold"
        animate={{ opacity: [0.2, 1, 0.2] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  );
};
