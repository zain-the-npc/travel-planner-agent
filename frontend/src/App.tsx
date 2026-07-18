import { useState } from 'react';
import { Hero } from './components/Hero';
import { TripForm } from './components/TripForm';
import { LoadingState } from './components/LoadingState';
import { ResultTicket } from './components/ResultTicket';
import { ErrorState } from './components/ErrorState';
import type { TripRequest, TripResponse } from './types/trip';
import { planTrip } from './lib/api';

type AppState = 'idle' | 'loading' | 'success' | 'error';

function App() {
  const [state, setState] = useState<AppState>('idle');
  const [request, setRequest] = useState<TripRequest | null>(null);
  const [response, setResponse] = useState<TripResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const handleFormSubmit = async (req: TripRequest) => {
    setRequest(req);
    setState('loading');
    setErrorMsg('');
    setResponse(null);

    try {
      const res = await planTrip(req);
      setResponse(res);
      setState('success');
    } catch (err: any) {
      setErrorMsg(err.message || 'Something went wrong. Please check your backend connection.');
      setState('error');
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 md:px-6 max-w-2xl mx-auto font-body text-ink flex flex-col justify-start">
      <Hero />
      <TripForm onSubmit={handleFormSubmit} isLoading={state === 'loading'} />

      {state === 'loading' && <LoadingState />}
      {state === 'success' && response && request && (
        <ResultTicket
          answer={response.answer}
          route={`${request.origin} → ${request.destination_airport}`}
          date={request.departure_date}
          totalCostUsd={response.total_cost_usd}
        />
      )}
      {state === 'error' && <ErrorState message={errorMsg} />}
    </div>
  );
}

export default App;
