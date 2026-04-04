USER_PROFILE = {
    "favorite_genre":       "rock",
    "favorite_mood":        "intense",
    "target_energy":        0.85,
    "target_tempo_bpm":     140,
    "target_valence":       0.50,
    "target_danceability":  0.60,
    "target_acousticness":  0.10
}

"""
ML ENGINEER CRITIQUE — USER_PROFILE
=====================================

1. DIFFERENTIATION TEST
   Comparing "Storm Runner" (rock/intense) vs "Midnight Coding" (lofi/chill):

   Feature            Rock    Lofi    Delta   Profile Target   Rock Gap   Lofi Gap
   energy             0.91    0.42    0.49    0.85             0.06       0.43
   tempo_bpm          152     78      74      140              12         62
   acousticness       0.10    0.71    0.61    0.10             0.00       0.61

   Verdict: YES, this profile separates the two cleanly. Energy and acousticness
   each contribute large deltas. Tempo reinforces the signal. The three together
   make misclassification essentially impossible on this dataset.

2. NARROWNESS RISK
   target_acousticness = 0.10 is the riskiest value. Of 18 songs, only 4 score
   below 0.15 on acousticness (Storm Runner 0.10, Gym Hero 0.05, Voltage 0.03,
   Iron Hollow 0.04). Every acoustic/folk/classical song will be heavily penalized
   on this feature alone, which is intentional — but if the Gaussian sigma is set
   tight (e.g., 0.15), even songs at 0.22 (Night Drive) take a significant hit,
   narrowing the useful ranking to just a handful of songs.

   target_tempo_bpm = 140 is also aggressive. Only "Voltage" (electronic, 142 bpm)
   and "Iron Hollow" (metal, 172 bpm) are near this target. "Storm Runner" at 152
   is reasonably close, but most rock songs in a real catalog sit at 120–140 bpm.
   This won't break the recommender but will under-score mid-tempo rock.

3. MISSING SIGNAL
   target_valence = 0.50 is set to neutral and won't differentiate anything.
   Valence is the clearest marker of emotional tone — "intense/angry" songs
   (Storm Runner 0.48, Iron Hollow 0.29) cluster below 0.50, while happy/romantic
   songs cluster above 0.70. Setting target_valence to ~0.35 would actively
   reward dark, intense songs and penalize upbeat ones, adding a meaningful
   second dimension to mood matching beyond the categorical "favorite_mood" key.

4. SUGGESTED FIX
   Lower target_valence from 0.50 to 0.35:

       "target_valence": 0.35,   # was 0.50

   Why: The user's stated preference is "intense rock," which consistently maps to
   low valence in the dataset (Storm Runner 0.48, Iron Hollow 0.29, Night Drive 0.49).
   A neutral 0.50 target means valence contributes near-zero signal — every song
   looks equally good on this axis. Shifting to 0.35 turns valence into a meaningful
   tiebreaker that rewards dark/intense songs without changing the dominant energy
   and acousticness signals that already drive the core separation.
"""


def score_song(song: dict, profile: dict) -> float:
    """Score a single song against a user profile; higher score = better match."""

    # Weights encode relative importance: genre is the primary axis, mood is secondary,
    # energy is the most discriminating continuous feature, acousticness separates
    # electric from acoustic catalogs cleanly, valence encodes emotional tone,
    # tempo and danceability add texture but overlap with energy so they get half weight.
    WEIGHTS = {
        "genre_match":      2.00,  # dominant preference — genre organizes the entire catalog
        "mood_match":       1.00,  # secondary categorical filter, narrows within genre
        "energy_sim":       1.50,  # strongest continuous separator: intense songs cluster 0.87–0.97
        "valence_sim":      1.00,  # emotional brightness proxy; equals mood_match weight to reinforce tone
        "tempo_sim":        0.50,  # correlated with energy; half weight avoids double-counting
        "danceability_sim": 0.50,  # broad mid-range distribution; half weight reduces noise
        "acousticness_sim": 0.75,  # bimodal (electric 0.03–0.22 vs acoustic 0.71–0.97); clear separator
    }

    score = 0.0  # accumulate weighted contributions from all features

    # --- Categorical features: binary match, full weight or zero ---

    # Genre match: exact string equality only; partial matches (e.g. "indie pop" vs "pop")
    # are intentionally not rewarded to keep scoring deterministic and profile-driven.
    score += WEIGHTS["genre_match"] if song["genre"] == profile["favorite_genre"] else 0.0

    # Mood match: same binary logic; mood is a categorical label, not a spectrum here.
    score += WEIGHTS["mood_match"] if song["mood"] == profile["favorite_mood"] else 0.0

    # --- Continuous features: weight × (1 − |song_value − target| / max_possible_range) ---
    # Formula produces [0, weight] for each term: 0 = maximally wrong, weight = perfect match.
    # Using fixed ranges (not dataset-derived stats) keeps scores stable as catalog grows.

    # Energy: range 0.0–1.0 (unitless), so max_possible_range = 1.0
    score += WEIGHTS["energy_sim"] * (1 - abs(song["energy"] - profile["target_energy"]) / 1.0)

    # Valence: range 0.0–1.0; low valence (≈0.3) = dark/intense, high valence (≈0.8) = bright/happy
    score += WEIGHTS["valence_sim"] * (1 - abs(song["valence"] - profile["target_valence"]) / 1.0)

    # Tempo: fixed range 60–200 BPM (covers virtually all music); range = 140
    # Using fixed bounds instead of dataset min/max so scores don't shift when catalog expands.
    score += WEIGHTS["tempo_sim"] * (1 - abs(song["tempo_bpm"] - profile["target_tempo_bpm"]) / (200 - 60))

    # Danceability: range 0.0–1.0; mid-range values are common so signal is noisy — hence low weight
    score += WEIGHTS["danceability_sim"] * (1 - abs(song["danceability"] - profile["target_danceability"]) / 1.0)

    # Acousticness: range 0.0–1.0; most discriminating feature for electric-targeting profiles
    # because the distribution is bimodal — even 0.75 weight produces large score gaps
    score += WEIGHTS["acousticness_sim"] * (1 - abs(song["acousticness"] - profile["target_acousticness"]) / 1.0)

    # Round to 3 decimal places: suppresses floating-point noise while preserving enough
    # precision to distinguish close scores (minimum meaningful step ≈ 0.004 given weight scale)
    return round(score, 3)
