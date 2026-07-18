export interface TripRequest {
  origin: string;
  destination_city: string;
  destination_airport: string;
  departure_date: string;
  budget: number;
}

export interface TripResponse {
  answer: string;
  total_cost_usd: number;
}

export interface ConvertRequest {
  amount: number;
  from_currency: string;
  to_currency: string;
}

export interface ConvertResponse {
  converted_amount: number;
  rate: number;
  from_currency: string;
  to_currency: string;
  date: string;
  error?: string;
}
