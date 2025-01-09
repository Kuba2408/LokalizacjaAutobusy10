import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import { useCallback, useEffect, useState, useRef } from "react";
import { IconX } from '@tabler/icons-react';
import L from 'leaflet';
import {Paper, Text, ScrollArea, Tabs, TextInput, Checkbox, Button} from '@mantine/core';
import busIcon from './assets/bus.svg';
import {useDisclosure} from "@mantine/hooks";

const createBusMarkerIcon = (line) => {
    return L.divIcon({
        className: 'custom-bus-icon',
        html: `
            <div class="flex flex-col-reverse">
                <img src="${busIcon}" alt="Bus" class="bus-icon" />

                <span class="bg-black text-white rounded-xl">${line}</span>
            </div>
        `,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -10]
    });
};

function App() {
    const [buses, setBuses] = useState([]);
    const [lines, setLines] = useState([]);
    const [searchLine, setSearchLine] = useState('');
    const [selectedLines, setSelectedLines] = useState([]);
    const [error, setError] = useState(null);
    const [showError, { open: openError, close: closeError }] = useDisclosure(false);
    const mapRef = useRef(null);

    const getBuses = useCallback(async () => {
        try {
            const response = await fetch("//localhost:8080/get_all_data");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const _buses = Object.entries(data)
                .filter(([k,_v]) => k.startsWith("bus"))
                .map(bus => ({id: bus[0],...bus[1]}));
            const _lines = Array.from(new Set(_buses.map(b => b.line)));
            setLines(_lines);
            setBuses(_buses);
        } catch (e) {
            setError(e.message);
            openError();
        }
    }, [openError]);

    useEffect(() => {
        const intervalId = setInterval(getBuses, 10000);
        getBuses();
        return () => clearInterval(intervalId);
    }, [getBuses]);

    const focusOnBus = (lat, lng) => {
        mapRef.current?.flyTo([lat, lng], 15);
    };

    const handleLineCheckbox = (line) => {
        setSelectedLines(prev =>
            prev.includes(line)
                ? prev.filter(l => l !== line)
                : [...prev, line]
        );
    };

    const clearSelectedLines = () => {
        setSelectedLines([]);
    };

    const filteredLines = lines.filter(line =>
        line.toLowerCase().includes(searchLine.toLowerCase())
    );

    const filteredBuses = buses.filter(bus =>
        selectedLines.length === 0 || selectedLines.includes(bus.line)
    );

    return (
        <div className="relative h-screen w-full">
            <MapContainer
                ref={mapRef}
                className="h-full w-full z-0"
                center={[52.237049, 21.017532]}
                zoom={11}
            >
                <TileLayer url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png" />
                {filteredBuses.map(bus => (
                    <Marker
                        key={bus.id}
                        icon={createBusMarkerIcon(bus.line)}
                        position={[bus.latitude, bus.longitude]}
                    >
                        <Popup>
                            Bus ID: {bus.id}<br/>
                            Line: {bus.line}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {showError && (
                <Notification
                    icon={<IconX size="1.1rem" />}
                    color="red"
                    title="Error"
                    className="absolute bottom-4 right-4 z-9999"
                    onClose={closeError}
                >
                    {error}
                </Notification>
            )}

            <Paper
                className="bg-white absolute top-4 right-4 w-64 max-h-[calc(100vh-2rem)] overflow-hidden z-9999"
                shadow="md"
                radius="md"
            >
                <Tabs variant="outline" defaultValue="lines">
                    <Tabs.List>
                        <Tabs.Tab value="lines">Linie</Tabs.Tab>
                        <Tabs.Tab value="buses">Autobusy</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="lines" p="xs">
                        <TextInput
                            placeholder="Wyszukaj..."
                            value={searchLine}
                            onChange={(event) => setSearchLine(event.currentTarget.value)}
                            mb="sm"
                        />
                        <div className="flex justify-between items-center mb-2">
                            <Text size="sm">Zaznaczone: {selectedLines.length}</Text>
                            <Button
                                size="xs"
                                variant="light"
                                onClick={clearSelectedLines}
                                disabled={selectedLines.length === 0}
                            >
                                Wyczyść
                            </Button>
                        </div>
                        <ScrollArea className="h-[calc(100vh-14rem)]">
                            {filteredLines.map(line => (
                                <Checkbox
                                    key={line}
                                    label={line}
                                    checked={selectedLines.includes(line)}
                                    onChange={() => handleLineCheckbox(line)}
                                    mb="xs"
                                />
                            ))}
                        </ScrollArea>
                    </Tabs.Panel>

                    <Tabs.Panel value="buses" p="xs">
                        <ScrollArea className="h-[calc(100vh-10rem)]">
                            {filteredBuses.map(bus => (
                                <div
                                    key={bus.id}
                                    className="p-3 cursor-pointer hover:bg-gray-100 transition-colors"
                                    onClick={() => focusOnBus(bus.latitude, bus.longitude)}
                                >
                                    <Text>Identyfikator: {bus.id.split(':').slice(1).join(':')}</Text>
                                    <Text>Linia: {bus.line}</Text>
                                </div>
                            ))}
                        </ScrollArea>
                    </Tabs.Panel>
                </Tabs>
            </Paper>
        </div>
    );
}

export default App;