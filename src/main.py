"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from typing import List, Dict

from .recommender import load_songs, recommend_songs, USER_PROFILE


# WHY #1 RANKED FIRST — High-Energy Pop
# Genre match (+2.0): "pop" == "pop" ✓
# Mood match (+1.0): "happy" == "happy" ✓
# Energy sim: 1.46/1.50 — song energy 0.82 vs target 0.85, gap of 0.03
# Valence sim: 0.99/1.00 — near-perfect match (song 0.84 vs target 0.85, gap of 0.01)
# Total advantage over #2 (Gym Hero, 5.947): Gym Hero has genre match but not mood match;
#   Sunrise City's +1.0 mood bonus creates the decisive 1.16-pt gap
# Conclusion: fixed match bonuses are the dominant factor, not audio similarity

# WHY #1 RANKED FIRST — Chill Lo-Fi Study
# Genre match (+2.0): "lofi" == "lofi" ✓
# Mood match (+1.0): "chill" == "chill" ✓
# Energy sim: 1.50/1.50 — PERFECT match, song energy 0.35 == target 0.35, gap of 0.00
# Acousticness sim: 0.71/0.75 — song 0.86 vs target 0.80, closer than #2 Midnight Coding
# Total advantage over #2 (Midnight Coding, 7.022): both songs share genre+mood bonus;
#   Library Rain wins by a 0.107-pt margin from perfect energy and closer acousticness
# Conclusion: within a genre-locked tie, continuous feature precision determines the winner

# ─── Default User Profile ────────────────────────────────────────────────────

# USER_PROFILE is imported from src.recommender


# ─── Standard Test Profiles ──────────────────────────────────────────────────

PROFILE_POP = {
    "favorite_genre":          "pop",
    "favorite_mood":           "happy",
    "target_energy":           0.85,
    "target_tempo_bpm":        125.0,
    "target_valence":          0.85,
    "target_danceability":     0.80,
    "target_acousticness":     0.10,
    "target_popularity":       85,
    "target_decade":           2010,
    "target_detailed_mood":    "euphoric",
    "target_instrumentalness": 0.08,
    "target_liveness":         0.08,
}

PROFILE_LOFI = {
    "favorite_genre":          "lofi",
    "favorite_mood":           "chill",
    "target_energy":           0.35,
    "target_tempo_bpm":        75.0,
    "target_valence":          0.55,
    "target_danceability":     0.55,
    "target_acousticness":     0.80,
    "target_popularity":       50,
    "target_decade":           2010,
    "target_detailed_mood":    "dreamy",
    "target_instrumentalness": 0.80,
    "target_liveness":         0.05,
}

PROFILE_ROCK = {
    "favorite_genre":          "rock",
    "favorite_mood":           "intense",
    "target_energy":           0.92,
    "target_tempo_bpm":        155.0,
    "target_valence":          0.40,
    "target_danceability":     0.60,
    "target_acousticness":     0.05,
    "target_popularity":       76,
    "target_decade":           2000,
    "target_detailed_mood":    "aggressive",
    "target_instrumentalness": 0.05,
    "target_liveness":         0.12,
}


# ─── Adversarial Edge Case Profiles ──────────────────────────────────────────

# PROFILE_CONFLICTED
# Edge case: High energy (0.95) paired with a sad mood — tests whether the
#   energy proximity score overrides the mood mismatch.
# The rock genre has NO "sad" songs in the catalog; "Storm Runner"
#   (rock/angry, energy=0.91) competes with "Velvet and Rain" (R&B/sad,
#   energy=0.52) for genre vs. mood signal dominance.
# Expected surprise: Storm Runner ranks #1 despite being "angry" not "sad"
#   because genre match (+2.0) + strong energy proximity outweigh the lone
#   +1.0 mood bonus from Velvet and Rain — energy effectively overrides mood.
# Most likely surfaces: Storm Runner (rock/angry), Velvet and Rain (R&B/sad),
#   Gym Hero (pop/intense).
PROFILE_CONFLICTED = {
    "favorite_genre":          "rock",
    "favorite_mood":           "sad",
    "target_energy":           0.95,
    "target_tempo_bpm":        155.0,
    "target_valence":          0.20,
    "target_danceability":     0.60,
    "target_acousticness":     0.10,
    "target_popularity":       75,
    "target_decade":           2000,
    "target_detailed_mood":    "tense",
    "target_instrumentalness": 0.05,
    "target_liveness":         0.15,
}

# PROFILE_GHOST
# Edge case: Genre ("bossa nova") and mood ("euphoric") match zero songs in
#   the catalog — tests whether the ranker degrades gracefully on pure
#   continuous-feature similarity scores alone.
# No genre or mood bonus is awarded to any song; ranking is determined
#   entirely by energy, valence, acousticness, danceability, and tempo.
# Expected surprise: Songs with mid-range feature values surface even though
#   they have nothing to do with bossa nova or euphoria — "Rooftop Lights"
#   (indie pop/happy) or "Night Drive Loop" (synthwave/moody) may top the
#   list based solely on numeric proximity.
# Most likely surfaces: Rooftop Lights (indie pop), Night Drive Loop
#   (synthwave), Blue Hour Letters (R&B).
PROFILE_GHOST = {
    "favorite_genre":          "bossa nova",
    "favorite_mood":           "euphoric",
    "target_energy":           0.65,
    "target_tempo_bpm":        110.0,
    "target_valence":          0.75,
    "target_danceability":     0.70,
    "target_acousticness":     0.45,
    "target_popularity":       65,
    "target_decade":           2010,
    "target_detailed_mood":    "euphoric",
    "target_instrumentalness": 0.4,
    "target_liveness":         0.2,
}

# PROFILE_FLATLINE
# Edge case: All numeric targets at exactly 0.5; genre and mood absent from
#   the catalog to eliminate categorical signal entirely.
# Tests whether the ranker produces meaningful score separation or a
#   near-tie flat ranking.
# Notable: target_tempo_bpm=0.5 (literally 0.5 BPM) compresses the tempo
#   term — contributions range from ~0.03 (fast songs) to ~0.29 (slow songs),
#   suppressing that dimension and reducing total score spread.
# Expected surprise: Scores may cluster in a narrow ~0.5-point band; rank
#   order is decided by whichever features happen to sit closest to 0.5,
#   producing a nearly arbitrary tie with minimal separation.
# Most likely surfaces: Velvet and Rain (R&B), Blue Hour Letters (R&B),
#   Porch Swing Dusk (country).
PROFILE_FLATLINE = {
    "favorite_genre":          "vapor",
    "favorite_mood":           "nostalgic",
    "target_energy":           0.5,
    "target_tempo_bpm":        0.5,
    "target_valence":          0.5,
    "target_danceability":     0.5,
    "target_acousticness":     0.5,
    "target_popularity":       50,
    "target_decade":           1990,
    "target_detailed_mood":    "",
    "target_instrumentalness": 0.5,
    "target_liveness":         0.5,
}

# PROFILE_EXTREME
# Edge case: Every numeric feature target at maximum (1.0), including
#   tempo_bpm — tests whether high-energy songs dominate regardless of
#   genre/mood preference.
# Notable: target_tempo_bpm=1.0 causes NEGATIVE tempo contributions for any
#   song above ~141 BPM (formula: 0.5*(1 - |bpm-1|/140)), so the fastest
#   songs (Shatter the Sky 172 BPM, Drop the Grid 142 BPM) are penalized.
# With target_acousticness=1.0, "Autumn Sonata" (acousticness=0.97) scores
#   almost perfectly there; combined with the genre match (+2.0 classical),
#   a quiet classical piece can outrank loud electronic tracks.
# Expected surprise: "Autumn Sonata" (energy=0.21, tempo=66) ranks #1 despite
#   all-max numeric targets — the genre bonus + high acousticness outweigh
#   its terrible energy score, inverting the "extreme = high energy" intuition.
# Most likely surfaces: Autumn Sonata (classical), Shatter the Sky (metal),
#   Spacewalk Thoughts (ambient).
PROFILE_EXTREME = {
    "favorite_genre":          "classical",
    "favorite_mood":           "angry",
    "target_energy":           1.0,
    "target_tempo_bpm":        1.0,
    "target_valence":          1.0,
    "target_danceability":     1.0,
    "target_acousticness":     1.0,
    "target_popularity":       100,
    "target_decade":           2020,
    "target_detailed_mood":    "aggressive",
    "target_instrumentalness": 1.0,
    "target_liveness":         1.0,
}

# PROFILE_INVERSE
# Edge case: All preferences are the direct opposite of PROFILE_LOFI —
#   tests whether the system correctly buries lofi songs at the bottom.
# Genre "metal" + mood "angry" point to Shatter the Sky; numeric targets
#   (low acousticness=0.20, low valence=0.45, higher energy=0.65, higher
#   BPM=125) all penalize the slow, acoustic, gentle lofi catalog.
# Expected: lofi tracks (Library Rain, Midnight Coding, Focus Flow) rank last
#   because they receive 0 categorical bonus AND poor continuous-feature
#   scores on every dimension.
# Most likely surfaces: Shatter the Sky (metal/angry), Storm Runner
#   (rock/intense), Drop the Grid (electronic/energetic).
PROFILE_INVERSE = {
    "favorite_genre":          "metal",
    "favorite_mood":           "angry",
    "target_energy":           0.65,
    "target_tempo_bpm":        125.0,
    "target_valence":          0.45,
    "target_danceability":     0.45,
    "target_acousticness":     0.20,
    "target_popularity":       75,
    "target_decade":           2000,
    "target_detailed_mood":    "aggressive",
    "target_instrumentalness": 0.05,
    "target_liveness":         0.2,
}


# ─── Profile Registry ────────────────────────────────────────────────────────

PROFILES = [
    ("High-Energy Pop",               PROFILE_POP),
    ("Chill Lo-Fi Study",             PROFILE_LOFI),
    ("Hard Rock Workout",             PROFILE_ROCK),
    ("Conflicted (Energy vs Mood)",   PROFILE_CONFLICTED),
    ("Ghost (No Catalog Match)",      PROFILE_GHOST),
    ("Flatline (All 0.5 Targets)",    PROFILE_FLATLINE),
    ("Extreme (All 1.0 Targets)",     PROFILE_EXTREME),
    ("Inverse of Lo-Fi",              PROFILE_INVERSE),
]

HEADER_SEP = "\u2550" * 60   # ════════════════════════════════════════════════════════════
ROW_SEP    = "\u2500" * 41   # ─────────────────────────────────────────


def display_recommendations(
    results: List[Dict],
    profile_name: str,
    mode: str,
) -> None:
    """Display recs as a fancy_grid ASCII table via tabulate, or plain text if tabulate is absent."""
    try:
        from tabulate import tabulate  # optional dependency — falls back gracefully
        rows = [
            [
                i,
                rec["title"],
                rec["artist"],
                rec["genre"],
                f"{rec['score']:.3f}",
                mode,
                " | ".join(rec["reasons"][:3]),  # top 3 reasons keep table readable
            ]
            for i, rec in enumerate(results, 1)
        ]
        headers = ["#", "Title", "Artist", "Genre", "Score", "Mode", "Top Reasons"]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    except ImportError:
        for i, rec in enumerate(results, 1):
            reasons_str = " | ".join(rec["reasons"])
            print(ROW_SEP)
            print(f"#{i}  {rec['title']} \u2014 {rec['artist']}")
            print(f"    Score   : {rec['score']}")
            print(f"    Genre   : {rec['genre']:<14} Mood: {rec['mood']}")
            print(f"    Reasons : {reasons_str}")
        print(ROW_SEP)


def main() -> None:
    """Load songs, score them against each test profile, and print results."""
    songs = load_songs("data/songs.csv")

    # ── Challenge 2: High-Energy Pop across all 3 scoring modes ──────────────
    print()
    print("\u2550" * 60)
    print("CHALLENGE 2 — HIGH-ENERGY POP: ALL 3 SCORING MODES")
    print("\u2550" * 60)
    for mode_name in ["genre_first", "mood_first", "energy_focused"]:
        print()
        print(f"  ── Mode: {mode_name} ──")
        recs = recommend_songs(PROFILE_POP, songs, k=5, mode=mode_name, diversity=False)
        display_recommendations(recs, "High-Energy Pop", mode_name)

    # ── Challenge 3: Chill Lo-Fi diversity comparison ─────────────────────────
    print()
    print("\u2550" * 60)
    print("CHALLENGE 3 — CHILL LO-FI: DIVERSITY ON vs OFF")
    print("\u2550" * 60)
    print()
    print("  ── Diversity ON ──")
    recs_on = recommend_songs(PROFILE_LOFI, songs, k=5, diversity=True)
    display_recommendations(recs_on, "Chill Lo-Fi Study", "default")
    print()
    print("  ── Diversity OFF ──")
    recs_off = recommend_songs(PROFILE_LOFI, songs, k=5, diversity=False)
    display_recommendations(recs_off, "Chill Lo-Fi Study", "default")

    # ── All profiles (default mode, diversity on) ─────────────────────────────
    print()
    print("\u2550" * 60)
    print("ALL PROFILES — DEFAULT MODE")
    print("\u2550" * 60)
    for profile_name, user_prefs in PROFILES:
        print()
        print(HEADER_SEP)
        print(f"PROFILE: {profile_name}")
        print(HEADER_SEP)
        recommendations = recommend_songs(user_prefs, songs, k=5)
        display_recommendations(recommendations, profile_name, "default")


if __name__ == "__main__":
    main()
