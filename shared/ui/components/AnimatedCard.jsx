import React from "react";
import { motion } from "framer-motion";

/**
 * AnimatedCard/AnimatedFormContainer - Wraps content with a mount animation.
 * Usage: <AnimatedCard>{children}</AnimatedCard>
 */
const mountVariants = {
    hidden: { opacity: 0, y: 32, scale: 0.98 },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { duration: 0.45, ease: "easeOut" }
    }
};

const AnimatedCard = ({ children, style, ...props }) => (
    <motion.div
        initial="hidden"
        animate="visible"
        variants={mountVariants}
        style={style}
        {...props}
    >
        {children}
    </motion.div>
);

export default AnimatedCard;
