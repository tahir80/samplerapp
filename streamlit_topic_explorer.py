
import streamlit as st
import pandas as pd
import re
import random

# ====== SETTINGS ======
FILE_PATH = "https://drive.google.com/file/d/1SeAh_-UqzTw11xtkQbLVMbxyKNJhixte/view?usp=sharing"  # Update if needed

# ====== LOAD DATA ======
@st.cache_data
def load_data():
    df = pd.read_csv(FILE_PATH)
    df = df[df['topic'].notna() & (df['topic'] != -1)]
    df['combined_text'] = df['op_title'].fillna('') + ". " + df['op_text'].fillna('')
    return df

df = load_data()

# ====== HELPER FUNCTIONS ======
def extract_keywords(text):
    return set(re.findall(r'\b[a-zA-Z]{5,}\b', str(text).lower()))

def highlight_keywords(text, keywords):
    for word in sorted(keywords, key=len, reverse=True):
        text = re.sub(fr'\b({re.escape(word)})\b', r'<mark>\1</mark>', text, flags=re.IGNORECASE)
    return text

def get_random_examples(df):
    eligible_topics = df['topic'].value_counts()
    eligible_topics = eligible_topics[eligible_topics >= 5].index.tolist()
    chosen_topic = random.choice(eligible_topics)
    examples = df[df['topic'] == chosen_topic].sample(5).reset_index(drop=True)

    keyword_sets = [extract_keywords(text) for text in examples['combined_text']]
    common_keywords = set.intersection(*keyword_sets) if keyword_sets else set()
    examples['highlighted'] = examples['combined_text'].apply(lambda x: highlight_keywords(x, common_keywords))

    return chosen_topic, examples

# ====== INITIALIZATION ======
if 'chosen_topic' not in st.session_state:
    st.session_state['chosen_topic'], st.session_state['examples'] = get_random_examples(df)

# ====== PAGE CONFIG ======
st.set_page_config(layout="wide")
st.title("🧠 Topic Cluster Explorer")
st.write("Explore 5 randomly selected examples from the same topic cluster.")

# ====== REFRESH BUTTON ======
if st.button("🔁 Refresh Examples"):
    st.session_state['chosen_topic'], st.session_state['examples'] = get_random_examples(df)

# ====== DISPLAY EXAMPLES ======
chosen_topic = st.session_state['chosen_topic']
examples = st.session_state['examples']

st.markdown(f"### 🔍 Topic `{chosen_topic}` — 5 Examples Compared")
cols = st.columns(5)

for i in range(5):
    with cols[i]:
        st.markdown(f"**Example {i+1}**", unsafe_allow_html=True)
        st.markdown(f"*{examples.loc[i, 'op_title']}*", unsafe_allow_html=True)
        st.markdown(examples.loc[i, 'highlighted'], unsafe_allow_html=True)
