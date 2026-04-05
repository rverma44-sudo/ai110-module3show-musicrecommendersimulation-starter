"""
Music recommender module: load songs from CSV and score/rank them for a user profile.
"""

import csv
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 70
    release_decade: int = 2010
    detailed_mood: str = ""
    instrumentalness: float = 0.2
    liveness: float = 0.1


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_popularity: int = 70
    target_decade: int = 2010
    target_detailed_mood: str = ""
    target_instrumentalness: float = 0.2
    target_liveness: float = 0.1


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]) -> None:
        """Initialize the Recommender with a catalog of Song objects."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects for the given UserProfile (placeholder)."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why song was recommended to user (placeholder)."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with typed fields."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Songs CSV not found at '{path.resolve()}'. "
            "Ensure you are running from the project root and the file exists."
        )

    songs: List[Dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "popularity":       int(row["popularity"]),
                "release_decade":   int(row["release_decade"]),
                "detailed_mood":    row["detailed_mood"],
                "instrumentalness": float(row["instrumentalness"]),
                "liveness":         float(row["liveness"]),
            })

    print(f"Loaded songs: {len(songs)}")
    return songs


# EXPERIMENT RESULTS
# Weight Shift (genre 2.0→1.0, energy 1.5→3.0):
#   High-Energy Pop  — #1 Sunrise City (7.56), #2 Gym Hero (6.327), #3 Rooftop Lights (6.239)
#   Hard Rock Workout — #1 Storm Runner (7.562), #2 Gym Hero (6.128), #3 Shatter the Sky (5.397)
#   Doubling energy weight caused non-genre songs with strong energy (Rooftop Lights,
#   Shatter the Sky) to climb dramatically, nearly closing the gap to genre-matched leaders —
#   rankings became less genre-dependent because continuous energy scores began to
#   rival the fixed categorical bonus.
#
# Feature Removal (mood check disabled):
#   High-Energy Pop  — #1 Sunrise City (6.105), #2 Gym Hero (5.947), #3 Block Party (3.976)
#   Hard Rock Workout — #1 Storm Runner (6.077), #2 Shatter the Sky (3.972), #3 Drop the Grid (3.694)
#   Removing mood check caused Gym Hero to fall from #2 (4.643) to #4 (3.643) in Rock Workout,
#   and Rooftop Lights to fall from #3 (4.874) to #4 (3.874) in High-Energy Pop —
#   top results shifted toward pure energy-proximity ordering, with mood-reliant songs
#   losing their decisive advantage over acoustically-similar but wrong-genre tracks.
#
# Conclusion: the most sensitive weight is energy because doubling it from 1.5→3.0 produced
#   the largest visible reshuffling (Rooftop Lights from 4.874 to 6.239, nearly tying
#   genre-matched Gym Hero at 6.327), demonstrating that the energy term can overpower
#   the genre categorical bonus once its coefficient exceeds the bonus magnitude.


# Default weights mirror the original hardcoded scoring constants.
WEIGHTS: Dict[str, float] = {
    "genre_match":       2.0,
    "mood_match":        1.0,
    "energy_sim":        1.5,
    "valence_sim":       1.0,
    "acousticness_sim":  0.75,
    "danceability_sim":  0.5,
    "tempo_sim":         0.5,
    "popularity_sim":    1.0,
    "decade_sim":        0.75,
    "detailed_mood":     1.5,
    "instrumentalness":  0.5,
    "liveness_sim":      0.5,
}

# Strategy pattern: each mode is a named weights dict that score_song applies uniformly,
# letting callers swap scoring emphasis by name without modifying any core scoring logic.
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "genre_first": {
        "genre_match":       4.0,   # doubled from default — genre is the dominant factor
        "mood_match":        1.0,
        "detailed_mood":     1.0,
        "energy_sim":        0.75,
        "valence_sim":       0.5,
        "acousticness_sim":  0.5,
        "danceability_sim":  0.25,
        "tempo_sim":         0.25,
        "popularity_sim":    0.5,
        "decade_sim":        0.25,
        "instrumentalness":  0.25,
        "liveness_sim":      0.25,
    },
    "mood_first": {
        "genre_match":       1.0,
        "mood_match":        2.5,   # heavily weighted — mood matters more than genre
        "detailed_mood":     3.0,   # dominant factor — fine-grained emotion drives ranking
        "energy_sim":        1.0,
        "valence_sim":       1.5,
        "acousticness_sim":  0.5,
        "danceability_sim":  0.5,
        "tempo_sim":         0.25,
        "popularity_sim":    0.5,
        "decade_sim":        0.25,
        "instrumentalness":  0.25,
        "liveness_sim":      0.25,
    },
    "energy_focused": {
        "genre_match":       1.0,
        "mood_match":        0.5,
        "detailed_mood":     0.5,
        "energy_sim":        4.0,   # dominant factor — perceived intensity drives ranking
        "valence_sim":       1.0,
        "acousticness_sim":  1.0,
        "danceability_sim":  1.5,
        "tempo_sim":         1.5,
        "popularity_sim":    0.5,
        "decade_sim":        0.25,
        "instrumentalness":  0.5,
        "liveness_sim":      0.5,
    },
}


USER_PROFILE: Dict = {
    "favorite_genre":          "pop",
    "favorite_mood":           "happy",
    "target_energy":           0.80,
    "target_valence":          0.7,
    "target_acousticness":     0.2,
    "target_danceability":     0.75,
    "target_tempo_bpm":        120.0,
    "target_popularity":       75,
    "target_decade":           2010,
    "target_detailed_mood":    "euphoric",
    "target_instrumentalness": 0.1,
    "target_liveness":         0.1,
}


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict] = None,
) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (total_score, reasons)."""
    if weights is None:
        weights = WEIGHTS

    score = 0.0
    reasons: List[str] = []

    # +genre_match for exact genre match — strongest categorical signal
    if user_prefs["favorite_genre"] == song["genre"]:
        score += weights["genre_match"]
        reasons.append(f"genre match (+{weights['genre_match']:.1f})")

    # +mood_match for exact mood match — strong categorical signal, weighted less than genre
    if user_prefs["favorite_mood"] == song["mood"]:
        score += weights["mood_match"]
        reasons.append(f"mood match (+{weights['mood_match']:.1f})")

    # +energy_sim max for energy proximity — most impactful continuous feature (perceived intensity)
    energy_contrib = weights["energy_sim"] * (1 - abs(song["energy"] - user_prefs["target_energy"]) / 1.0)
    score += energy_contrib
    reasons.append(f"energy similarity: {energy_contrib:.2f}/{weights['energy_sim']:.2f}")

    # +valence_sim max for valence proximity — emotional positivity alignment
    valence_contrib = weights["valence_sim"] * (1 - abs(song["valence"] - user_prefs.get("target_valence", 0.7)) / 1.0)
    score += valence_contrib
    reasons.append(f"valence similarity: {valence_contrib:.2f}/{weights['valence_sim']:.2f}")

    # +acousticness_sim max for acousticness proximity — production texture/style fit
    acoustic_contrib = weights["acousticness_sim"] * (1 - abs(song["acousticness"] - user_prefs.get("target_acousticness", 0.2)) / 1.0)
    score += acoustic_contrib
    reasons.append(f"acousticness similarity: {acoustic_contrib:.2f}/{weights['acousticness_sim']:.2f}")

    # +danceability_sim max for danceability proximity — rhythmic energy alignment
    dance_contrib = weights["danceability_sim"] * (1 - abs(song["danceability"] - user_prefs.get("target_danceability", 0.75)) / 1.0)
    score += dance_contrib
    reasons.append(f"danceability similarity: {dance_contrib:.2f}/{weights['danceability_sim']:.2f}")

    # +tempo_sim max for tempo proximity — normalized over 60–200 BPM range (span = 140)
    tempo_contrib = weights["tempo_sim"] * (1 - abs(song["tempo_bpm"] - user_prefs.get("target_tempo_bpm", 120.0)) / 140.0)
    score += tempo_contrib
    reasons.append(f"tempo similarity: {tempo_contrib:.2f}/{weights['tempo_sim']:.2f}")

    # +popularity_sim max for popularity proximity — aligns mainstream vs. niche preference
    pop_target = user_prefs.get("target_popularity", 70)
    pop_contrib = weights["popularity_sim"] * (1 - abs(song["popularity"] - pop_target) / 100.0)  # normalized over 0–100 scale
    score += pop_contrib
    reasons.append(f"popularity similarity: {pop_contrib:.2f}/{weights['popularity_sim']:.2f}")

    # +decade_sim max for release decade proximity — reflects era/production-style preference
    decade_target = user_prefs.get("target_decade", 2010)
    decade_contrib = weights["decade_sim"] * (1 - abs(song["release_decade"] - decade_target) / 60.0)  # normalized over 1960–2020 span
    score += decade_contrib
    reasons.append(f"decade similarity: {decade_contrib:.2f}/{weights['decade_sim']:.2f}")

    # +detailed_mood for exact detailed mood string match — fine-grained emotional alignment
    target_dm = user_prefs.get("target_detailed_mood", "")
    if target_dm and target_dm == song["detailed_mood"]:  # only award points when user has a preference
        score += weights["detailed_mood"]
        reasons.append(f"detailed mood match (+{weights['detailed_mood']:.1f})")

    # +instrumentalness max for instrumentalness proximity — vocal vs. instrumental preference
    inst_target = user_prefs.get("target_instrumentalness", 0.2)
    inst_contrib = weights["instrumentalness"] * (1 - abs(song["instrumentalness"] - inst_target) / 1.0)  # normalized over 0.0–1.0 scale
    score += inst_contrib
    reasons.append(f"instrumentalness similarity: {inst_contrib:.2f}/{weights['instrumentalness']:.2f}")

    # +liveness_sim max for liveness proximity — studio vs. live recording preference
    live_target = user_prefs.get("target_liveness", 0.1)
    live_contrib = weights["liveness_sim"] * (1 - abs(song["liveness"] - live_target) / 1.0)  # normalized over 0.0–1.0 scale
    score += live_contrib
    reasons.append(f"liveness similarity: {live_contrib:.2f}/{weights['liveness_sim']:.2f}")

    return round(score, 3), reasons


def apply_diversity_penalty(
    ranked: list[dict],
    artist_penalty: float = 0.5,
    genre_penalty: float = 0.3,
    max_per_artist: int = 1,
    max_per_genre: int = 2,
) -> list[dict]:
    """Apply artist and genre repeat penalties to a pre-sorted recommendation list and re-sort."""
    # Penalties are applied post-sort so the top-ranked song claims its artist/genre slot first;
    # if applied during scoring every candidate would be penalized before rank order is known,
    # making it impossible to fairly honor which song "earned" the unpenalized slot.
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    for song in ranked:
        artist = song["artist"]
        genre = song["genre"]

        if artist_counts.get(artist, 0) >= max_per_artist:
            song["score"] = round(song["score"] * (1 - artist_penalty), 3)
            song["reasons"].append("artist repeat penalty (−50%)")

        if genre_counts.get(genre, 0) >= max_per_genre:
            song["score"] = round(song["score"] * (1 - genre_penalty), 3)
            song["reasons"].append("genre repeat penalty (−30%)")

        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return sorted(ranked, key=lambda s: s["score"], reverse=True)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "default",
    diversity: bool = True,
) -> List[Dict]:
    """Score all songs and return the top-k results as enriched dicts with 'score' and 'reasons'."""
    weights = SCORING_MODES.get(mode, WEIGHTS)

    # Collect (score, reasons, song) for every track in the catalog
    scored: List[Tuple[Tuple[float, List[str]], Dict]] = [
        (score_song(user_prefs, song, weights), song) for song in songs
    ]

    # sorted() is preferred over .sort() because it returns a new list,
    # preserving the original catalog unchanged — safe for repeated calls
    # with different k or user profiles.
    ranked_sorted = sorted(scored, key=lambda item: item[0][0], reverse=True)

    results: List[Dict] = []
    for (song_score, song_reasons), song in ranked_sorted:
        result = dict(song)          # copy so original catalog entry is not mutated
        result["score"] = song_score
        result["reasons"] = list(song_reasons)
        results.append(result)

    # Apply diversity penalty before slicing so penalized songs can drop out of top-k
    if diversity:
        results = apply_diversity_penalty(results)

    # Handle k > total songs gracefully by capping at len(songs)
    return results[:k]
