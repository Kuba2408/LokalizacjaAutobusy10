import {ErrorBoundary, JSX, Suspense} from "solid-js";

type AppProviderProps = {
    children: JSX.Element[]
}

export default function AppProvider({children}: AppProviderProps) {
    return <Suspense fallback={<div>Loading...</div>}>
        <ErrorBoundary fallback={(err, reset) => <div onClick={reset}>{err.toString()}</div>}>
            {children}
        </ErrorBoundary>
    </Suspense>
}