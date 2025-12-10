import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useQuery, gql } from "@apollo/client";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const GET_MAP_DATA = gql`
  query GetMapData {
    hydravions {
      id
      nom
      statut
      port_actuel
    }
    ports {
      nom
      latitude
      longitude
    }
  }
`;

const planeIcon = new L.Icon({
  iconUrl: "https://www.pngkey.com/png/detail/367-3676850_airplane-icon-vector-icono-de-avion-png.png",
  iconSize: [35, 35],
});

const portIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
  iconSize: [30, 30],
});

export default function MapView() {
  const { data, loading, error } = useQuery(GET_MAP_DATA, {
    pollInterval: 5000,
  });

  if (loading) return <p>Chargement de la carte...</p>;
  if (error) return <p>Erreur : {error.message}</p>;

  const { hydravions, ports } = data;

  const getPortCoords = (name) => ports.find((p) => p.nom === name);

  return (
    <MapContainer
      center={[-0.9538, -90.9656]} 
      zoom={9}
      style={{ height: "600px", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        maxZoom={18}
      />

      {ports.map((port) => (
        <Marker
          key={port.nom}
          position={[port.latitude, port.longitude]}
          icon={portIcon}
        >
          <Popup>
            <strong>{port.nom}</strong>
          </Popup>
        </Marker>
      ))}

      {hydravions.map((h) => {
        const port = getPortCoords(h.port_actuel);
        if (!port) return null;

        return (
          <Marker
            key={h.id}
            position={[port.latitude, port.longitude]}
            icon={planeIcon}
          >
            <Popup>
              <strong>{h.nom}</strong> <br />
              Statut : {h.statut} <br />
              Port : {h.port_actuel}
            </Popup>
          </Marker>
        );
      })}

    </MapContainer>
  );
}
