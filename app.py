import streamlit as st
import os
import mysql.connector
from pyresparser import ResumeParser
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

# ------------------ Page Config ------------------
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.sidebar.image("logo/logo.png", use_container_width=True)
st.sidebar.title("AI Resume Analyzer")
st.sidebar.write("Upload your resume to get personalized insights!")

# ------------------ Database Insert Function ------------------
def insert_into_db(data, filename):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="Ommni@123",  # Replace with your MySQL password
            database="resume_analyzer_db"
        )
        cursor = conn.cursor()
        sql = """
        INSERT INTO resume_data (name, email, phone, degree, experience, skills, filename)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get('name'),
            data.get('email'),
            data.get('mobile_number'),
            data.get('degree'),
            data.get('total_experience'),
            ', '.join(data.get('skills', [])),
            filename
        )
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")

# ------------------ Resume Upload ------------------
st.header("📄 Upload Your Resume")
uploaded_file = st.file_uploader("Choose your resume (PDF/DOCX)", type=["pdf", "docx"])

# ------------------ Video Sections ------------------
with st.expander("🎥 Resume Building Videos"):
    for link in resume_videos:
        st.video(link)

with st.expander("🎤 Interview Preparation Videos"):
    for link in interview_videos:
        st.video(link)

# ------------------ Resume Analysis ------------------
if uploaded_file is not None:
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing your resume..."):
            save_path = os.path.join("Uploaded_Resumes", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                data = ResumeParser(save_path).get_extracted_data()

                if data:
                    insert_into_db(data, uploaded_file.name)
                    st.success("✅ Resume Analyzed Successfully!")

                    st.subheader("👤 Candidate Information")
                    st.write(f"**Name:** {data.get('name', 'N/A')}")
                    st.write(f"**Email:** {data.get('email', 'N/A')}")
                    st.write(f"**Phone:** {data.get('mobile_number', 'N/A')}")
                    st.write(f"**Degree:** {data.get('degree', 'N/A')}")
                    st.write(f"**Experience:** {data.get('total_experience', 'N/A')} years")
                    st.write(f"**Skills:** {', '.join(data.get('skills', []))}")

                    # ------------------ Course Recommendations ------------------
                    st.subheader("🎯 Recommended Courses")

                    skills = [skill.lower() for skill in data.get("skills", [])]

                    def display_courses(title, courses):
                        st.markdown(f"**{title}**")
                        for name, link in courses:
                            st.markdown(f"- [{name}]({link})")

                    if any(skill in skills for skill in ['ml', 'machine learning', 'data science', 'python']):
                        display_courses("📊 Data Science / ML Courses", ds_course)
                    if any(skill in skills for skill in ['html', 'css', 'javascript', 'django', 'react']):
                        display_courses("🌐 Web Development Courses", web_course)
                    if any(skill in skills for skill in ['android', 'kotlin', 'flutter']):
                        display_courses("📱 Android Development Courses", android_course)
                    if any(skill in skills for skill in ['ios', 'swift', 'objective-c']):
                        display_courses("🍏 iOS Development Courses", ios_course)
                    if any(skill in skills for skill in ['ui', 'ux', 'design']):
                        display_courses("🎨 UI/UX Courses", uiux_course)
                else:
                    st.error("⚠️ Failed to extract data. Try another file.")
            except Exception as e:
                st.error(f"🚨 Error: {str(e)}")
