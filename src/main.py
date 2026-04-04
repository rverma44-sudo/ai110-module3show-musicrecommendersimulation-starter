"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    """Load songs, score them against the default user profile, and print top-5."""
    songs = load_songs("data/songs.csv")

    # Default user profile for the test run
    user_prefs = {
        "favorite_genre":     "pop",
        "favorite_mood":      "happy",
        "target_energy":      0.80,
        "target_valence":     0.7,
        "target_acousticness": 0.2,
        "target_danceability": 0.75,
        "target_tempo_bpm":   120.0,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    SEP = "\u2500" * 41   # exactly 41 ─ characters

    print()
    for i, rec in enumerate(recommendations, 1):
        reasons_str = " | ".join(rec["reasons"])
        print(SEP)
        print(f"#{i}  {rec['title']} \u2014 {rec['artist']}")
        print(f"    Score   : {rec['score']}")
        print(f"    Genre   : {rec['genre']:<14} Mood: {rec['mood']}")
        print(f"    Reasons : {reasons_str}")
    print(SEP)


if __name__ == "__main__":
    main()
