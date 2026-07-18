import React from 'react';

interface ErrorStateProps {
  message: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message }) => {
  return (
    <div className="max-w-xl mx-auto mt-6 text-center">
      <p className="font-body text-sm text-sky leading-relaxed">
        {message}
      </p>
    </div>
  );
};
