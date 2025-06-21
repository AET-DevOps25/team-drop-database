import React from "react";
import {GoogleMap, Marker, useLoadScript} from "@react-google-maps/api";
import {CircularProgress} from "@mui/material";

interface AttractionMapProps {
    /** Latitude of the attraction */
    lat: number;
    /** Longitude of the attraction */
    lng: number;
    /** Optional name for the marker tooltip */
    name?: string;
    /** Height of the map container – accepts number (pixels) or any CSS string */
    height?: number | string;
}

/**
 * Displays a Google Map centred on the attraction’s location with a single marker.
 *
 * Uses @react-google-maps/api under the hood. Make sure you have a Google Maps
 * API key available via either `VITE_GOOGLE_MAPS_API_KEY` (Vite) **or**
 * `REACT_APP_GOOGLE_MAPS_API_KEY` (Create‑React‑App).
 */
const AttractionMap: React.FC<AttractionMapProps> = ({
                                                         lat,
                                                         lng,
                                                         name,
                                                         height = 400,
                                                     }) => {
    const {isLoaded, loadError} = useLoadScript({
        googleMapsApiKey: process.env.GOOGLE_API_KEY as string
    });

    if (loadError) {
        return (
            <div style={{textAlign: "center", marginTop: 16}}>
                地图加载失败，请稍后再试
            </div>
        );
    }

    if (!isLoaded) {
        return (
            <div style={{textAlign: "center", marginTop: 16}}>
                <CircularProgress/>
            </div>
        );
    }

    const center = {lat, lng} as google.maps.LatLngLiteral;

    return (
        <GoogleMap
            center={center}
            zoom={15}
            mapContainerStyle={{
                width: "100%",
                height: typeof height === "number" ? `${height}px` : height,
                borderRadius: 12,
            }}
            options={{
                fullscreenControl: false,
                streetViewControl: false,
                mapTypeControl: false,
            }}
        >
            <Marker position={center} title={name}/>
        </GoogleMap>
    );
};

export default AttractionMap;
