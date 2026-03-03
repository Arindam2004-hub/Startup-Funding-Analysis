import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout='wide', page_title='StartUp Analysis')

df = pd.read_csv("startup_cleaned.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year


def load_overall_analysis():
    st.title('Overall Analysis')

    total = round(df['amount'].sum())
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    num_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total', str(total) + ' Cr')
    with col2:
        st.metric('Max', str(max_funding) + ' Cr')
    with col3:
        st.metric('Avg', str(round(avg_funding)) + ' Cr')
    with col4:
        st.metric('Funded Startups', num_startups)

    st.header('Month-over-Month Graph')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])
    if selected_option == 'Total':
        temp_df = df.groupby('month')['amount'].sum().reset_index()
    else:
        temp_df = df.groupby('month')['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str')  
    # + temp_df['month'].astype('str')

    fig3, ax3 = plt.subplots()
    ax3.plot(temp_df['x_axis'], temp_df['amount'])
    st.pyplot(fig3)



def load_startup_details(startup):
    st.title(startup)

    startup_df = df[df['startup'] == startup]

    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Funding', str(round(startup_df['amount'].sum())) + ' Cr')
    with col2:
        st.metric('Total Rounds', str(startup_df.shape[0]))
    with col3:
        st.metric('Sector', startup_df['vertical'].mode()[0] if not startup_df['vertical'].isna().all() else 'N/A')

    # Funding rounds table
    st.subheader('Funding Rounds')
    st.dataframe(startup_df[['date', 'investors', 'vertical', 'city', 'round', 'amount']].reset_index(drop=True))

    col1, col2 = st.columns(2)

    with col1:
        # Funding by round type
        round_series = startup_df.groupby('round')['amount'].sum().sort_values(ascending=False)
        if not round_series.empty:
            st.subheader('Funding by Round')
            fig, ax = plt.subplots()
            ax.bar(round_series.index, round_series.values, color='steelblue')
            ax.set_xlabel('Round')
            ax.set_ylabel('Amount (Cr)')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)

    with col2:
        # YoY funding
        year_series = startup_df.groupby('year')['amount'].sum()
        if not year_series.empty:
            st.subheader('YoY Funding')
            fig2, ax2 = plt.subplots()
            ax2.plot(year_series.index, year_series.values, marker='o', color='orange')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Amount (Cr)')
            st.pyplot(fig2)


def load_investor_details(investor):
    st.title(investor)

    investor_df = df[df['investors'].str.contains(investor, na=False)]

    last5_df = investor_df.head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)

    with col1:
        big_series = investor_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investments')
        if not big_series.empty:
            fig, ax = plt.subplots()
            ax.bar(big_series.index, big_series.values, color='steelblue')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No investment data available.")

    with col2:
        vertical_series = investor_df.groupby('vertical')['amount'].sum()
        st.subheader('Sectors invested in')
        if not vertical_series.empty:
            fig1, ax1 = plt.subplots()
            ax1.pie(vertical_series, labels=vertical_series.index, autopct="%0.01f%%")
            st.pyplot(fig1)
        else:
            st.info("No sector data available for this investor.")

    year_series = investor_df.groupby('year')['amount'].sum()
    st.subheader('YoY Investment')
    if not year_series.empty:
        fig2, ax2 = plt.subplots()
        ax2.plot(year_series.index, year_series.values, marker='o')
        st.pyplot(fig2)
    else:
        st.info("No yearly data available.")


# Sidebar 
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    
    selected_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find StartUp Details')
    if btn1:
        load_startup_details(selected_startup)
    else:
        st.title('StartUp Analysis')
        st.info(' Select a startup from the sidebar and click **Find StartUp Details**')

else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)
    else:
        st.title('Investor Analysis')
        st.info(' Select an investor from the sidebar and click **Find Investor Details**')
        
