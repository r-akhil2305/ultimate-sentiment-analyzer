import streamlit as st
from textblob import TextBlob
import nltk
import pandas as pd
import plotly.graph_objects as go
import time

# Download NLTK resources
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

st.title("📝 Ultimate Sentiment Analyzer")
st.write("Analyze multiple sentences, see your mood gauge animate, get suggestions, play games, and listen to songs!")

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Songs with names and URLs
positive_songs_dict = {
    "Happy Tune": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Joyful Beat": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Upbeat Vibes": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}

negative_songs_dict = {
    "Sad Melody": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "Blue Note": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    "Rainy Mood": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3"
}

neutral_songs_dict = {
    "Chill Beat": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
    "Calm Flow": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
    "Easy Listening": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3"
}

# User input
user_input = st.text_area("Enter your sentences (one per line):")

if st.button("Analyze"):
    if user_input.strip() == "":
        st.warning("Please enter at least one sentence!")
    else:
        results = []
        lines = user_input.strip().split("\n")
        for sentence in lines:
            blob = TextBlob(sentence)
            polarity = blob.sentiment.polarity
            if polarity > 0:
                sentiment = "POSITIVE 😃"
                color = "green"
            elif polarity < 0:
                sentiment = "NEGATIVE 😢"
                color = "red"
            else:
                sentiment = "NEUTRAL 😐"
                color = "gray"
            
            results.append({"Sentence": sentence, "Sentiment": sentiment, "Polarity": polarity, "Color": color})
        
        st.session_state.history.extend(results)

        # Animated sentence display
        st.subheader("Analysis Results")
        for i, res in enumerate(results, start=1):
            html = (
                f"<p style='color:{res['Color']}; font-size:16px;'>"
                f"{i}. {res['Sentence']} → <b>{res['Sentiment']}</b> (Polarity: {res['Polarity']:.2f})</p>"
            )
            st.markdown(html, unsafe_allow_html=True)
            time.sleep(0.2)

        # History panel
        st.subheader("History Panel")
        history_df = pd.DataFrame(st.session_state.history)
        history_df.index = history_df.index + 1
        st.dataframe(history_df[["Sentence", "Sentiment", "Polarity"]])

        # Overall polarity gauge
        st.subheader("🌡️ Overall Mood Gauge")
        overall_polarity = history_df["Polarity"].mean()
        gauge_value_target = (overall_polarity + 1) * 50

        gauge_placeholder = st.empty()
        for val in range(0, int(gauge_value_target)+1, 2):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 33], 'color': "red"},
                        {'range': [33, 66], 'color': "gray"},
                        {'range': [66, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': val
                    }
                },
                title={'text': "Overall Mood Gauge"}
            ))
            gauge_placeholder.plotly_chart(fig)
            time.sleep(0.01)

        # Determine mood, suggestion, game, songs
        if overall_polarity > 0.1:
            overall_sentiment = "POSITIVE 😃"
            suggestion = "Keep up the good vibes! Maybe share your happiness with a friend or work on something creative."
            game = "[Play Chrome Dino 🦖](https://chromedino.com/)"
            songs_dict = positive_songs_dict
        elif overall_polarity < -0.1:
            overall_sentiment = "NEGATIVE 😢"
            suggestion = "Take a short break, breathe, or listen to your favorite music to lift your mood."
            game = "[Play Relaxing Bubbles 🌊](https://neal.fun/ambient-chaos/)"
            songs_dict = negative_songs_dict
        else:
            overall_sentiment = "NEUTRAL 😐"
            suggestion = "You're balanced right now. Maybe challenge your brain with a puzzle!"
            game = "[Play Sudoku 🧩](https://sudoku.com/)"
            songs_dict = neutral_songs_dict

        st.write(f"**Overall Sentiment:** {overall_sentiment} (Avg Polarity: {overall_polarity:.2f})")

        # Suggestion box
        st.info(f"💡 Suggestion: {suggestion}")

        # Game
        st.subheader("🎮 Mood Games")
        st.markdown(f"{game}", unsafe_allow_html=True)

        # Songs with names and audio player
        st.subheader("🎵 Mood Songs Playlist")
        for name, track in songs_dict.items():
            st.markdown(f"**{name}**")
            st.audio(track, format="audio/mp3")

        # Download CSV
        csv = history_df[["Sentence", "Sentiment", "Polarity"]].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download History as CSV",
            data=csv,
            file_name="sentiment_history.csv",
            mime="text/csv"
        )
