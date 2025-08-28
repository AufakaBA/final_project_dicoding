import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

# CSS
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #F5F2E7; /* krem muda */
        }

        /* Sidebar dengan coklat muda */
        section[data-testid="stSidebar"] {
            background-color: #EDE0D4; /* coklat muda */
        }

        /* Card style */
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            background-color: #FFF8F0; /* beige */
            box-shadow: 0px 4px 8px rgba(140, 98, 57, 0.2);
            text-align: center;
        }

        .metric-title {
            font-size: 14px;
            color: #6B4226; /* coklat tua */
        }

        .metric-value {
            font-size: 22px;
            font-weight: bold;
            color: #8B5E3C; /* coklat medium */
        }

        h1, h2, h3 {
            color: #6B4226; /* judul coklat tua */
        }
    </style>
""", unsafe_allow_html=True)

# function masukin data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('all_data.csv')
        date_columns = ['order_date','order_approved_at','order_delivered_carrier_date',
                        'order_delivered_customer_date','order_estimated_delivery_date',
                        'shipping_limit_date']
        for col in date_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col], errors='coerce')
        return data
    except FileNotFoundError:
        st.error("Error: all_data.csv not found.")
        return pd.DataFrame()

df = load_data()

# --- Layout dashboardnya ---
st.title("🌱 Sales Dashboard Overview")

if not df.empty:
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()

    with st.sidebar:
        st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=150)
        start_date, end_date = st.date_input(
            label='📅 Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

    main_df = df[(df["order_date"] >= str(start_date)) & (df["order_date"] <= str(end_date))]

    # Overview pake card
    st.subheader("Data Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Number of Orders</div>
            <div class="metric-value">{df['order_id'].nunique():,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Number of Customers</div>
            <div class="metric-value">{df['customer_id'].nunique():,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">${df['total_price'].sum():,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- earth tone pa;ette
    sns.set_palette(["#A47551", "#C2B280", "#8B5E3C", "#B08968", "#6B4226"])

    # Top Categories
    st.subheader("🏆 Top Selling Product Categories")
    if 'product_category_name_english' in df.columns:
        top_categories = df.groupby('product_category_name_english')['order_id'].nunique().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=top_categories.values, y=top_categories.index, ax=ax)
        ax.set_xlabel("Number of Orders")
        ax.set_ylabel("Category")
        st.pyplot(fig)
        plt.close(fig)

    # Top States
    st.subheader("📍 Top Selling Regions")
    if 'customer_state' in df.columns:
        top_states = df.groupby('customer_state')['order_id'].nunique().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_states.values, y=top_states.index, ax=ax)
        ax.set_xlabel("Orders")
        ax.set_ylabel("State")
        st.pyplot(fig)
        plt.close(fig)

    # Payment Types
    st.subheader("💳 Payment Methods Distribution")
    if 'payment_type' in df.columns:
        payment_type_counts = df['payment_type'].value_counts()
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(payment_type_counts, labels=payment_type_counts.index, autopct='%1.1f%%',
               startangle=90, colors=["#A47551", "#C2B280", "#8B5E3C", "#6B4226"])
        ax.axis('equal')
        st.pyplot(fig)
        plt.close(fig)

    # RFM Analysis
    st.subheader("🤖  Customer Segmentation (RFM Analysis)")
    
    if 'order_date' in df.columns and 'total_price' in df.columns and 'customer_id' in df.columns:
        # Recalculate RFM if not loaded from a separate file
        rfm_df = df.groupby(by="customer_id", as_index=False).agg({
            "order_date": "max",  # get the last order date
            "order_id": "nunique",  # count unique orders
            "total_price": "sum"  # sum up the total price
        })
        rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

        # Calculate Recency
        rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
        recent_date = df["order_date"].dt.date.max() # Use the latest date from the entire dataset
        rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

        rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

        st.write("RFM Metrics (first 5 customers):")
        st.dataframe(rfm_df.head())

        # Display average RFM metrics

        # 🔹 RFM Metrics (pakai card juga)
        average_recency = rfm_df['recency'].mean()
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        average_monetary = rfm_df.monetary.mean()

        st.subheader("📊 RFM Metrics Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
            <div class="metric-title">Average Recency</div>
            <div class="metric-value">{average_recency:.2f} days</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")

        with col2:
            st.markdown(f"""
            <div class="metric-card">
            <div class="metric-title">Average Frequency</div>
            <div class="metric-value">{avg_frequency:.2f} trx/customer</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
        with col3:
            st.markdown(f"""
            <div class="metric-card">
            <div class="metric-title">Average Monetary Value</div>
            <div class="metric-value">{format_currency(average_monetary, 'USD', locale='en_US')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

        # Visualize RFM
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(15, 5)) # Adjust figure size for Streamlit

        colors = ["#DEB887"] # Use a single color for simplicity or define a list

        # Recency Plot
        sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0]) # Sort ascending for recency (lower is better)
        ax[0].set_ylabel("Recency (days)")
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Customers by Recency")
        ax[0].tick_params(axis ='x', labelsize=8, rotation=45) # Rotate labels for better readability

        # Frequency Plot
        sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
        ax[1].set_ylabel("Frequency")
        ax[1].set_xlabel(None)
        ax[1].set_title("Best Customers by Frequency")
        ax[1].tick_params(axis='x', labelsize=8, rotation=45)

        # Monetary Plot
        sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
        ax[2].set_ylabel("Monetary Value")
        ax[2].set_xlabel(None)
        ax[2].set_title("Best Customers by Monetary")
        ax[2].tick_params(axis='x', labelsize=8, rotation=45)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig) # Close the figure

        st.markdown("---")

    elif df.empty:
        st.warning("Punten, data ga masuk")
    else:
        st.info("Nah data masuk sih, tapi mana kolom yang mau dipakenya")

else:
    st.warning("data ga masuk we")