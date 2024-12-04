import {Component, JSX} from "solid-js";
import {cn} from "@/utils/cn.ts";

interface ButtonProps extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "icon";
    size?: "sm" | "md" | "lg";
    icon?: JSX.Element
}

const variantStyles = {
    primary:
        "border-gray-300 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:focus:border-blue-400 dark:focus:ring-blue-400",
    icon:
        "border-red-300 focus:border-red-500 focus:ring-red-500 dark:border-red-400 dark:focus:border-red-300 dark:focus:ring-red-300",
};

const sizeStyles = {
    sm: "text-sm",
    md: "text-sm",
    lg: "text-lg",
};


export const Button: Component<ButtonProps> = ({
                                                   variant = "primary", size = "md", children, icon
                                                   , ...props
                                               }) => {

    return <button
        class={cn("rounded-xl border bg-white transition-colors px-3 py-2.5", variantStyles[variant], sizeStyles[size], props.class)}>
        {icon ? <div class="text-gray-400">{icon}</div> : children}
    </button>
}