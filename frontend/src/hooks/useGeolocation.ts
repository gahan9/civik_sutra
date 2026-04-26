import { useCallback, useState } from "react";

import type { LatLng } from "../types/booth";


interface GeolocationState {
  location: LatLng | null;
  loading: boolean;
  error: string | null;
  denied: boolean;
}

interface UseGeolocationResult extends GeolocationState {
  requestLocation: () => void;
}

export function useGeolocation(): UseGeolocationResult {
  const [state, setState] = useState<GeolocationState>({
    location: null,
    loading: false,
    error: null,
    denied: false,
  });

  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setState({
        location: null,
        loading: false,
        error: "Geolocation is not supported by this browser.",
        denied: false,
      });
      return;
    }

    setState((current) => ({
      ...current,
      loading: true,
      error: null,
      denied: false,
    }));

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          location: {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          },
          loading: false,
          error: null,
          denied: false,
        });
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
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      },
    );
  }, []);

  return {
    ...state,
    requestLocation,
  };
}
