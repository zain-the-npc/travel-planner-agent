import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { convertCurrency } from '../lib/api';
import type { ConvertResponse } from '../types/trip';

interface ResultTicketProps {
  answer: string;
  route: string;
  date: string;
  totalCostUsd: number;
}

export const ResultTicket: React.FC<ResultTicketProps> = ({ answer, route, date, totalCostUsd }) => {
  const [targetCurrency, setTargetCurrency] = useState('EUR');
  const [conversionLoading, setConversionLoading] = useState(false);
  const [conversionResult, setConversionResult] = useState<ConvertResponse | null>(null);
  const [conversionError, setConversionError] = useState(false);

  const handleConvert = async () => {
    setConversionLoading(true);
    setConversionError(false);
    setConversionResult(null);
    try {
      const res = await convertCurrency({
        amount: totalCostUsd,
        from_currency: 'USD',
        to_currency: targetCurrency,
      });
      if ('error' in res && res.error) {
        setConversionError(true);
      } else {
        setConversionResult(res);
      }
    } catch (err) {
      setConversionError(true);
    } finally {
      setConversionLoading(false);
    }
  };

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

        {/* Currency Conversion Section */}
        <div className="border-t border-navy-deep/15 pt-6 mt-6">
          <label className="block font-mono text-[10px] tracking-wider text-navy-deep/60 uppercase mb-2">
            Convert total to:
          </label>
          <div className="flex items-center gap-3">
            <select
              value={targetCurrency}
              onChange={(e) => setTargetCurrency(e.target.value)}
              className="bg-transparent border border-navy-deep/20 rounded-sm text-navy-deep text-sm px-3 py-1.5 focus:outline-none focus:border-gold font-body"
            >
              {['EUR', 'GBP', 'PKR', 'TRY', 'JPY', 'AUD', 'CAD'].map((cc) => (
                <option key={cc} value={cc} className="bg-sand text-navy-deep">
                  {cc}
                </option>
              ))}
            </select>
            <button
              onClick={handleConvert}
              disabled={conversionLoading}
              className="border border-gold text-gold hover:bg-gold/5 font-body font-semibold text-xs py-1.5 px-4 rounded-[2px] transition-colors duration-200 disabled:opacity-50 flex items-center justify-center min-w-[80px]"
            >
              {conversionLoading ? (
                <svg className="animate-spin h-3.5 w-3.5 text-gold" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                'Convert'
              )}
            </button>
          </div>

          {/* Success State */}
          {conversionResult && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sky font-body text-xs mt-3 leading-relaxed"
            >
              ${totalCostUsd} USD ≈ {conversionResult.converted_amount.toFixed(2)} {conversionResult.to_currency} (rate: {conversionResult.rate.toFixed(4)}, as of {conversionResult.date})
            </motion.p>
          )}

          {/* Error State */}
          {conversionError && (
            <p className="text-navy-deep/60 font-body text-xs mt-3">
              Conversion failed, try again
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
};
