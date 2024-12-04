import * as L from 'leaflet';

const BaseIcon = L.Icon.extend({
    options: {
        iconSize: [24, 24],
        iconAnchor: [0, 0],
        popupAnchor: [12, 2]
    }
});

const blueDot = new URL('../assets/icons/blue-dot.svg', import.meta.url).href;
const busIcon = new URL('../assets/icons/bus.svg', import.meta.url).href;
const tramIcon = new URL('../assets/icons/tram.svg', import.meta.url).href;

// @ts-ignore
export const BusIcon = new BaseIcon({
    iconUrl: busIcon
});

// @ts-ignore
export const TramIcon = new BaseIcon({
    iconUrl: tramIcon
});

// @ts-ignore
export const UserIcon = new BaseIcon({
    iconUrl: blueDot,
    iconSize: [16, 16]
});