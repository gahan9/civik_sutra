import { useCallback, useState } from "react";

import type { LatLng } from "../types/booth";

interface GeolocationState {
  location: LatLng | null;
  loading: boolean;
  error: string | null;
  denied: boolean;
}

interface UseGeolocationResult extends GeolocationState {
  requestLocation: () => Promise<LatLng | null>;
}

export function useGeolocation(): UseGeolocationResult {
  const [state, setState] = useState<GeolocationState>({
    location: null,
    loading: false,
    error: null,
    denied: false,
  });

  const requestLocation = useCallback((): Promise<LatLng | null> => {
    if (!navigator.geolocation) {
      setState({
        location: null,
        loading: false,
        error: "Geolocation is not supported by this browser.",
        denied: false,
      });
      return Promise.resolve(null);
    }

    setState((current) => ({
      ...current,
      loading: true,
      error: null,
      denied: false,
    }));

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setState({
            location,
            loading: false,
            error: null,
            denied: false,
          });
          resolve(location);
        },
        (error) => {
          const denied = error.code === error.PERMISSION_DENIED;
          setState({
            location: null,
            loading: false,
            error: denied
              ? "Location permission was denied. Use manual search instead."
              : "Unable to determine your location right now.",
            denied,
          });
          resolve(null);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      );
    });
  }, []);

  return {
    ...state,
    requestLocation,
  };
}
