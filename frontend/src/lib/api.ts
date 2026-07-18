import type { TripRequest, TripResponse } from '../types/trip';

export async function planTrip(req: TripRequest): Promise<TripResponse> {
  const response = await fetch('http://localhost:8000/plan-trip', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    throw new Error(`Failed to plan trip. Server responded with status ${response.status}`);
  }

  return response.json();
}
