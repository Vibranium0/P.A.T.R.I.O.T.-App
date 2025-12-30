import React, { createContext, useContext, useState } from "react";
import usePageTransition from "../shared/ui/components/usePageTransition";

// Context to provide transition trigger and state
const TransitionContext = createContext();

export function useTransitionOverlay() {
    return useContext(TransitionContext);
}

export function TransitionProvider({ children }) {
    const [direction, setDirection] = useState("left");
    const [active, trigger] = usePageTransition();

    // Expose trigger with direction
    const triggerTransition = (cb, dir = "left") => {
        setDirection(dir);
        trigger(cb);
    };

    return (
        <TransitionContext.Provider value={{ active, triggerTransition, direction }}>
            {children}
        </TransitionContext.Provider>
    );
}
