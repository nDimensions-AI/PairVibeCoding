"""
Face Attendance System - Streamlit Frontend

A demo application for the mobile face attendance system.
Provides UI for student registration, attendance marking, and reports.
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Page configuration
st.set_page_config(
    page_title="Face Attendance System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #721c24;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 1rem;
        color: #856404;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if the API is available."""
    try:
        response = requests.get(f"{API_URL.replace('/api/v1', '')}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main application entry point."""
    st.markdown('<h1 class="main-header">👤 Face Attendance System</h1>', unsafe_allow_html=True)

    # Check API health
    api_healthy = check_api_health()

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/face-id.png", width=80)
        st.title("Navigation")

        # API Status indicator
        if api_healthy:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.info(f"API URL: {API_URL}")

        st.divider()

        # Navigation
        page = st.radio(
            "Select Page",
            ["🏠 Home", "📝 Registration", "✅ Attendance", "📊 Reports", "⚙️ Settings"],
            label_visibility="collapsed"
        )

        st.divider()

        # Quick stats
        if api_healthy:
            try:
                stats = requests.get(f"{API_URL}/reports/stats", timeout=5).json()
                st.metric("Total Students", stats.get("total_students", 0))
                st.metric("Today's Attendance", stats.get("today_attendance", 0))
            except:
                pass

    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 Registration":
        show_registration_page()
    elif page == "✅ Attendance":
        show_attendance_page()
    elif page == "📊 Reports":
        show_reports_page()
    elif page == "⚙️ Settings":
        show_settings_page()


def show_home_page():
    """Display the home page."""
    st.header("Welcome to Face Attendance System")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📝 Registration
        Enroll students by capturing their face photo.
        The system generates a unique 512-D face vector for each student.
        """)
        if st.button("Go to Registration", key="home_reg"):
            st.session_state.page = "📝 Registration"
            st.rerun()

    with col2:
        st.markdown("""
        ### ✅ Attendance
        Mark attendance using facial recognition.
        Includes liveness detection to prevent spoofing.
        """)
        if st.button("Go to Attendance", key="home_att"):
            st.session_state.page = "✅ Attendance"
            st.rerun()

    with col3:
        st.markdown("""
        ### 📊 Reports
        View attendance reports and analytics.
        Track attendance patterns and system performance.
        """)
        if st.button("Go to Reports", key="home_rep"):
            st.session_state.page = "📊 Reports"
            st.rerun()

    st.divider()

    # Features
    st.subheader("Key Features")

    feat_col1, feat_col2 = st.columns(2)

    with feat_col1:
        st.markdown("""
        #### 🎯 High Accuracy
        - >99.5% match accuracy using ArcFace embeddings
        - 512-dimensional face vectors for precise identification

        #### ⚡ Fast Processing
        - <1.5 seconds from scan to result
        - <10ms vector search across 5,000 identities
        """)

    with feat_col2:
        st.markdown("""
        #### 🛡️ Anti-Spoofing
        - Passive liveness detection
        - Blocks photo and screen attacks
        - Multiple texture and color analysis checks

        #### 📍 Location Tracking
        - Optional GPS logging
        - Device identification
        - Complete audit trail
        """)


def show_registration_page():
    """Display the registration page."""
    st.header("📝 Student Registration")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Student Information")

        student_id = st.text_input("Student ID *", placeholder="e.g., STU001")
        name = st.text_input("Full Name *", placeholder="e.g., John Doe")
        email = st.text_input("Email", placeholder="e.g., john@example.com")
        department = st.selectbox(
            "Department",
            ["", "Computer Science", "Engineering", "Business", "Arts", "Science", "Other"]
        )

    with col2:
        st.subheader("Face Photo")

        # Option to use camera or upload
        input_method = st.radio(
            "Input Method",
            ["📷 Camera", "📤 Upload"],
            horizontal=True
        )

        if input_method == "📷 Camera":
            image = st.camera_input("Capture your face")
        else:
            image = st.file_uploader(
                "Upload a clear face photo",
                type=["jpg", "jpeg", "png"],
                help="Please upload a clear photo of your face with good lighting"
            )

        if image:
            st.image(image, caption="Preview", use_container_width=True)

    st.divider()

    # Validation button
    if st.button("Validate Image", type="secondary"):
        if image:
            with st.spinner("Validating..."):
                files = {"image": image.getvalue()}
                try:
                    response = requests.post(
                        f"{API_URL}/validate-face",
                        files={"image": ("image.jpg", image.getvalue(), "image/jpeg")}
                    )
                    result = response.json()

                    if result.get("valid"):
                        st.success(f"✅ Image is valid! Quality: {result.get('face_quality', 0):.1%}")
                    else:
                        st.warning(f"⚠️ {result.get('message', 'Image validation failed')}")

                    with st.expander("Validation Details"):
                        st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please capture or upload an image first")

    # Registration button
    if st.button("Register Student", type="primary"):
        if not student_id or not name:
            st.error("Please fill in Student ID and Name")
        elif not image:
            st.error("Please capture or upload a face photo")
        else:
            with st.spinner("Registering student..."):
                try:
                    data = {
                        "student_id": student_id,
                        "name": name,
                        "email": email if email else None,
                        "department": department if department else None
                    }

                    response = requests.post(
                        f"{API_URL}/register",
                        data=data,
                        files={"image": ("image.jpg", image.getvalue(), "image/jpeg")}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result.get('message', 'Registration successful!')}")
                        st.balloons()

                        with st.expander("Registration Details"):
                            st.json(result)
                    else:
                        error = response.json()
                        st.error(f"❌ Registration failed: {error.get('detail', 'Unknown error')}")

                except Exception as e:
                    st.error(f"Error: {e}")


def show_attendance_page():
    """Display the attendance marking page."""
    st.header("✅ Mark Attendance")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Capture Face")

        input_method = st.radio(
            "Input Method",
            ["📷 Camera", "📤 Upload"],
            horizontal=True,
            key="attendance_input"
        )

        if input_method == "📷 Camera":
            image = st.camera_input("Look at the camera", key="attendance_camera")
        else:
            image = st.file_uploader(
                "Upload your face photo",
                type=["jpg", "jpeg", "png"],
                key="attendance_upload"
            )

        if image:
            st.image(image, caption="Your photo", use_container_width=True)

    with col2:
        st.subheader("Location (Optional)")

        use_location = st.checkbox("Include GPS location")

        latitude = None
        longitude = None

        if use_location:
            col_lat, col_lng = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", value=0.0, format="%.6f")
            with col_lng:
                longitude = st.number_input("Longitude", value=0.0, format="%.6f")

        device_id = st.text_input("Device ID (Optional)", placeholder="e.g., DEVICE001")

    st.divider()

    # Mark attendance button
    if st.button("Mark Attendance", type="primary", use_container_width=True):
        if not image:
            st.error("Please capture or upload a face photo")
        else:
            with st.spinner("Processing... Please wait"):
                try:
                    data = {}
                    if latitude and longitude:
                        data["latitude"] = latitude
                        data["longitude"] = longitude
                    if device_id:
                        data["device_id"] = device_id

                    response = requests.post(
                        f"{API_URL}/attendance",
                        data=data if data else None,
                        files={"image": ("image.jpg", image.getvalue(), "image/jpeg")}
                    )

                    result = response.json()
                    status = result.get("status", "failure")

                    if status == "success":
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Attendance Marked!</h3>
                            <p><strong>Student:</strong> {result.get('student_name', 'Unknown')} ({result.get('student_id', '')})</p>
                            <p><strong>Similarity:</strong> {result.get('match', {}).get('similarity_score', 0):.1%}</p>
                            <p><strong>Processing Time:</strong> {result.get('processing_time_ms', 0):.0f}ms</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()

                    elif status == "spoof_detected":
                        st.markdown(f"""
                        <div class="error-box">
                            <h3>🚫 Spoof Detected!</h3>
                            <p>{result.get('message', 'Photo or screen attack detected.')}</p>
                            <p>Please use a live camera and ensure your real face is visible.</p>
                        </div>
                        """, unsafe_allow_html=True)

                    elif status == "no_match":
                        st.markdown(f"""
                        <div class="warning-box">
                            <h3>❓ Face Not Recognized</h3>
                            <p>{result.get('message', 'No matching student found.')}</p>
                            <p>Please ensure you are registered in the system.</p>
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.error(f"❌ {result.get('message', 'Attendance marking failed')}")

                    # Show details
                    with st.expander("Full Response Details"):
                        st.json(result)

                except Exception as e:
                    st.error(f"Error: {e}")


def show_reports_page():
    """Display the reports page."""
    st.header("📊 Attendance Reports")

    tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "📋 Records", "👤 Student Report"])

    with tab1:
        # Dashboard with stats
        try:
            stats = requests.get(f"{API_URL}/reports/stats", timeout=10).json()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Students", stats.get("total_students", 0))
            with col2:
                st.metric("Today's Attendance", stats.get("today_attendance", 0))
            with col3:
                st.metric("Success Rate", f"{stats.get('success_rate', 0):.1%}")
            with col4:
                st.metric("Avg Processing", f"{stats.get('average_processing_time_ms', 0):.0f}ms")

            st.divider()

            # Daily summary chart
            daily = requests.get(f"{API_URL}/reports/daily-summary?days=7", timeout=10).json()

            if daily.get("summary"):
                import pandas as pd
                import plotly.express as px

                df = pd.DataFrame(daily["summary"])

                fig = px.bar(
                    df,
                    x="date",
                    y=["successful", "failed", "spoof_attempts"],
                    title="Daily Attendance Summary (Last 7 Days)",
                    barmode="stack",
                    labels={"value": "Count", "date": "Date", "variable": "Status"}
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading dashboard: {e}")

    with tab2:
        # Attendance records
        st.subheader("Attendance Records")

        col1, col2, col3 = st.columns(3)
        with col1:
            filter_student = st.text_input("Filter by Student ID")
        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "success", "no_match", "spoof_detected", "no_face_detected"]
            )
        with col3:
            limit = st.number_input("Records to show", value=50, min_value=10, max_value=500)

        if st.button("Load Records"):
            try:
                params = {"limit": limit}
                if filter_student:
                    params["student_id"] = filter_student
                if filter_status != "All":
                    params["status"] = filter_status

                records = requests.get(
                    f"{API_URL}/attendance/history",
                    params=params,
                    timeout=10
                ).json()

                if records.get("records"):
                    import pandas as pd
                    df = pd.DataFrame(records["records"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No records found")

            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        # Student report
        st.subheader("Individual Student Report")

        student_id = st.text_input("Enter Student ID", key="student_report_id")

        if st.button("Get Report") and student_id:
            try:
                report = requests.get(
                    f"{API_URL}/reports/student/{student_id}",
                    timeout=10
                ).json()

                if "error" in report:
                    st.error(report["error"])
                else:
                    student = report.get("student", {})
                    summary = report.get("attendance_summary", {})

                    st.markdown(f"""
                    ### {student.get('name', 'Unknown')}
                    - **Student ID:** {student.get('student_id', '')}
                    - **Department:** {student.get('department', 'N/A')}
                    - **Registered:** {student.get('registered_at', 'N/A')}
                    """)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Attempts", summary.get("total_attempts", 0))
                    with col2:
                        st.metric("Successful", summary.get("successful", 0))
                    with col3:
                        st.metric("Success Rate", f"{summary.get('success_rate', 0):.1%}")

            except Exception as e:
                st.error(f"Error: {e}")


def show_settings_page():
    """Display the settings page."""
    st.header("⚙️ Settings")

    st.subheader("API Configuration")

    api_url = st.text_input("API URL", value=API_URL)

    if st.button("Test Connection"):
        try:
            response = requests.get(f"{api_url.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Connection successful!")
                st.json(response.json())
            else:
                st.error(f"Connection failed: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    st.divider()

    st.subheader("Demo Data")

    st.markdown("""
    Generate demo student records to test the system's performance with large datasets.
    This creates fake students with random face embeddings.
    """)

    demo_count = st.number_input("Number of demo students", value=100, min_value=1, max_value=5000)

    if st.button("Generate Demo Data"):
        with st.spinner(f"Generating {demo_count} demo students..."):
            try:
                response = requests.post(
                    f"{API_URL}/reports/demo-data?count={demo_count}",
                    timeout=60
                )
                result = response.json()
                st.success(f"✅ {result.get('message', 'Demo data generated!')}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    st.subheader("System Information")

    st.markdown("""
    **Face Attendance System v1.0**

    - **Face Detection:** MediaPipe
    - **Face Embedding:** InsightFace (ArcFace)
    - **Vector Database:** Supabase with pgvector
    - **Liveness Detection:** Multi-factor passive anti-spoofing

    **Performance Targets:**
    - Match Accuracy: >99.5%
    - Processing Time: <1.5 seconds
    - Search Time: <10ms for 5,000 identities
    """)


if __name__ == "__main__":
    main()
