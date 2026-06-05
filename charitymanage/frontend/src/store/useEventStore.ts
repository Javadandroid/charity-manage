import { create } from 'zustand';
import api from '../api';

interface Event {
  id: number;
  name: string;
  is_active: boolean;
  start_date: string;
  end_date: string;
  location: string;
}

interface EventStore {
  activeEvent: Event | null;
  allEvents: Event[];
  fetchEvents: () => Promise<void>;
  setActiveEvent: (event: Event) => void;
}

export const useEventStore = create<EventStore>((set) => ({
  activeEvent: null,
  allEvents: [],
  fetchEvents: async () => {
    try {
      const response = await api.get('/api/events/');
      const events = response.data;
      const active = events.find((e: Event) => e.is_active);
      set({ allEvents: events, activeEvent: active || null });
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  },
  setActiveEvent: (event) => set({ activeEvent: event }),
}));
