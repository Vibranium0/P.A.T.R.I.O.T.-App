import React, { useRef, useEffect } from "react";
import styles from "../../styles/transitions.module.css";

/**
 * StarkPageTransition
 *
 * Reusable page transition overlay for Sentinel/P.A.T.R.I.O.T. apps.
 *
 * Usage:
 *   <StarkPageTransition active={isTransitioning} direction="left" />
 *
 * - active: boolean, triggers the animation
 * - direction: 'left' | 'right' (default: 'left')
 *
 * Animation intent:
 * - Clean, engineered panel sweep with subtle blue energy wipe
 * - No bounce, deliberate timing, HUD-style overlay
 * - Overlay is pointer-events: none and does not block content
 *
 * To use: trigger `active` when navigating between pages.
 */

/**
 * Props:
 * - active: boolean
 * - direction: 'left' | 'right'
 * - destBackgroundClass: string (optional) - CSS class for the destination page background
 */
const StarkPageTransition = ({ active, direction = "left", destBackgroundClass = "" }) => {
    const overlayRef = useRef(null);
    const bgRef = useRef(null);
    const prevBgRef = useRef(null);
    // Track previous background class for crossfade
    const prevBgClass = useRef("");

    // On mount, set prevBgClass to initial
    useEffect(() => {
        prevBgClass.current = document.body.getAttribute("data-bg-class") || "";
    }, []);

    // On transition start, set prevBgClass to current
    useEffect(() => {
        if (active) {
            prevBgClass.current = document.body.getAttribute("data-bg-class") || "";
        }
    }, [active]);

    // Animate overlay and update mask for destination background
    useEffect(() => {
        let rafId;
        const overlay = overlayRef.current;
        const bg = bgRef.current;
        if (!overlay || !bg) return;

        function setClip(percent) {
            // percent: 0 (start, left) to 1 (end, right)
            // For left swipe: reveal from left to right
            // For right swipe: reveal from right to left
            if (direction === "left") {
                bg.style.setProperty('--swipe-clip', `polygon(0 0, ${percent * 100}% 0, ${percent * 100}% 100%, 0 100%)`);
            } else {
                bg.style.setProperty('--swipe-clip', `polygon(${100 - percent * 100}% 0, 100% 0, 100% 100%, ${100 - percent * 100}% 100%)`);
            }
        }

        if (!active) {
            overlay.classList.remove(styles.transitionActive);
            overlay.style.transform =
                direction === "left"
                    ? "translateX(-100%)"
                    : "translateX(100%)";
            setClip(0);
            return;
        }

        overlay.classList.add(styles.transitionActive);
        // Animate the swipe and update the mask in sync
        let start;
        function animate(ts) {
            if (!start) start = ts;
            const duration = 800; // ms
            const elapsed = Math.min(ts - start, duration);
            // Ease: cubic-bezier(0.7,0,0.3,1)
            const t = elapsed / duration;
            // Approximate cubic-bezier with easeInOutCubic
            const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
            setClip(ease);
            if (elapsed < duration) {
                rafId = requestAnimationFrame(animate);
            } else {
                setClip(1);
            }
        }
        rafId = requestAnimationFrame(animate);
        return () => rafId && cancelAnimationFrame(rafId);
    }, [active, direction, styles.transitionActive]);

    // Animate both backgrounds for crossfade
    useEffect(() => {
        if (!active && bgRef.current && prevBgRef.current) {
            bgRef.current.classList.remove(styles.bgActive);
            prevBgRef.current.classList.remove(styles.bgFadeOut);
            bgRef.current.style.opacity = 0;
            prevBgRef.current.style.opacity = 1;
        }
        if (active && bgRef.current && prevBgRef.current) {
            // Make both backgrounds visible at the start
            bgRef.current.style.opacity = 1;
            prevBgRef.current.style.opacity = 1;
            // Animate destination background in and previous out
            bgRef.current.classList.add(styles.bgActive);
            prevBgRef.current.classList.add(styles.bgFadeOut);
        }
    }, [active, direction, styles.bgActive, styles.bgFadeOut]);

    // Set data-bg-class on body for next transition
    useEffect(() => {
        if (!active && destBackgroundClass) {
            document.body.setAttribute("data-bg-class", destBackgroundClass);
        }
    }, [active, destBackgroundClass]);

    return (
        <>
            {/* Previous background always visible */}
            <div
                ref={prevBgRef}
                className={`${styles.transitionBg} ${prevBgClass.current}`}
                style={{ opacity: active ? 1 : 0, zIndex: 997, pointerEvents: 'none' }}
                aria-hidden="true"
            />
            {/* Destination background is revealed by a mask that follows the overlay */}
            <div
                ref={bgRef}
                className={`${styles.transitionBg} ${destBackgroundClass} ${styles.bgMasked}`}
                style={{ zIndex: 998, pointerEvents: 'none' }}
                aria-hidden="true"
            />
            {/* Masked overlay for the dark .background::after effect */}
            <div
                className={styles.bgMaskedOverlay}
                aria-hidden="true"
                style={{ zIndex: 999, pointerEvents: 'none' }}
            />
            {/* The swipe overlay (above both backgrounds, below HUD) */}
            <div
                ref={overlayRef}
                className={styles.transitionOverlay}
                style={{
                    transform:
                        direction === "left"
                            ? "translateX(-100%)"
                            : "translateX(100%)",
                    pointerEvents: 'none'
                }}
                aria-hidden="true"
            />
        </>
    );
};

export default StarkPageTransition;
