from fpdf import FPDF
import base64
import pandas as pd
import io
from datetime import datetime
import os
import streamlit as st
import matplotlib.pyplot as plt

st.title("CNG Efficiency Analyzer")

st.markdown("""
This app helps you compare fuel costs between Petrol and CNG, calculate your monthly savings, 
and estimate the payback period for switching to CNG. You can download your results and track them over time.
""")

def calculate_cost_per_km(fuel_price, consumption_per_100km):
    return (fuel_price * consumption_per_100km) / 100

def calculate_monthly_savings(distance_per_month, petrol_cost_per_km, cng_cost_per_km):
    return distance_per_month * (petrol_cost_per_km - cng_cost_per_km)

def calculate_payback(conversion_cost, monthly_savings):
    if monthly_savings > 0:
        return conversion_cost / monthly_savings
    else:
        return float('inf')



st.header("🔧 Input Vehicle & Fuel Details")

# User Inputs
petrol_price = st.number_input("Petrol price per litre (₦)", min_value=0.0, value=680.0)
cng_price = st.number_input("CNG price per SCM (₦)", min_value=0.0, value=230.0)
distance_per_month = st.number_input("Average distance per month (km)", min_value=0.0, value=1000.0)
petrol_consumption = st.number_input("Petrol consumption per 100km (litres)", min_value=0.0, value=12.5)
cng_consumption = st.number_input("CNG consumption per 100km (SCM)", min_value=0.0, value=6.5)
conversion_cost = st.number_input("CNG Conversion cost (₦)", min_value=0.0, value=250000.0)

def generate_pdf(petrol_cost_km, cng_cost_km, monthly_savings, payback_months):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="CNG vs Petrol Efficiency Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Petrol Cost per km: NGN {petrol_cost_km:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"CNG Cost per km: NGN {cng_cost_km:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Monthly Savings: NGN {monthly_savings:.2f}", ln=True)

    if payback_months != float('inf'):
        pdf.cell(200, 10, txt=f"Payback Period: {payback_months:.1f} months", ln=True)
    else:
        pdf.cell(200, 10, txt="No Payback (No Savings)", ln=True)

    return pdf.output(dest="S").encode("latin-1")



if st.button("Analyze"):
    petrol_cost_per_km = calculate_cost_per_km(petrol_price, petrol_consumption)
    cng_cost_per_km = calculate_cost_per_km(cng_price, cng_consumption)
    monthly_savings = calculate_monthly_savings(distance_per_month, petrol_cost_per_km, cng_cost_per_km)
    payback_months = calculate_payback(conversion_cost, monthly_savings)

    st.subheader("📊 Results")
    st.metric("Petrol Cost/km", f"₦{petrol_cost_per_km:.2f}")
    st.metric("CNG Cost/km", f"₦{cng_cost_per_km:.2f}")
    st.metric("Monthly Savings", f"₦{monthly_savings:.2f}")

    # 🗂️ Logging input & results to CSV
    log_file = "cng_usage_log.csv"

    log_data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Petrol Price (₦/L)": [petrol_price],
        "CNG Price (₦/SCM)": [cng_price],
        "Distance (km/month)": [distance_per_month],
        "Petrol Usage (L/100km)": [petrol_consumption],
        "CNG Usage (SCM/100km)": [cng_consumption],
        "Petrol Cost/km": [petrol_cost_per_km],
        "CNG Cost/km": [cng_cost_per_km],
        "Monthly Savings (₦)": [monthly_savings],
        "Payback Period (months)": [payback_months if payback_months != float('inf') else "No Payback"]
    }

    log_df = pd.DataFrame(log_data)

    # Append or create log file
    if os.path.exists(log_file):
        log_df.to_csv(log_file, mode='a', header=False, index=False)
    else:
        log_df.to_csv(log_file, index=False)

    st.success("✅ Your input and results have been logged.")

        

    if payback_months != float('inf'):
        st.metric("Payback Period", f"{payback_months:.1f} months")

        # 🧠 Smart Recommendation
        st.subheader("🧠 Recommendation")
        if payback_months != float('inf'):
            if payback_months <= 6:
                st.success(f"✅ Great! Switching to CNG is a smart financial choice. You'll recover the cost in about {payback_months:.1f} months.")
            elif payback_months <= 12:
                st.info(f"👍 CNG could still be worth it. You'll break even in about {payback_months:.1f} months.")
            else:
                st.warning(f"⚠️ Long payback period ({payback_months:.1f} months). CNG may not be cost-effective for your usage.")
        else:
            st.error("🚫 Based on your input, switching to CNG may not offer any cost savings.")
            

    else:
        st.warning("No savings from CNG. Payback period cannot be calculated.")

                # 🧠 Smart Recommendation
        st.subheader("🧠 Recommendation")
        if payback_months != float('inf'):
            if payback_months <= 6:
                st.success(f"✅ Great! Switching to CNG is a smart financial choice. You'll recover the cost in about {payback_months:.1f} months.")
            elif payback_months <= 12:
                st.info(f"👍 CNG could still be worth it. You'll break even in about {payback_months:.1f} months.")
            else:
                st.warning(f"⚠️ Long payback period ({payback_months:.1f} months). CNG may not be cost-effective for your usage.")
        else:
            st.error("🚫 Based on your input, switching to CNG may not offer any cost savings.")
            


        

    # Chart
    monthly_petrol_cost = distance_per_month * petrol_cost_per_km
    monthly_cng_cost = distance_per_month * cng_cost_per_km

    labels = ['Petrol', 'CNG', 'Savings']
    values = [monthly_petrol_cost, monthly_cng_cost, monthly_savings]
    colors = ['red', 'green', 'blue']

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=colors)
    ax.set_ylabel('₦ (Monthly Cost)')
    ax.set_title('Monthly Cost Comparison: Petrol vs CNG')
    st.pyplot(fig)

    # 📈 Line Chart: Cumulative Monthly Savings
    months = list(range(1, 13))
    monthly_savings_list = [monthly_savings * m for m in months]

    fig2, ax2 = plt.subplots()
    ax2.plot(months, monthly_savings_list, marker='o', linestyle='-', color='blue')
    ax2.set_title('Cumulative Savings Over 12 Months')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('₦ (Cumulative Savings)')
    ax2.grid(True)

    st.pyplot(fig2)

    # 📄 Generate downloadable PDF
    pdf_data = generate_pdf(petrol_cost_per_km, cng_cost_per_km, monthly_savings, payback_months)
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="cng_report.pdf">📄 Download Report as PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

    # 📊 Prepare data for Excel
    excel_data = {
        'Petrol Cost/km': [petrol_cost_per_km],
        'CNG Cost/km': [cng_cost_per_km],
        'Monthly Savings': [monthly_savings],
        'Payback Period (months)': [payback_months if payback_months != float('inf') else "No Payback"]
    }

    df = pd.DataFrame(excel_data)
    # 📥 Convert to Excel in memory
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    # 📎 Download link for Excel file
    st.download_button(
        label="📥 Download Report as Excel",
        data=excel_buffer,
        file_name="cng_efficiency_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


st.markdown("""
---
Built with ❤️ by **Blessing** | 🚗 AI-Enhanced Automotive Tools  
For training, support, or collaboration: 📱 +234-7051531665  
""", unsafe_allow_html=True)

