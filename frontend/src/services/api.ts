export const FLASK_URL = process.env.NEXT_PUBLIC_FLASK_URL || 'http://localhost:5000';

export interface SearchResponse {
  status_key: string;
  dish: string;
  city: string;
}

export interface StatusResponse {
  status: string;
  progress: number;
}

export interface Restaurant {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  avg_rating: number;
  reviews: number;
  score: number;
}

export interface ResultsResponse {
  dish: string;
  city: string;
  city_lat: number;
  city_lng: number;
  restaurants: Restaurant[];
  error?: string;
}

export const api = {
  async search(dish: string, city: string, maxPlaces: number = 15): Promise<SearchResponse> {
    const res = await fetch(`${FLASK_URL}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dish, city, max_places: maxPlaces }),
    });
    if (!res.ok) throw new Error('Search request failed');
    return res.json();
  },

  async getStatus(dish: string, city: string): Promise<StatusResponse> {
    const res = await fetch(`${FLASK_URL}/api/status/${encodeURIComponent(dish)}/${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error('Status request failed');
    return res.json();
  },

  async getResults(dish: string, city: string): Promise<ResultsResponse> {
    const res = await fetch(`${FLASK_URL}/api/results/${encodeURIComponent(dish)}/${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error('Results not ready or request failed');
    return res.json();
  }
};
