// Sentinel/P.A.T.R.I.O.T. - usePageTransition hook
// Provides a simple API to trigger the StarkPageTransition overlay on navigation.
// Usage: const [active, trigger] = usePageTransition();
//        trigger() to start the transition, then navigate after a delay.
import { useState, useCallback } from "react";

/**
 * usePageTransition
 *
 * Returns [active, triggerTransition].
 * - active: boolean, pass to <StarkPageTransition active={active} />
 * - triggerTransition: function, call to start the animation
 *
 * Handles timing and disables re-triggering while active.
 *
 * Example:
 *   const [transitioning, triggerTransition] = usePageTransition();
 *   const handleNav = () => {
 *     triggerTransition();
 *     setTimeout(() => navigate(...), 700); // match animation duration
 *   }
 */
/**
 * usePageTransition
 *
 * Returns [active, triggerTransition].
 * - active: boolean, pass to <StarkPageTransition active={active} />
 * - triggerTransition: function, call to start the animation
 *   Optionally pass a callback to run at the midpoint (e.g., to navigate while overlay is fully covering)
 *
 * Example:
 *   const [transitioning, triggerTransition] = usePageTransition();
 *   const handleNav = () => {
 *     triggerTransition(() => navigate(...));
 *   }
 */
export default function usePageTransition(duration = 800, midpoint = 0.5) {
    const [active, setActive] = useState(false);
    /**
     * Triggers the transition. If a callback is provided, it will be called at the midpoint of the animation.
     */
    const trigger = useCallback((onMidpoint) => {
        if (!active) {
            setActive(true);
            // Call the callback at the midpoint (default 0.5)
            if (typeof onMidpoint === 'function') {
                setTimeout(onMidpoint, duration * midpoint);
            }
            setTimeout(() => setActive(false), duration);
        }
    }, [active, duration, midpoint]);
    return [active, trigger];
}
