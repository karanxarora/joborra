import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import apiService from '../services/api';
import { Job, JobFavoriteWithJob } from '../types';

interface FavoritesState {
  favorites: JobFavoriteWithJob[];
  map: Record<number, number>; // job_id -> favorite_id
  loading: boolean;
  refresh: () => Promise<void>;
  add: (jobId: number, notes?: string | null) => Promise<number | null>; // returns favorite_id
  remove: (favoriteId: number) => Promise<boolean>;
}

const FavoritesContext = createContext<FavoritesState | undefined>(undefined);

export const useFavorites = () => {
  const ctx = useContext(FavoritesContext);
  if (!ctx) throw new Error('useFavorites must be used within FavoritesProvider');
  return ctx;
};

export const FavoritesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [favorites, setFavorites] = useState<JobFavoriteWithJob[]>([]);
  const [map, setMap] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState<boolean>(true);

  const buildMap = (items: any[]) => {
    const m: Record<number, number> = {};
    items.forEach((f: any) => { m[f.job_id] = f.id; });
    return m;
  };

  const refresh = async () => {
    setLoading(true);
    try {
      const items = await apiService.listFavorites();
      setFavorites(items as any);
      setMap(buildMap(items));
    } catch (e: any) {
      // If unauthorized, keep current state to avoid flicker and let route protection handle access
      if (e?.response?.status === 401) {
        // no-op: keep existing favorites/map
      } else {
        setFavorites([]);
        setMap({});
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Preload on app start; auth interceptor will redirect if unauthenticated
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const add = async (jobId: number, notes?: string | null) => {
    try {
      const created = await apiService.addFavorite(jobId, notes);
      // Only minimal update to avoid needing job object; callers often don't need full list here
      setMap((prev) => ({ ...prev, [jobId]: created.id }));
      // Best-effort refresh to populate list with job details
      refresh();
      return created.id as number;
    } catch (e) {
      return null;
    }
  };

  const remove = async (favoriteId: number) => {
    try {
      await apiService.removeFavorite(favoriteId);
      setFavorites((prev) => prev.filter((f) => f.id !== favoriteId));
      setMap((prev) => {
        const newMap = { ...prev } as Record<number, number>;
        // delete by reverse lookup
        const jobId = Object.keys(newMap).find((k) => newMap[Number(k)] === favoriteId);
        if (jobId) delete newMap[Number(jobId)];
        return newMap;
      });
      return true;
    } catch (e) {
      return false;
    }
  };

  const value = useMemo(() => ({ favorites, map, loading, refresh, add, remove }), [favorites, map, loading]);

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  );
};
