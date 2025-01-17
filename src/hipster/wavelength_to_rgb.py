def wavelength_to_rgb(wavelength, gamma=0.8):
    """
    Approximate conversion from wavelength (nm) to RGB color.
    Adapted from Dan Bruton's algorithm: http://www.midnightkite.com/color.html
    """

    # Clamp wavelength to the visible range
    if wavelength < 380:
        wavelength = 380
    if wavelength > 780:
        wavelength = 780
    R = G = B = 0.0
    if 380 <= wavelength < 440:
        t = (wavelength - 380) / (440 - 380)
        R = -t
        G = 0.0
        B = 1.0
    elif 440 <= wavelength < 490:
        R = 0.0
        t = (wavelength - 440) / (490 - 440)
        G = t
        B = 1.0
    elif 490 <= wavelength < 510:
        R = 0.0
        G = 1.0
        t = (wavelength - 490) / (510 - 490)
        B = 1.0 - t
    elif 510 <= wavelength < 580:
        R = (wavelength - 510) / (580 - 510)
        G = 1.0
        B = 0.0
    elif 580 <= wavelength < 645:
        R = 1.0
        t = (wavelength - 580) / (645 - 580)
        G = 1.0 - t
        B = 0.0
    elif 645 <= wavelength <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    # Intensity correction near range edges
    if 380 <= wavelength < 420:
        alpha = 0.3 + 0.7 * (wavelength - 380) / 40
    elif 420 <= wavelength <= 700:
        alpha = 1.0
    elif 700 < wavelength <= 780:
        alpha = 0.3 + 0.7 * (780 - wavelength) / 80
    else:
        alpha = 0.0
    # Gamma correction
    R = (R * alpha) ** gamma
    G = (G * alpha) ** gamma
    B = (B * alpha) ** gamma
    return (R, G, B)
