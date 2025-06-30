import pandas as pd
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import streamlit as st



def winClassifier(df):
    predictor_cols = ['speed_Q1', 'speed_Q2', 'speed_Q3', 'speed_Q4',
                    'pos_Q1', 'pos_Q2', 'pos_Q3', 'pos_Q4']
    df = df.dropna(subset=predictor_cols)

    X = df[predictor_cols]
    y = df['win']


    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)

    model.fit(X_train, y_train)

    coef_df = pd.DataFrame({
        'Feature': predictor_cols,
        'Coefficient': model.coef_[0]
    }).sort_values(by='Coefficient', ascending=False)

    return coef_df

def strategyGuide(df, coef_df):

    # Strategy logic
    def strategy_tip(row):
        f, coef = row['Feature'], row['Coefficient']
        quarter = f[-2:]  # Q1, Q2, Q3, Q4
        impact = abs(coef)
        
        # Position-based features
        if 'pos' in f:
            if coef < -0.75:
                return (f"🏁 Crucial Positioning Phase 🏁 <br>"
                        f"Your odds of winning drop sharply with every position lost. "
                        f"Make sure you're contesting the lead entering this segment.")
            elif coef < -0.25:
                return (f"⚠️ Positional Pressure ⚠️ <br>"
                        f"Falling more than a few lengths back reduces your win potential. "
                        f"Stay engaged with the leaders and prepare to respond.")
            elif coef > 0.25:
                return (f"🧠 Tactical Hold-Back Opportunity 🧠 <br>"
                        f"jockeys positioned just off the pace here tend to set up successful closing runs. "
                        f"Avoid over-committing too early.")
            else:
                return (f"ℹ️ Flexible Positioning ℹ️ <br>"
                        f"No strong positional impact observed. Focus on conserving energy and tracking the pace.")
        
        # Speed-based features
        elif 'speed' in f:
            if coef > 0.1:
                return (f"🚀 Momentum Advantage 🚀 <br> "
                        f"Faster speeds here have a meaningful impact. If you're well-positioned, consider driving forward to gain tactical edge.")
            elif coef > 0.02:
                return (f"⏩ Marginal Speed Gain ⏩ <br> "
                        f"Increasing pace helps, but only slightly. Push only if it won’t cost you late.")
            elif coef < -0.1:
                return (f"⛔ Risk of Overexertion ⛔ <br> "
                        f"Higher speed in this segment typically backfires. Focus on rhythm and efficiency.")
            elif coef < -0.02:
                return (f"⚠️ Subtle Fatigue Zone ⚠️ <br> "
                        f"Be cautious — small increases in speed don’t pay off. Prioritize form and control.")
            else:
                return (f"ℹ️ Neutral Speed Effect ℹ️ <br>"
                        f"No significant impact from changes in speed here. Let race dynamics guide your pacing.")
        
        # Fallback
        else:
            return "No strategy available for this feature."

    # Apply strategy interpretation
    coef_df['Odds Multiplier'] = np.exp(coef_df['Coefficient'])
    coef_df['Strategy Tip'] = coef_df.apply(strategy_tip, axis=1)

    # Reorder and show as strategy guide
    strategy_guide = coef_df.sort_values(by='Feature')[['Feature', 'Coefficient', 'Odds Multiplier', 'Strategy Tip']]

    return strategy_guide


def rgb_str(rgb):
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def strategy_block(segment, pos_text, speed_text,segment_colors):
    color_rgb = segment_colors[segment]
    header_color = rgb_str(color_rgb)

    st.markdown(f"""
        <div style="background-color: #343332;
                    padding: 0.8rem 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                    border: 1px solid #ddd;
                    color: #ffffff;">
            <h3 style="color:{header_color}; margin: 0; padding: 0; line-height: 1.3;">Strategy {segment}</h3>
            <div style="display: flex; justify-content: space-between; margin-top: 0.3rem;">
                <div style="flex: 1;">
                    <h4 style="color:{header_color};margin: 0; padding: 0; line-height: 1.3;">Positioning</h4>
                    <p style="margin: 0; padding: 0;">{pos_text}</p>
                </div>
                <div style="flex: 1;">
                    <h4 style="color:{header_color};margin: 0; padding: 0; line-height: 1.1;">Speed</h4>
                    <p style="margin: 0; padding: 0;">{speed_text}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)