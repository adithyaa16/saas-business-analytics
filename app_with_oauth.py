import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import smtplib
from email.mime.text import MIMEText
from sklearn.linear_model import LinearRegression
from streamlit_oauth import OAuth2Component
import requests
from datetime import datetime

st.set_page_config(
    page_title="SaaS Business Analytics",
    page_icon="🚀",
    layout="wide"
)

# SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# GOOGLE OAUTH CONFIG
try:
    GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
except:
    GOOGLE_CLIENT_ID = ""
    GOOGLE_CLIENT_SECRET = ""

# USERS FILE
users_file = "users.csv"

if not os.path.exists(users_file):
    users_df = pd.DataFrame(
        columns=["username", "password"]
    )
    users_df.to_csv(users_file, index=False)

# LOGIN PAGE
if not st.session_state.logged_in:

    st.title("🚀 SaaS Business Analytics Platform")

    st.markdown("""
    ### Business Intelligence Dashboard

    Analyze SaaS platform performance,
    revenue, customers, products,
    churn and forecasting.
    """)

    menu = st.selectbox(
        "Select",
        ["Login", "Signup", "Google OAuth"]
    )

    # LOGIN
    if menu == "Login":

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            users = pd.read_csv(
                users_file,
                dtype=str
            )

            users["username"] = (
                users["username"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            users["password"] = (
                users["password"]
                .astype(str)
                .str.strip()
            )

            username_input = (
                username
                .strip()
                .lower()
            )

            password_input = (
                str(password)
                .strip()
            )

            user = users[
                (
                    users["username"]
                    == username_input
                )
                &
                (
                    users["password"]
                    == password_input
                )
            ]

            if not user.empty:

                st.session_state.logged_in = True

                st.session_state.username = (
                    username_input
                )

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )

    # SIGNUP
    elif menu == "Signup":

        new_user = st.text_input(
            "Create Username"
        )

        new_pass = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Signup"):

            users = pd.read_csv(
                users_file,
                dtype=str
            )

            users["username"] = (
                users["username"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            new_user = (
                new_user
                .strip()
                .lower()
            )

            if (
                new_user
                in users["username"].values
            ):

                st.warning(
                    "Username Already Exists"
                )

            else:

                new_data = pd.DataFrame(
                    {
                        "username": [new_user],
                        "password": [new_pass]
                    }
                )

                users = pd.concat(
                    [users, new_data],
                    ignore_index=True
                )

                users.to_csv(
                    users_file,
                    index=False
                )

                st.success(
                    "Account Created Successfully"
                )

    # GOOGLE OAUTH
    elif menu == "Google OAuth":

        st.subheader("🔐 Sign in with Google")

        CLIENT_ID = GOOGLE_CLIENT_ID
        CLIENT_SECRET = GOOGLE_CLIENT_SECRET
        AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
        TOKEN_URL = "https://oauth2.googleapis.com/token"
        REFRESH_TOKEN_URL = TOKEN_URL

        # ✅ REVOKE_TOKEN_URL removed to fix MissingRevokeTokenAuthMethodError
        oauth2 = OAuth2Component(
            CLIENT_ID,
            CLIENT_SECRET,
            AUTHORIZE_URL,
            TOKEN_URL,
            REFRESH_TOKEN_URL,
        )

        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="http://localhost:8501/",
            scope="openid email profile",
            use_container_width=True,
            pkce="S256",
            key="google_login",
        )

        if result:
            st.session_state.logged_in = True
            st.session_state.username = "Google User"
            st.success("✅ Google Login Successful")
            st.rerun()

    st.stop()

# LOGOUT
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# LOAD DATASET
try:
    df = pd.read_csv("SaaS-Sales.csv")
except:
    st.error("SaaS-Sales.csv not found in project folder")
    st.stop()

# DATE COLUMN
if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

# SIDEBAR
st.sidebar.title("📊 SaaS Analytics")
st.sidebar.success(f"Welcome {st.session_state.username}")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Sales Analytics",
        "Customer Analytics",
        "Product Analytics",
        "Region Analytics",
        "Forecast Prediction",
        "AI Insights",
        "Dataset Upload",
        "Dataset History",
        "Churn Prediction",
        "Revenue Prediction",
        "Reports",
        "SMTP Email"
    ]
)

# DASHBOARD
if page == "Dashboard":
    st.title("🚀 SaaS Business Analytics Dashboard")

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_customers = df["Customer"].nunique()
    total_products = df["Product"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", f"${total_sales:,.0f}")
    c2.metric("Profit", f"${total_profit:,.0f}")
    c3.metric("Customers", total_customers)
    c4.metric("Products", total_products)

    monthly_sales = (
        df.groupby(
            df["Order Date"]
            .dt.to_period("M")
        )["Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales[
        "Order Date"
    ] = monthly_sales[
        "Order Date"
    ].astype(str)

    fig = px.line(
        monthly_sales,
        x="Order Date",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# SALES ANALYTICS
elif page == "Sales Analytics":
    st.title("📈 Sales Analytics")

    fig1 = px.histogram(
        df,
        x="Sales",
        title="Sales Distribution"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    industry_sales = (
        df.groupby("Industry")
        ["Sales"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        industry_sales,
        x="Industry",
        y="Sales",
        color="Industry",
        title="Industry Wise Sales"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    fig3 = px.pie(
        industry_sales,
        names="Industry",
        values="Sales",
        title="Industry Share"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# CUSTOMER ANALYTICS
elif page == "Customer Analytics":
    st.title("👥 Customer Analytics")

    top_customers = (
        df.groupby("Customer")
        ["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    st.subheader("Top Customers")

    fig = px.bar(
        top_customers,
        x="Customer",
        y="Sales",
        color="Sales"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        top_customers
    )

# PRODUCT ANALYTICS
elif page == "Product Analytics":
    st.title("📦 Product Analytics")

    top_products = (
        df.groupby("Product")
        ["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_products,
        x="Product",
        y="Sales",
        color="Sales"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        top_products
    )

# REGION ANALYTICS
elif page == "Region Analytics":
    st.title("🌍 Region Analytics")

    region_sales = (
        df.groupby("Region")
        ["Sales"]
        .sum()
        .reset_index()
    )

    fig1 = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        color="Region"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    fig2 = px.pie(
        region_sales,
        names="Region",
        values="Sales"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# FORECAST PREDICTION
elif page == "Forecast Prediction":
    st.title("🔮 Sales Forecast")

    forecast_df = (
        df.groupby("Order Date")
        ["Sales"]
        .sum()
        .reset_index()
    )

    forecast_df = (
        forecast_df
        .sort_values(
            "Order Date"
        )
    )

    forecast_df["Day"] = range(
        len(forecast_df)
    )

    X = forecast_df[
        ["Day"]
    ]

    y = forecast_df[
        "Sales"
    ]

    model = LinearRegression()

    model.fit(
        X,
        y
    )

    future_days = st.slider(
        "Forecast Days",
        1,
        180,
        30
    )

    prediction = model.predict(
        [[
            len(forecast_df)
            +
            future_days
        ]]
    )[0]

    st.success(
        f"Predicted Sales After {future_days} Days : ${prediction:,.2f}"
    )

    fig = px.line(
        forecast_df,
        x="Order Date",
        y="Sales",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# REPORTS
elif page == "Reports":
    st.title("📑 Business Report")

    total_sales = (
        df["Sales"]
        .sum()
    )

    total_profit = (
        df["Profit"]
        .sum()
    )

    best_customer = (
        df.groupby("Customer")
        ["Sales"]
        .sum()
        .idxmax()
    )

    best_product = (
        df.groupby("Product")
        ["Sales"]
        .sum()
        .idxmax()
    )

    st.info(
        f"""
Total Revenue : ${total_sales:,.2f}

Total Profit : ${total_profit:,.2f}

Best Customer :
{best_customer}

Best Product :
{best_product}
"""
    )

elif page == "AI Insights":
    st.title("🤖 AI Business Insights")

    revenue = df["Sales"].sum()
    profit = df["Profit"].sum()

    if profit > 0:
        st.success(
            "Business is profitable."
        )
    else:
        st.error(
            "Business is running at loss."
        )

    top_region = (
        df.groupby("Region")["Sales"]
        .sum()
        .idxmax()
    )

    top_product = (
        df.groupby("Product")["Sales"]
        .sum()
        .idxmax()
    )

    st.info(
        f"""
Top Region : {top_region}

Top Product : {top_product}

Revenue : ${revenue:,.2f}

Profit : ${profit:,.2f}
"""
    )

elif page == "Dataset Upload":
    st.title("📂 Upload Dataset")

    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded:

        upload_df = pd.read_csv(uploaded)

        st.success(
            "Dataset Uploaded Successfully"
        )

        st.subheader(
            "Dataset Preview"
        )

        st.dataframe(
            upload_df.head()
        )

        st.subheader(
            "Dataset Overview"
        )

        c1,c2,c3 = st.columns(3)

        c1.metric(
            "Rows",
            upload_df.shape[0]
        )

        c2.metric(
            "Columns",
            upload_df.shape[1]
        )

        numeric_cols = upload_df.select_dtypes(
            include=np.number
        ).columns

        c3.metric(
            "Numeric Columns",
            len(numeric_cols)
        )

        st.subheader(
            "Column Information"
        )

        info_df = pd.DataFrame({
            "Column":
            upload_df.columns,

            "Datatype":
            upload_df.dtypes.astype(str)
        })

        st.dataframe(
            info_df
        )

        st.subheader(
            "Missing Values Analysis"
        )

        missing = (
            upload_df
            .isnull()
            .sum()
            .reset_index()
        )

        missing.columns = [
            "Column",
            "Missing Values"
        ]

        st.dataframe(
            missing
        )

        if len(numeric_cols) > 0:

            st.subheader(
                "Distribution Analysis"
            )

            selected_col = st.selectbox(
                "Select Numeric Column",
                numeric_cols
            )

            fig = px.histogram(
                upload_df,
                x=selected_col,
                title=f"{selected_col} Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        if len(numeric_cols) > 1:

            st.subheader(
                "Correlation Analysis"
            )

            corr = upload_df[
                numeric_cols
            ].corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                title="Correlation Matrix"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader(
            "🤖 AI Dataset Insights"
        )

        rows = upload_df.shape[0]
        cols = upload_df.shape[1]

        st.info(
            f"""
Dataset contains {rows} rows and {cols} columns.

✔ Suitable for Analytics

✔ Suitable for Reporting

✔ Suitable for Prediction

✔ Suitable for Machine Learning
"""
        )

        if len(numeric_cols) > 0:

            st.subheader(
                "Future Prediction"
            )

            target_column = (
                numeric_cols[-1]
            )

            X = np.arange(
                len(upload_df)
            ).reshape(-1,1)

            y = upload_df[
                target_column
            ]

            model = LinearRegression()

            model.fit(
                X,
                y
            )

            prediction = model.predict(
                [[
                    len(upload_df)+30
                ]]
            )[0]

            st.success(
                f"""
Predicted Future Value of
{target_column}

= {prediction:.2f}
"""
            )

            final_result = (
                f"Prediction for {target_column} : {prediction:.2f}"
            )

            history_file = (
                f"{st.session_state.username}_history.csv"
            )

            new_history = pd.DataFrame({
                "Dataset":[uploaded.name],
                "Rows":[rows],
                "Columns":[cols],
                "Prediction":[final_result]
            })

            if os.path.exists(
                history_file
            ):

                old = pd.read_csv(
                    history_file
                )

                new_history = pd.concat(
                    [
                        old,
                        new_history
                    ],
                    ignore_index=True
                )

            new_history.to_csv(
                history_file,
                index=False
            )

            st.success(
                "Analysis Saved To History"
            )

        st.subheader(
            "Download Report"
        )

        report = pd.DataFrame({
            "Metric":[
                "Rows",
                "Columns"
            ],
            "Value":[
                rows,
                cols
            ]
        })

        csv = report.to_csv(
            index=False
        )

        st.download_button(
            "Download Analysis Report",
            csv,
            "analysis_report.csv",
            "text/csv"
        )

elif page == "Dataset History":

    st.title("📜 Dataset Analysis History")

    history_file = (
        f"{st.session_state.username}_history.csv"
    )

    if os.path.exists(history_file):

        history = pd.read_csv(
            history_file
        )

        st.success(
            f"Total Reports : {len(history)}"
        )

        st.dataframe(
            history
        )

        selected = st.selectbox(
            "Select Previous Analysis",
            history["Dataset"]
        )

        selected_row = history[
            history["Dataset"]
            ==
            selected
        ]

        st.subheader(
            "Analysis Result"
        )

        st.write(
            selected_row
        )

    else:

        st.warning(
            "No History Available"
        )

elif page == "Churn Prediction":

    st.title("📉 Churn Prediction")

    active_users = st.number_input(
        "Active Users",
        0,
        100000,
        5000
    )

    support_tickets = st.number_input(
        "Support Tickets",
        0,
        5000,
        200
    )

    if st.button("Predict Churn"):

        score = (
            support_tickets /
            (active_users + 1)
        ) * 100

        if score > 5:
            st.error(
                "High Churn Risk"
            )
        else:
            st.success(
                "Low Churn Risk"
            )

elif page == "Revenue Prediction":

    st.title("💰 Revenue Prediction")

    months = st.slider(
        "Future Months",
        1,
        24,
        6
    )

    avg_monthly = (
        df.groupby(
            df["Order Date"].dt.month
        )["Sales"]
        .sum()
        .mean()
    )

    predicted = (
        avg_monthly * months
    )

    st.success(
        f"Predicted Revenue : ${predicted:,.2f}"
    )

elif page == "SMTP Email":

    st.title("📧 Email Report")

    receiver = st.text_input(
        "Receiver Email"
    )

    if st.button("Send Report"):

        try:

            sender_email = "adithyadinesh1316@gmail.com"

            app_password = st.secrets.get("app_password", "")

            subject = "SaaS Business Analytics Report"

            message = """
Business Analytics Report

Dashboard Generated Successfully.

Regards,
SaaS Analytics Platform
"""

            msg = MIMEText(message)

            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = receiver

            server = smtplib.SMTP(
                "smtp.gmail.com",
                587
            )

            server.starttls()

            server.login(
                sender_email,
                app_password
            )

            server.sendmail(
                sender_email,
                receiver,
                msg.as_string()
            )

            server.quit()

            st.success(
                "Email Sent Successfully"
            )

        except Exception as e:

            st.error(
                str(e)
            )
