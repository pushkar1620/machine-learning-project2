import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(page_title="📊 WhatsApp Chat Analyzer", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📱 WhatsApp Chat Analyzer</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/733/733585.png", width=100)
    st.title("Upload Chat File")
    uploaded_file = st.file_uploader("Choose your WhatsApp .txt file", type=["txt"])
    st.markdown("---")

    if uploaded_file:
        st.success("File uploaded successfully!", icon="✅")

# Process file
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocessor(data)

    # Show raw data if user wants
    with st.expander("📄 Show Raw Chat Data"):
        st.dataframe(df, use_container_width=True)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Analyze messages by", user_list)
    st.sidebar.markdown("---")

    if st.sidebar.button("📈 Show Analysis"):

        # 1. Top Stats
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.markdown("## 🔢 Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        stats = [("Total Messages", num_messages),
                 ("Total Words", words),
                 ("Media Shared", num_media_messages),
                 ("Links Shared", num_links)]

        for col, (label, value) in zip([col1, col2, col3, col4], stats):
            with col:
                st.metric(label, value)

        st.markdown("---")

        # 2. Monthly Timeline
        st.markdown("## 📆 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        ax.set_title("Monthly Messages Trend")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        st.markdown("---")

        # 3. Daily Timeline
        st.markdown("## 📅 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        ax.set_title("Daily Message Count")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        st.markdown("---")

        # 4. Activity Maps
        st.markdown("## 🗓️ Weekly & Monthly Activity")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Active Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.subheader("Most Active Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.markdown("---")

        # 5. Heatmap
        st.markdown("## 🌡️ Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax, cmap="YlGnBu")
        ax.set_title("Day & Time Activity")
        st.pyplot(fig)
        st.markdown("---")

        # 6. Busiest Users
        if selected_user == 'Overall':
            st.markdown("## 👥 Most Active Users")
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                ax.set_title("Most Active Users")
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        st.markdown("---")

        # 7. WordCloud
        st.markdown("## ☁️ WordCloud of Most Used Words")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
        st.markdown("---")

        # 8. Most Common Words
        st.markdown("## 🔠 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='skyblue')
        ax.invert_yaxis()
        ax.set_xlabel("Count")
        st.pyplot(fig)
        st.markdown("---")

        # 9. Emoji Analysis
        st.markdown("## 😄 Emoji Usage")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f", startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
