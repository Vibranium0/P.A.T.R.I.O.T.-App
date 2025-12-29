import React, { useEffect } from "react";
import { motion, useAnimation } from "framer-motion";

/**
 * ShakeOnError - Wraps children and triggers a shake animation when `trigger` changes.
 * Usage: <ShakeOnError trigger={error}>{children}</ShakeOnError>
 */
const shakeVariants = {
    still: { x: 0 },
    shake: {
        x: [0, -10, 10, -8, 8, -4, 4, 0],
        transition: { duration: 0.5, ease: "easeInOut" }
    }
};

const ShakeOnError = ({ trigger, children, style, ...props }) => {
    const controls = useAnimation();
    useEffect(() => {
        if (trigger) {
            controls.start("shake");
        }
    }, [trigger, controls]);
    return (
        <motion.div
            animate={controls}
            initial="still"
            variants={shakeVariants}
            style={style}
            {...props}
            onAnimationComplete={() => controls.set("still")}
        >
            {children}
        </motion.div>
    );
};

export default ShakeOnError;
