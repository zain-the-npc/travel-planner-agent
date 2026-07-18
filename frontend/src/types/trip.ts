export interface TripRequest {
  origin: string;
  destination_city: string;
  destination_airport: string;
  departure_date: string;
  budget: number;
}

export interface TripResponse {
  answer: string;
}
