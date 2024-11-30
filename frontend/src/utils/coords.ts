import {Position} from "@/types/api.ts";

export function getDefaultCoords(): Position {
    return {
        lat: Number(import.meta.env.VITE_DEFAULT_LAT),
        lng: Number(import.meta.env.VITE_DEFAULT_LNG)
    }
}