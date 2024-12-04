// import a bunch of leaflet stuff!
import 'leaflet/dist/leaflet.css';
import * as L from 'leaflet';
import 'leaflet.markercluster';


import {Component, createEffect, onMount} from 'solid-js';
import {getDefaultCoords} from "@/utils/coords.ts";
import {Transportation} from "@/types/api.ts";
import {TransportationType} from "@/features/transportation/types/transportation-type.ts";
import {BusIcon, TramIcon} from "@/libs/map.ts";

type ViewProps = {
    transportations: Transportation[]
}

export const View: Component<ViewProps> = ({transportations}) => {

    let mapRef: HTMLDivElement;

    onMount(() => {

        const coords = getDefaultCoords();
        const map = L.map('map').setView([coords.lat, coords.lng], 13);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map);

        let markerLayer = L.layerGroup([]);

        createEffect(() => {
            markerLayer.clearLayers();
            console.log(transportations);
            const markers = transportations?.map(t => {
                return L.marker([t.position.lat, t.position.lng], {icon: t.type === TransportationType.Tram ? TramIcon : BusIcon}).bindPopup(`${t.line} ${t.tripId}`);
            });
            markerLayer = L.layerGroup(markers);

            map.addLayer(markerLayer);
        });

        map.addLayer(markerLayer);
    });

    // @ts-ignore
    return <div ref={mapRef} id="map" class="h-screen"/>
}