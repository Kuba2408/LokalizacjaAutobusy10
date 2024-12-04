import {IoSearch} from 'solid-icons/io'
import {IoLocate} from 'solid-icons/io'
import {Component, createSignal} from "solid-js";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";

interface ControlsProps {

};

export const Controls: Component<ControlsProps> = (props) => {
    const [search, setSearch] = createSignal("");
    return <div class="z-[999] absolute flex justify-end items-start gap-1 right-1 top-1">
        <Button class="" icon={<IoLocate/>}/>
        <Input value={search()} onInput={(e) => setSearch(e.currentTarget.value)}
               class="max-w-[300px] w-screen"
               appendIcon={<IoSearch class="cursor-pointer"/>}/>
    </div>
}