import {PositionDto, Transportation} from "@/types/api.ts";
import {TransportationType} from "@/features/transportation/types/transportation-type.ts";

const parseTripId = (_tripId: string) => {
    // RA220830/24/TP-NBM/DP/07.15__
    const split = _tripId.split("/");
    const line = split[1];
    const tripId = split[0];


    const type = Number(line) >= 100 ? TransportationType.Bus : TransportationType.Tram;

    return {
        line, tripId, type
    }
}

export const createFromDto = (pos: PositionDto): Transportation => {
    const {line, tripId, type} = parseTripId(pos.trip_id);

    return {
        line,
        tripId,
        type,
        position: {lat: pos.lat, lng: pos.lon},
        id: pos.id,
        timestamp: pos.timestamp,
        sideNumber: pos.side_number
    }
}