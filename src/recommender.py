"""
Music recommender module: load songs from CSV and score/rank them for a user profile.
"""

import csv
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


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


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
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
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })

    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (total_score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    # +2.0 for exact genre match — strongest categorical signal
    if user_prefs["favorite_genre"] == song["genre"]:
        score += 2.0
        reasons.append("genre match (+2.0)")

    # +1.0 for exact mood match — strong categorical signal, weighted less than genre
    if user_prefs["favorite_mood"] == song["mood"]:
        score += 1.0
        reasons.append("mood match (+1.0)")

    # +1.5 max for energy proximity — most impactful continuous feature (perceived intensity)
    energy_contrib = 1.5 * (1 - abs(song["energy"] - user_prefs["target_energy"]) / 1.0)
    score += energy_contrib
    reasons.append(f"energy similarity: {energy_contrib:.2f}/1.50")

    # +1.0 max for valence proximity — emotional positivity alignment
    valence_contrib = 1.0 * (1 - abs(song["valence"] - user_prefs.get("target_valence", 0.7)) / 1.0)
    score += valence_contrib
    reasons.append(f"valence similarity: {valence_contrib:.2f}/1.00")

    # +0.75 max for acousticness proximity — production texture/style fit
    acoustic_contrib = 0.75 * (1 - abs(song["acousticness"] - user_prefs.get("target_acousticness", 0.2)) / 1.0)
    score += acoustic_contrib
    reasons.append(f"acousticness similarity: {acoustic_contrib:.2f}/0.75")

    # +0.5 max for danceability proximity — rhythmic energy alignment
    dance_contrib = 0.5 * (1 - abs(song["danceability"] - user_prefs.get("target_danceability", 0.75)) / 1.0)
    score += dance_contrib
    reasons.append(f"danceability similarity: {dance_contrib:.2f}/0.50")

    # +0.5 max for tempo proximity — normalized over 60–200 BPM range (span = 140)
    tempo_contrib = 0.5 * (1 - abs(song["tempo_bpm"] - user_prefs.get("target_tempo_bpm", 120.0)) / 140.0)
    score += tempo_contrib
    reasons.append(f"tempo similarity: {tempo_contrib:.2f}/0.50")

    return round(score, 3), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Dict]:
    """Score all songs and return the top-k results as enriched dicts with 'score' and 'reasons'."""
    # Collect (score, reasons, song) for every track in the catalog
    scored: List[Tuple[Tuple[float, List[str]], Dict]] = [
        (score_song(user_prefs, song), song) for song in songs
    ]

    # sorted() is preferred over .sort() because it returns a new list,
    # preserving the original catalog unchanged — safe for repeated calls
    # with different k or user profiles.
    ranked = sorted(scored, key=lambda item: item[0][0], reverse=True)

    # Handle k > total songs gracefully by capping at len(songs)
    top_k = ranked[:k]

    results: List[Dict] = []
    for (song_score, song_reasons), song in top_k:
        result = dict(song)          # copy so original catalog entry is not mutated
        result["score"] = song_score
        result["reasons"] = song_reasons
        results.append(result)

    return results
