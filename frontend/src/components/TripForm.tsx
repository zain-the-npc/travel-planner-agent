import React, { useState } from 'react';
import type { TripRequest } from '../types/trip';

interface TripFormProps {
  onSubmit: (data: TripRequest) => void;
  isLoading: boolean;
}

export const TripForm: React.FC<TripFormProps> = ({ onSubmit, isLoading }) => {
  const [origin, setOrigin] = useState('');
  const [destinationAirport, setDestinationAirport] = useState('');
  const [destinationCity, setDestinationCity] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [budget, setBudget] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!origin || !destinationAirport || !destinationCity || !departureDate || !budget) {
      return;
    }
    onSubmit({
      origin: origin.toUpperCase().trim(),
      destination_airport: destinationAirport.toUpperCase().trim(),
      destination_city: destinationCity.trim(),
      departure_date: departureDate,
      budget: parseFloat(budget),
    });
  };

  const inputClass = "w-full bg-transparent border-b border-muted text-ink font-body text-base py-2 focus:outline-none focus:border-gold transition-colors duration-200 placeholder-muted/40";
  const labelClass = "font-mono text-[10px] tracking-wider text-muted uppercase block mb-1";

  return (
    <form onSubmit={handleSubmit} className="bg-navy p-6 md:p-8 border border-ink/10 rounded-sm space-y-6 max-w-xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="origin" className={labelClass}>From (Airport Code)</label>
          <input
            id="origin"
            type="text"
            placeholder="LHR"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            maxLength={3}
            required
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="destination_airport" className={labelClass}>To (Airport Code)</label>
          <input
            id="destination_airport"
            type="text"
            placeholder="IST"
            value={destinationAirport}
            onChange={(e) => setDestinationAirport(e.target.value)}
            maxLength={3}
            required
            className={inputClass}
          />
        </div>

        <div className="md:col-span-2">
          <label htmlFor="destination_city" className={labelClass}>Destination City</label>
          <input
            id="destination_city"
            type="text"
            placeholder="Istanbul"
            value={destinationCity}
            onChange={(e) => setDestinationCity(e.target.value)}
            required
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="departure_date" className={labelClass}>Departure Date</label>
          <input
            id="departure_date"
            type="date"
            value={departureDate}
            onChange={(e) => setDepartureDate(e.target.value)}
            required
            className={`${inputClass} [color-scheme:dark]`}
          />
        </div>

        <div>
          <label htmlFor="budget" className={labelClass}>Total Budget (USD)</label>
          <input
            id="budget"
            type="number"
            placeholder="1500"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            min={1}
            required
            className={inputClass}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gold text-navy-deep font-body font-semibold text-sm py-3 rounded-[2px] transition-opacity duration-200 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider"
      >
        {isLoading ? 'Planning Trip...' : 'Plan My Trip'}
      </button>
    </form>
  );
};
