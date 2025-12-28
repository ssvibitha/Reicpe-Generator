import streamlit as st
st.title("Health report to recipes")

st.header("Upload your health report and get personalised recipes.")

uploaded_file =st.file_uploader("Upload an image or pdf")

if uploaded_file:
    st.write("File uploaded: ", uploaded_file.name)