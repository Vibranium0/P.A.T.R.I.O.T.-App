# Email Verification Page Theme Configuration
# Separate theme for the email verification page displayed after clicking verification links

VERIFICATION_THEME = {
    # Colors
    "background": "#0A3C44",  # Deep Tech Teal
    "interactive": "#00A5BD",  # Circuit Cyan (glow elements)
    "primary": "#D19A22",      # Sentinel Gold (buttons/highlights)
    "borders": "#7B1E12",      # Forged Red (borders/panels/cards)
    "text_light": "#FFFFFF",   # White text
    "text_dark": "#2C2C2C",    # Iron Black text
    
    # Gradient colors
    "gradient_start": "#D19A22",  # Sentinel Gold
    "gradient_end": "#B87333",    # Burnished Copper
    
    # Fonts (matching main app)
    "font_family": "'Poppins', sans-serif",
}

def get_verification_styles():
    """Generate CSS styles for the verification page"""
    theme = VERIFICATION_THEME
    
    return f"""
        body {{
            font-family: {theme['font_family']};
            margin: 0;
            padding: 0;
            background-color: {theme['background']};
            color: {theme['text_light']};
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        .background-logo {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('/static/sentinel_logo.png');
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 0.1;
            pointer-events: none;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 40px;
            position: relative;
            z-index: 10;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .title {{
            color: {theme['text_light']};
            margin-bottom: 20px;
            font-weight: bold;
            font-size: 32px;
        }}
        .message {{
            color: {theme['text_light']};
            line-height: 1.6;
            margin-bottom: 30px;
            opacity: 0.95;
            font-size: 16px;
        }}
        .btn {{
            display: inline-block;
            background-color: {theme['interactive']};
            color: {theme['text_light']};
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 165, 189, 0.4);
        }}
        .btn:hover {{
            background-color: {theme['primary']};
            box-shadow: 0 0 25px rgba(209, 154, 34, 0.6);
            transform: translateY(-2px);
        }}
        .app-name {{
            font-size: 36px;
            font-weight: bold;
            color: {theme['text_light']};
            margin-bottom: 30px;
            letter-spacing: 3px;
        }}
    """
