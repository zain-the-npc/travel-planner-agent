import React from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

interface ResultTicketProps {
  answer: string;
  route: string;
  date: string;
}

export const ResultTicket: React.FC<ResultTicketProps> = ({ answer, route, date }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="relative rounded-sm overflow-hidden bg-sand text-navy-deep max-w-xl mx-auto mt-8 shadow-xl"
    >
      {/* Header Bar */}
      <div className="bg-navy text-ink px-6 py-4 flex justify-between items-center font-mono text-xs uppercase tracking-widest">
        <span className="font-semibold">{route}</span>
        <span className="text-gold">{date}</span>
      </div>

      {/* Perforation Divider with Cutouts */}
      <div className="relative py-2 bg-sand">
        <div className="w-full border-t-[2px] border-dashed border-navy-deep/20"></div>
        <div className="absolute -left-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-navy-deep"></div>
        <div className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-navy-deep"></div>
      </div>

      {/* Ticket Body with Markdown */}
      <div className="p-6 md:p-8 font-body">
        <ReactMarkdown
          components={{
            h2: ({ node, ...props }) => (
              <h2 className="font-display font-semibold text-lg text-navy-deep mt-4 mb-2 first:mt-0" {...props} />
            ),
            h3: ({ node, ...props }) => (
              <h3 className="font-display font-semibold text-base text-navy-deep mt-3 mb-1" {...props} />
            ),
            strong: ({ node, ...props }) => (
              <strong className="text-sky font-semibold" {...props} />
            ),
            ul: ({ node, ...props }) => (
              <ul className="list-disc pl-5 my-2 space-y-1" {...props} />
            ),
            li: ({ node, ...props }) => (
              <li className="marker:text-gold text-sm leading-[1.7] text-navy-deep/90" {...props} />
            ),
            p: ({ node, ...props }) => (
              <p className="text-sm leading-[1.7] mb-3 text-navy-deep/90" {...props} />
            ),
          }}
        >
          {answer}
        </ReactMarkdown>
      </div>
    </motion.div>
  );
};
