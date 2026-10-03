# ---------------------------------------------------------
# CLSI M100-Ed36 (2026) disk-diffusion breakpoints
# ---------------------------------------------------------
#
# Method:
#   Kirby-Bauer disk diffusion
#   CLSI M02 / M100-Ed36
#
# Zone diameter is measured in mm.
#
# Only organism/antibiotic combinations for which a
# current CLSI disk-diffusion breakpoint is applicable
# are included.
#
# IMPORTANT:
# Do not use this file as a substitute for the current
# CLSI document or laboratory verification/QC procedures.
# ---------------------------------------------------------


BREAKPOINTS = {

    # =====================================================
    # Pseudomonas aeruginosa
    # =====================================================

    "Pseudomonas aeruginosa": {

        "Amikacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 17,
            "I": 15,
            "R": 14,
            "comment": "Report only for urinary isolates."
        },

        "Ciprofloxacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "5 µg",
            "S": 25,
            "I": 19,
            "R": 18
        },

        "Levofloxacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "5 µg",
            "S": 22,
            "I": 15,
            "R": 14
        },

        "Cefepime": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 18,
            "I": 15,
            "R": 14
        },

        "Ceftazidime": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 18,
            "I": 15,
            "R": 14
        },

        "Piperacillin-Tazobactam": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "100/10 µg",
            "S": 22,
            "I": 18,
            "R": 17
        },

        "Imipenem": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "10 µg",
            "S": 19,
            "I": 16,
            "R": 15
        },

        "Meropenem": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "10 µg",
            "S": 19,
            "I": 16,
            "R": 15
        },

        "Aztreonam": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 22,
            "I": 16,
            "R": 15
        },

        "Ofloxacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "5 µg",
            "S": 16,
            "I": 13,
            "R": 12
        }
    },


    # =====================================================
    # Acinetobacter calcoaceticus-baumannii complex
    # =====================================================

    "Acinetobacter calcoaceticus baumannii complex": {

        "Amikacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 20,
            "I": 17,
            "R": 16
        },

        "Gentamicin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "10 µg",
            "S": 19,
            "I": 14,
            "R": 13
        },

        "Ciprofloxacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "5 µg",
            "S": 21,
            "I": 16,
            "R": 15
        },

        "Levofloxacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "5 µg",
            "S": 17,
            "I": 14,
            "R": 13
        },

        "Cefepime": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 18,
            "I": 15,
            "R": 14
        },

        "Ceftazidime": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 18,
            "I": 15,
            "R": 14
        },

        "Piperacillin-Tazobactam": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "100/10 µg",
            "S": 21,
            "I": 18,
            "R": 17
        },

        "Imipenem": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "10 µg",
            "S": 22,
            "I": 19,
            "R": 18
        },

        "Meropenem": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "10 µg",
            "S": 18,
            "I": 15,
            "R": 14
        }
    },


    # =====================================================
    # Stenotrophomonas maltophilia
    # =====================================================

    "Stenotrophomonas maltophilia": {

        "Levofloxacin": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "5 µg",
            "S": 17,
            "I": 14,
            "R": 13
        },

        "Minocycline": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 26,
            "I": 21,
            "R": 20
        },

        "Trimethoprim-Sulfamethoxazole": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "1.25/23.75 µg",
            "S": 16,
            "I": 11,
            "R": 10
        },

        "Cefiderocol": {
            "method": "disk",
            "standard": "CLSI M100",
            "version": "Ed36 (2026)",
            "disk": "30 µg",
            "S": 17,
            "I": None,
            "R": None
        }
    },


    # =====================================================
    # Burkholderia cepacia complex
    # =====================================================
    #
    # CLSI M100-Ed36 does NOT provide disk-diffusion
    # breakpoints for B. cepacia complex.
    #
    # Therefore this organism intentionally has no
    # disk breakpoints here.
    #

    "Burkholderia cepacia complex": {},


    # =====================================================
    # Other
    # =====================================================

    "Other": {}
}


def interpret_zone(organism, antibiotic, zone):
    """
    Interpret a disk-diffusion zone diameter.

    Returns:
        "S" = Susceptible
        "I" = Intermediate
        "R" = Resistant
        None = no applicable breakpoint
    """

    try:
        zone = float(zone)
    except (ValueError, TypeError):
        return None

    organism_data = BREAKPOINTS.get(organism)

    if not organism_data:
        return None

    antibiotic_data = organism_data.get(antibiotic)

    if not antibiotic_data:
        return None

    susceptible = antibiotic_data.get("S")
    intermediate = antibiotic_data.get("I")
    resistant = antibiotic_data.get("R")

    if susceptible is None:
        return None

    # Susceptible
    if zone >= susceptible:
        return "S"

    # Intermediate
    if intermediate is not None and zone >= intermediate:
        return "I"

    # Resistant
    if resistant is not None and zone <= resistant:
        return "R"

    return None
