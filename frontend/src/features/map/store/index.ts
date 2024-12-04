import data from '@/tests/mocks/data.json';
import {createWithSignal} from "solid-zustand";
import {createFromDto} from "@/features/transportation/utils/create-from-dto.ts";
import {Transportation} from "@/types/api.ts";

const fetchData = async () => {
    console.log('loaded!');
    await new Promise((resolve) => setTimeout(resolve, ~~(Math.random() * 1000)));

    return data.positions.map(pos => {
        return createFromDto(pos);
    });
}

interface MapState {
    loading: boolean
    error: string
    positions: Transportation[]
    getTransportations: () => Promise<void>
}

export const useMapStore = createWithSignal<MapState>(set => ({
    positions: [],
    error: "",
    loading: false,
    getTransportations: async () => {
        set({loading: true});
        try {
            const positions = await fetchData();
            set({positions: positions});
        } catch (e) {
            if (e instanceof Error) {
                set({error: e.message});
            }
        } finally {
            set({loading: false});
        }
    }
}));

