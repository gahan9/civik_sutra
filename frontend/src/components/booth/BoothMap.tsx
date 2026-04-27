import { GoogleMap, MarkerF, useJsApiLoader } from "@react-google-maps/api";

import type { BoothResult, LatLng } from "../../types/booth";

interface BoothMapProps {
  userLocation: LatLng | null;
  booths: BoothResult[];
  selectedBoothId: string | null;
  onSelectBooth: (booth: BoothResult) => void;
}

const mapContainerStyle = {
  width: "100%",
  height: "100%",
};

const defaultCenter: LatLng = {
  lat: 28.6139,
  lng: 77.209,
};

export function BoothMap({
  userLocation,
  booths,
  selectedBoothId,
  onSelectBooth,
}: BoothMapProps) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined;
  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: apiKey ?? "",
  });

  if (!apiKey || !isLoaded) {
    return (
      <div className="map-fallback" aria-label="Polling booth map preview">
        <div className="map-grid">
          <span className="user-dot">You</span>
          {booths.map((booth) => (
            <button
              className={
                booth.id === selectedBoothId ? "map-pin selected" : "map-pin"
              }
              key={booth.id}
              type="button"
              onClick={() => onSelectBooth(booth)}
            >
              {booth.name}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <GoogleMap
      center={userLocation ?? booths[0]?.location ?? defaultCenter}
      mapContainerStyle={mapContainerStyle}
      options={{
        fullscreenControl: false,
        mapTypeControl: false,
        streetViewControl: false,
      }}
      zoom={14}
    >
      {userLocation ? (
        <MarkerF position={userLocation} title="Your location" />
      ) : null}
      {booths.map((booth) => (
        <MarkerF
          key={booth.id}
          position={booth.location}
          title={booth.name}
          onClick={() => onSelectBooth(booth)}
        />
      ))}
    </GoogleMap>
  );
}
