# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**SonicViber 1.0**

---

## 2. Intended Use

Simply enter your favorite genre, mood, and preferred vibe, and the system will score every song to find your top five closest matches. It even breaks down the results with specific scores and reasons, giving you total transparency into exactly why each track was recommended for you.

### Non-Intended Use

This system is not built for real-world music apps or massive catalogs that need to process unpredictable user data at scale.
---

## 3. How the Model Works

To find your perfect track, the system scores each song based on how well it matches your tastes. Nailing your preferred genre gives the biggest point boost, and hitting the right mood also adds a flat bonus. Meanwhile, features like energy and tempo earn more points the closer they get to your exact vibe, without any harsh cutoffs.
---

## 4. Data

Our catalog features 18 songs categorized by genre, mood, and five specific audio traits (energy, tempo_bpm, valence, danceability, acousticness), though an uneven mix gives lo-fi tracks an unfair scoring advantage. Since the system relies purely on a hand-written taste profile rather than real listening data, it can't naturally learn or adapt to your evolving music habits over time.
---

## 5. Strengths

This project is perfect for classrooms, prototypes, or anyone curious about how score-based recommenders actually work under the hood. Its transparent logic and simple CSV setup make it incredibly easy to trace and learn from.
---

## 6. Limitations and Bias

The system's massive genre bonus can completely skew your results, like prioritizing an angry rock track over a genuinely sad song or pushing a quiet classical piece to the top of a high-energy profile. Furthermore, if the system can't find any solid matches, it won't just admit defeat. Instead, it confidently spits out an essentially random, closely tied list of tracks as if they were perfect recommendations.
---

## 7. Evaluation

We tested a mix of standard and extreme profiles — including High-Energy Pop, Chill Lo-Fi Study, and Hard Rock Workout — to uncover weak spots in the system's scoring logic. The weirdest outcome was Autumn Sonata taking the top spot on a profile with totally maxed-out targets. This perfectly highlights the system's biggest quirk: the massive genre bonus can easily overpower a terrible audio match, resulting in recommendations that just feel wrong.
---

## 8. Future Work

To fix the system's flaws, we should swap the rigid genre bonus for a sliding scale, allowing tracks with similar styles to compete fairly. We also need to add a warning when a requested vibe isn't in the catalog, along with a minimum score requirement so the system stops spitting out weak, random recommendations when no true match exists.
---

## 9. Personal Reflection  

My biggest learning moment was seeing exactly how a score-based recommender works under the hood, and realizing that a massive, rigid genre bonus can easily overpower a terrible audio match. While AI tools are great for drafting these kinds of prototypes, I had to strictly double-check the scoring logic when extreme profiles confidently spit out completely wrong tracks, like a slow classical piece for maxed-out energy targets. It was surprising to see how a simple math equation calculating the closeness of audio traits can genuinely "feel" like a personalized recommendation, flawlessly flipping results between high-energy pop and chill lo-fi profiles. If I extended this project, I would replace the fixed genre bonus with a flexible sliding scale, establish a minimum score floor to stop the system from randomly guessing, and add user warnings when their requested vibe isn't actually in the catalog.