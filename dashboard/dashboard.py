import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency
sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("merge_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('geolocation_dataset.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Indradi Rahmatullah")

    # Logo Image
    st.image("data-science.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard")

# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#FF6347"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spend Money
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#32CD32"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#8A2BE2", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]  # Blue Violet for first chart

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

colors = ["#FF4500", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]  # Orange Red for second chart
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1,col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(x=review_score.index, 
            y=review_score.values, 
            order=review_score.index,
            palette=["#8A2BE2" if score == common_score else "#D3D3D3" for score in review_score.index]  # Using Blue Violet
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2, tab3 = st.tabs(["State", "Order Status", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette=["#FF6347" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                    )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Most Common Order Status: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(x=order_status.index,
                y=order_status.values,
                order=order_status.index,
                palette=["#32CD32" if score == common_status else "#D3D3D3" for score in order_status.index]
                )
    
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab3:
    map_plot.plot()

    with st.expander("Description"):
        st.write('According to the graph, there are more customers in the southeast and south. Another piece of information is that there are more customers in the capital cities (São Paulo, Rio de Janeiro, Porto Alegre, etc.).')

# New Visualizations

# Distribution of Orders Delivered On Time vs Late
st.subheader("Distribution of Orders Delivered On Time vs Late")
all_df['delivered_on_time'] = (all_df['order_delivered_customer_date'] <= all_df['order_estimated_delivery_date'])

delivery_status_counts = all_df['delivered_on_time'].value_counts()

fig, ax = plt.subplots(figsize=(6, 4))
delivery_status_counts.plot(kind='bar', color=['green', 'red'], ax=ax)
ax.set_title('Distribution of Orders Delivered On Time vs Late')
ax.set_xlabel('Delivery Status')
ax.set_ylabel('Number of Orders')
ax.set_xticklabels(['On Time', 'Late'], rotation=0)
st.pyplot(fig)


# Distribution of Payment Methods
st.subheader("Distribution of Payment Methods")
payment_type_counts = all_df['payment_type'].value_counts()

# Exclude the 'not_defined' category
payment_type_counts = payment_type_counts[payment_type_counts.index != 'not_defined']

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(payment_type_counts, autopct='%1.1f%%', colors=sns.color_palette("Set3", len(payment_type_counts)), startangle=180)
ax.set_title('Distribution of Payment Methods')
ax.set_ylabel('')  # Hide the y-label
ax.legend(wedges, payment_type_counts.index, title="Payment Methods", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.setp(autotexts, size=10, weight="bold")
st.pyplot(fig)

st.write(payment_type_counts)

# Top 10 Cities with the Most Sellers
st.subheader("Top 10 Cities with the Most Sellers")
top_seller_cities = all_df.groupby('seller_city')['seller_id'].nunique().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 6))
top_seller_cities.plot(kind='bar', color='skyblue', ax=ax)
ax.set_title('Top 10 Cities with the Most Sellers')
ax.set_xlabel('City')
ax.set_ylabel('Number of Sellers')
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Relationship between Payment Value and Review Score
st.subheader("Relationship between Payment Value and Review Score")
merged_payments_reviews = pd.merge(
    left=all_df[['order_id', 'payment_value']],
    right=all_df[['order_id', 'review_score']],
    how='left',
    on='order_id'
)

correlation = merged_payments_reviews[['payment_value', 'review_score']].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x='payment_value', y='review_score', data=merged_payments_reviews, color='purple', alpha=0.5, ax=ax)
ax.set_title('Relationship between Payment Value and Review Score')
ax.set_xlabel('Payment Value')
ax.set_ylabel('Review Score')
st.pyplot(fig)

st.caption('Copyright (C) Indradi Rahmatullah 2024')