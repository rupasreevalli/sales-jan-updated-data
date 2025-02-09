import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# Streamlit UI
st.title("Comprehensive Sales Analysis Dashboard")

# File upload option
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    try:
        # Load data
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        st.write("## Data Preview")
        st.dataframe(df.head())

        # Standardizing column names to match the updated dataset
        column_mapping = {
            "Company Name": "Company",
            "Created by": "Created By",
            "Demo date": "DemoDate",
            "Quote sent(Date)": "QuoteSentDate",
            "DateForNextAction": "Next Action Date",
            "OrderStatus": "Order Status",
            "ProductType": "Product Type"
        }
        df.rename(columns=column_mapping, inplace=True)

        # Convert date columns
        date_columns = ["Created on", "DemoDate", "QuoteSentDate", "Next Action Date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        # Convert numeric columns
        numeric_columns = ["Quantity", "Commitment", "Form Id"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Dashboard options
        analysis_option = st.selectbox(
            "Choose Analysis",
            [
                "Select",
                "Company Count by Order Stage",
                "Salesperson Performance Analysis",
                "Sales Funnel Analysis",
                "Average Duration Between Stages",
                "Key Sales Metrics"
            ]
        )

        # Analysis: Company Count by Order Stage
        if analysis_option == "Company Count by Order Stage":
            st.subheader("Company Count by Order Stage")
            if "Order Status" in df.columns and "Company" in df.columns:
                stage_summary = df.groupby("Order Status").agg(
                    Company_Count=("Company", "count")
                ).reset_index()
                st.dataframe(stage_summary)

                # Plot Bar Chart
                plt.figure(figsize=(12, 6))
                barplot = sns.barplot(
                    x="Order Status", y="Company_Count", data=stage_summary, color="skyblue"
                )
                plt.xticks(rotation=45)
                st.pyplot(plt)
            else:
                st.warning("Required columns missing from dataset!")

        # Analysis: Salesperson Performance
        elif analysis_option == "Salesperson Performance Analysis":
            st.subheader("Salesperson Performance Analysis")
            if all(col in df.columns for col in ["Created By", "Company", "Order Status"]):
                salesperson_summary = df.groupby("Created By").agg(
                    Total_Leads=("Company", "count"),
                    Wins=("Order Status", lambda x: (x.str.contains("Win", na=False)).sum())
                ).reset_index()
                salesperson_summary["Win Rate"] = salesperson_summary["Wins"] / salesperson_summary["Total_Leads"] * 100
                st.dataframe(salesperson_summary)

                fig, ax1 = plt.subplots(figsize=(12, 6))
                sns.barplot(x="Created By", y="Wins", data=salesperson_summary, ax=ax1, color="skyblue")
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("Required columns missing!")

        # Analysis: Sales Funnel
        elif analysis_option == "Sales Funnel Analysis":
            st.subheader("Sales Funnel Analysis")
            if "DemoDate" in df.columns and "QuoteSentDate" in df.columns and "Order Status" in df.columns:
                total_leads = len(df)
                demo_completed = df["DemoDate"].notnull().sum()
                quote_sent = df["QuoteSentDate"].notnull().sum()
                won = df["Order Status"].str.contains("Win", na=False).sum()

                stages = ["Total Leads", "Demo Completed", "Quote Sent", "Won"]
                values = [total_leads, demo_completed, quote_sent, won]

                fig = go.Figure(go.Funnel(y=stages, x=values, textinfo="value+percent initial"))
                st.plotly_chart(fig)
            else:
                st.warning("Required columns missing!")

        # Analysis: Average Duration Between Stages
        elif analysis_option == "Average Duration Between Stages":
            st.subheader("Average Duration Between Stages")
            df["Time to Demo"] = (df["DemoDate"] - df["Created on"]).dt.days
            df["Demo to Quote"] = (df["QuoteSentDate"] - df["DemoDate"]).dt.days
            df["Total Process Duration"] = (df["QuoteSentDate"] - df["Created on"]).dt.days

            avg_times = [df["Time to Demo"].mean(), df["Demo to Quote"].mean(), df["Total Process Duration"].mean()]
            stages = ["Time to Demo", "Demo to Quote", "Total Process Duration"]

            fig = go.Figure(data=[go.Bar(x=stages, y=avg_times, marker_color=["blue", "orange", "green"])])
            st.plotly_chart(fig)

        # Analysis: Key Sales Metrics
        elif analysis_option == "Key Sales Metrics":
            st.subheader("Key Sales Metrics")
            total_leads = df.shape[0]
            win_leads = df[df["Order Status"].str.contains("Win", na=False, case=False)]
            win_rate = (len(win_leads) / total_leads) * 100
            active_leads = df[~df["Order Status"].str.contains("Win|Drop", na=False, case=False)].shape[0]

            st.write(f"**Total Leads:** {total_leads}")
            st.write(f"**Win Rate:** {win_rate:.2f}%")
            st.write(f"**Active Leads:** {active_leads}")

    except Exception as e:
        st.error(f"Error loading or processing the file: {e}")
else:
    st.info("Please upload a CSV file to proceed.")
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Streamlit UI
st.title("📊 Sales Funnel Analysis")

# Upload CSV file in Streamlit
uploaded_file = st.file_uploader("Upload your sales data CSV", type=["csv"])

if uploaded_file is not None:
    # Load dataset
    data = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

    # Standardizing column names to match the updated dataset
    column_mapping = {
        "Created by": "Created By",
        "Demo date": "DemoDate",
        "Quote sent(Date)": "QuoteSentDate",
        "OrderStatus": "Order Status"
    }
    data.rename(columns=column_mapping, inplace=True)

    # Sidebar filter for user selection
    salespersons = data["Created By"].dropna().unique()
    selected_user = st.sidebar.selectbox("Select Salesperson", salespersons)

    # Filter dataset for the selected user
    df_user = data[data["Created By"] == selected_user]

    # Count leads at each stage
    total_leads = len(df_user)
    demo_completed = df_user[df_user["DemoStatus"].str.contains("Yes", na=False)].shape[0]
    quote_sent = df_user[df_user["QuoteSentDate"].notna()].shape[0]
    won = df_user[df_user["Order Status"].str.contains("Win", na=False)].shape[0]

    # Define funnel stages
    stages = ["Total Leads", "Demo Completed", "Quote Sent", "Won"]
    values = [total_leads, demo_completed, quote_sent, won]

    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker={"color": ["blue", "lightblue", "skyblue", "dodgerblue"]}
    ))

    # Display funnel chart in Streamlit
    st.plotly_chart(fig)

    # Show conversion percentages
    st.subheader(f"📊 Sales Funnel Breakdown for {selected_user}")
    st.write(f"**Total Leads:** {total_leads}")
    st.write(f"**Demo Completed:** {demo_completed} ({(demo_completed / total_leads * 100):.2f}%)" if total_leads > 0 else "0%")
    st.write(f"**Quote Sent:** {quote_sent} ({(quote_sent / demo_completed * 100):.2f}%)" if demo_completed > 0 else "0%")
    st.write(f"**Won Deals:** {won} ({(won / quote_sent * 100):.2f}%)" if quote_sent > 0 else "0%")

    # Show raw data for selected user
    if st.checkbox("Show Raw Data"):
        st.dataframe(df_user)

else:
    st.warning("⚠ Please upload a CSV file to proceed.")

