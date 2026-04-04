```mermaid
flowchart TD

    %% ── Input layer ──────────────────────────────────────────────────────────
    A([USER_PROFILE dict\nfavorite_genre · favorite_mood\ntarget_energy · target_tempo_bpm\ntarget_valence · target_danceability\ntarget_acousticness])
    B([songs.csv\n18 rows · 10 columns])

    A -- load profile --> C
    B -- parse rows --> C

    %% ── Process All Songs ────────────────────────────────────────────────────
    subgraph PAL [Process All Songs]
        direction TD
        C[Initialize results list] -- begin loop --> D[Fetch next song row]

        %% ── Score Single Song ────────────────────────────────────────────────
        subgraph SSS [Score Single Song]
            direction TD
            G1{Genre match?\nsong.genre == profile.favorite_genre}
            G2{Mood match?\nsong.mood == profile.favorite_mood}
            E1[energy_sim\n1.5 × 1 − |song.energy − target_energy|]
            E2[valence_sim\n1.0 × 1 − |song.valence − target_valence|]
            E3[tempo_sim\n0.5 × 1 − |song.tempo_bpm − target_tempo_bpm| ÷ 140]
            E4[danceability_sim\n0.5 × 1 − |song.danceability − target_danceability|]
            E5[acousticness_sim\n0.75 × 1 − |song.acousticness − target_acousticness|]
            SUM[Sum all components\ntotal_score = genre + mood\n+ energy + valence + tempo\n+ danceability + acousticness]

            G1 -- yes → +2.0 --> G2
            G1 -- no → +0.0 --> G2
            G2 -- yes → +1.0 --> E1
            G2 -- no → +0.0 --> E1
            E1 -- energy score --> E2
            E2 -- valence score --> E3
            E3 -- tempo score --> E4
            E4 -- danceability score --> E5
            E5 -- acousticness score --> SUM
        end

        D -- song dict --> G1
        SUM -- total_score --> ACC
        ACC[Append song_id · title · total_score\nto results list]
        ACC --> MORE{More songs\nin CSV?}
        MORE -- yes, next row --> D
    end

    MORE -- no more rows --> SORT

    %% ── Post-loop ────────────────────────────────────────────────────────────
    SORT[Sort results list\nby total_score descending]
    SORT -- sorted list --> SLICE[Slice top K entries]
    SLICE -- top-K results --> OUT

    OUT([Return ranked recommendations\nlist of song_id · title · score])
```

This flowchart traces the complete data pipeline of the song recommender: from loading `USER_PROFILE` and `songs.csv`, through the per-song weighted scoring loop, to sorting and returning the top-K ranked recommendations.
