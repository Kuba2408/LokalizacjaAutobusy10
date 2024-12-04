import {Controls} from "@/features/map/components/controls.tsx";
import {View} from "@/features/map/components/view.tsx";
import {onMount, Show} from "solid-js";
import {useMapStore} from "@/features/map/store";

export const Map = (props) => {

    const getBuses = useMapStore(state => state.getTransportations);
    const positions = useMapStore(state => state.positions);
    const loading = useMapStore(state => state.loading);

    onMount(() => {
        getBuses();
        setInterval(getBuses, 10_000);
    });

    return <>
        <Controls/>
        <Show when={!loading()} fallback={<View transportations={[]}/>}>
            <View transportations={positions()}/>
        </Show>
    </>
}