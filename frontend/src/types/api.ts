import {TransportationType} from "@/features/transportation/types/transportation-type.ts";

export type PositionDto = {
    id: string,
    timestamp: string,
    side_number: string,
    trip_id: string,
    lat: number,
    lon: number
}


export type Position = {
    lat: number,
    lng: number
}

export interface Transportation {
    type: TransportationType,
    position: Position
    id: string
    timestamp: string
    sideNumber: string
    tripId: string
    line: string
}


export interface Bus extends Transportation {
    type: TransportationType.Bus
}

export interface Tram extends Transportation {
    type: TransportationType.Tram
}