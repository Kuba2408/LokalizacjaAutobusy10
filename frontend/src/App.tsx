import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import {useCallback, useEffect, useState} from "react";
import busIcon from './assets/bus.svg';
import L from 'leaflet';

const busMarkerIcon = new L.Icon({
    iconUrl: busIcon,
    iconSize: [24, 24],
    iconAnchor: [13, 32],
    popupAnchor: [0, -32]
});

function App() {

    const [buses, setBuses] = useState([]);

    const getBuses = useCallback(async () => {
        const response = await fetch("//localhost:8080/get_all_data");
        const _buses = Object.entries((await response.json()))
            .filter(([k,_v]) => k.startsWith("bus"))
            .map(bus => ({id: bus[0],...bus[1]}));
        setBuses(_buses);
    },[]);

    useEffect(()=> {
        setInterval(getBuses,10_000);
        getBuses()
    },[]);

    return(<div>
        <MapContainer className="h-screen" center={[52.237049, 21.017532]} zoom={11} >
            <TileLayer url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png" />
            {buses.map(bus => <Marker icon={busMarkerIcon} key={bus.id} position={[bus.latitude, bus.longitude]}><Popup>{bus.line}</Popup></Marker>)}
        </MapContainer>
    </div>);

}

export default App;