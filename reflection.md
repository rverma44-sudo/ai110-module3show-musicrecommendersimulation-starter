# Reflection: Music Recommender Simulation

## High-Energy Pop vs Chill Lo-Fi Study

When we tested two total opposites—a high-energy pop profile and a relaxed lo-fi one—the system perfectly flipped its recommendations. It confidently matched the best tracks to each vibe, proving the scoring logic works beautifully for extremes. However, this success also highlights a hidden catch: the system is only as good as the songs available in its catalog.
## Hard Rock Workout vs Conflicted (Energy vs Mood)

We threw a curveball at the system by asking for "sad" hard rock, a combination that didn't actually exist in our catalog. The results showed that genre and energy scores completely overpowered the mood requirement, pushing intense rock songs to the top while burying the only genuinely sad track. It’s a noticeable flaw, as someone looking for a sad song shouldn't end up with angry metal just because the genres match.
## Ghost (No Catalog Match) vs Flatline (All 0.5 Targets)

We also tested profiles with completely unmatched genres and moods to see what would happen. When the profile still had specific audio preferences, the system adapted gracefully and found decent matches based on the song's actual sound. However, when a profile had completely neutral preferences across the board, the system stubbornly ranked the songs anyway, exposing its inability to simply say, "I don't know."
## Extreme (All 1.0 Targets) vs Inverse of Lo-Fi

We tried an "Extreme" profile by maxing out every value to 1.0, expecting loud, fast music, but surprisingly got a slow classical piece instead. This happened because setting the target tempo to literally one beat per minute severely penalized fast songs, whereas a standard, well-rounded profile worked exactly as intended. Ultimately, the system shines when your preferences make logical sense, but it easily breaks down if you feed it physically unrealistic numbers.
## Summary: Biggest Strength and Biggest Weakness

Overall, the project's biggest strength is its total transparency, making it easy to explain why a song was recommended when your preferences align with the catalog. On the flip side, its biggest weakness is the massive point bonus it awards just for matching a genre. This creates a rigid wall that prevents you from discovering great songs outside your usual tastes, and artificially props up bad songs simply because they fit the right category.