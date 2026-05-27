"""
Neuralcanvas - UI Views and Components
Professional Developer-Friendly Interface
"""
import streamlit as st
import time
from PIL import Image
import io
from utils import (
    login, signup, logout, upload_image, process_image, 
    get_job_status, get_image, get_user_jobs, api_request,
    classify_cartoon, get_classifier_info, get_all_identities,
    generate_cartoon, get_generator_info, format_identity_name,
    check_backend_status
)
from styles import glass_card, render_header, render_status


# ============ AUTH PAGE ============

def render_auth_page():
    """Render the authentication page with login/signup."""
    render_header("Neuralcanvas AI", "v1.0.0")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
            <h1 style='font-size: 3rem; font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem;'>
                The Developer's <span style='color: var(--accent-blue);'>AI Creative</span> Suite.
            </h1>
            <p style='color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 2rem;'>
                Transform images, classify cartoon faces, and generate AI art with a professional-grade interface. 
                Built for speed, precision, and developer experience.
            </p>
        """, unsafe_allow_html=True)
        
        # Feature Grid
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            glass_card("Transform images in seconds with GPU acceleration.", "🚀 Lightning Fast")
            glass_card("Recognize 100 public figures in cartoon images.", "🎭 Face ID")
        with f_col2:
            glass_card("Cartoon, Pencil, Watercolor & more.", "🎨 5 Art Styles")
            glass_card("Your images are processed securely.", "🔒 Secure")

    with col2:
        # Auth Forms
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_signup_form()
    
    # Backend Status
    st.markdown("<br>", unsafe_allow_html=True)
    render_status("API Backend Status", online=check_backend_status())


def render_login_form():
    """Render login form."""
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Sign In", use_container_width=True)
        
        if submit:
            if username and password:
                with st.spinner("Authenticating..."):
                    success, error = login(username, password)
                    if success:
                        st.success("✅ Welcome back!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
            else:
                st.warning("⚠️ Please fill in all fields")


def render_signup_form():
    """Render signup form."""
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("signup_form", clear_on_submit=False):
        email = st.text_input(
            "Email Address",
            placeholder="you@example.com",
            key="signup_email"
        )
        username = st.text_input(
            "Username",
            placeholder="Choose a unique username",
            key="signup_username"
        )
        full_name = st.text_input(
            "Full Name (optional)",
            placeholder="Your display name",
            key="signup_fullname"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Min 8 characters",
            key="signup_password"
        )
        confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Repeat password",
            key="signup_confirm"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🎨 Create Account", use_container_width=True)
        
        if submit:
            if email and username and password:
                if len(password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                elif password != confirm:
                    st.error("❌ Passwords do not match")
                else:
                    with st.spinner("Creating your account..."):
                        success, error = signup(email, username, password, full_name or None)
                        if success:
                            st.success("✅ Account created!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {error}")
            else:
                st.warning("⚠️ Please fill in all required fields")


# ============ SIDEBAR ============

def render_sidebar():
    """Render the sidebar with user info and navigation."""
    with st.sidebar:
        # User Profile
        if st.session_state.user:
            user = st.session_state.user
            display_name = user.get('full_name') or user.get('username', 'User')
            
            st.markdown(f"""
            <div style="padding: 1rem; background: var(--bg-tertiary); border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 1.5rem;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Active Session</div>
                <div style="font-weight: 600; color: var(--text-primary);">{display_name}</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">{user.get('email', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Stats
        st.markdown("### 📊 System Metrics")
        result, _ = get_user_jobs(per_page=100)
        if result:
            jobs = result.get("jobs", [])
            completed = sum(1 for j in jobs if j['status'] == 'completed')
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Jobs", len(jobs))
            with col2:
                st.metric("Success", completed)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Model Status
        st.markdown("### 🤖 Model Registry")
        
        # Classifier Status
        classifier_info, _ = get_classifier_info()
        render_status("Classifier v1.2", online=classifier_info.get('model_loaded') if classifier_info else False)
        
        # Generator Status  
        generator_info, _ = get_generator_info()
        render_status("Generator v2.0", online=generator_info.get('model_loaded') if generator_info else False)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logout
        if st.button("🚪 Sign Out", use_container_width=True):
            logout()
            st.rerun()


# ============ MAIN APP ============

def render_main_app():
    """Render the main application."""
    render_sidebar()
    
    render_header("Dashboard", "v1.0.0")
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🖼️ Transform",
        "🎭 Classify", 
        "✨ Generate",
        "📚 Gallery"
    ])
    
    with tab1:
        render_transform_tab()
    
    with tab2:
        render_classify_tab()
    
    with tab3:
        render_generator_tab()
    
    with tab4:
        render_gallery_tab()


# ============ TRANSFORM TAB ============

def render_transform_tab():
    """Render the image transformation tab."""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📤 Input Source")
        
        uploaded_file = st.file_uploader(
            "Upload image",
            type=["jpg", "jpeg", "png", "webp"],
            key="transform_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Original Image", use_column_width=True)
        
        st.markdown("### 🎨 Style Configuration")
        
        styles = [
            ("cartoon", "🎬", "Cartoon"),
            ("pencil_sketch", "✏️", "Pencil"),
            ("color_pencil", "🖍️", "Color Pencil"),
            ("edge_preserve", "🔲", "Edge"),
            ("watercolor", "💧", "Watercolor"),
        ]
        
        style = st.selectbox(
            "Select transformation style",
            options=[s[0] for s in styles],
            format_func=lambda x: next(f"{s[1]} {s[2]}" for s in styles if s[0] == x),
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Execute Transformation", use_container_width=True, disabled=not uploaded_file):
            process_transformation(uploaded_file, style)
    
    with col2:
        st.markdown("### ✨ Output Preview")
        
        if st.session_state.current_job:
            job = st.session_state.current_job
            
            if job.get("status") == "completed":
                processed_data, _ = get_image(job["id"], "processed")
                if processed_data:
                    st.image(processed_data, caption="Transformed Result", use_column_width=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.download_button(
                            "📥 Download",
                            data=processed_data,
                            file_name=f"toonified_{job['original_filename']}",
                            mime="image/png",
                            use_container_width=True
                        )
                    with col_b:
                        if st.button("🔄 Reset", use_container_width=True):
                            st.session_state.current_job = None
                            st.rerun()
        else:
            glass_card("Upload an image and select a style to begin the transformation process.", "Ready for Input")


def process_transformation(uploaded_file, style):
    """Process image transformation."""
    with st.spinner("Uploading..."):
        result, error = upload_image(uploaded_file, style)
    
    if error:
        st.error(f"❌ {error}")
        return
    
    job_id = result["job_id"]
    
    with st.spinner("Processing..."):
        process_result, process_error = process_image(job_id)
        
        if process_error:
            st.error(f"❌ {process_error}")
            return
        
        # Poll for completion
        progress = st.progress(0)
        for i in range(60):
            time.sleep(1)
            job_status, _ = get_job_status(job_id)
            if job_status:
                status = job_status.get("status")
                if status == "completed":
                    progress.progress(100)
                    st.session_state.current_job = job_status
                    st.rerun()
                    break
                elif status == "failed":
                    st.error(f"❌ {job_status.get('error_message')}")
                    break
            progress.progress(min((i + 1) * 2, 99))


# ============ CLASSIFY TAB ============

def render_classify_tab():
    """Render the cartoon classification tab."""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 🎭 Face Recognition")
        
        uploaded_file = st.file_uploader(
            "Upload cartoon face",
            type=["jpg", "jpeg", "png", "webp"],
            key="classify_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Input Face", use_column_width=True)
            
            if st.button("🔍 Run Inference", use_container_width=True):
                with st.spinner("Analyzing..."):
                    result, error = classify_cartoon(uploaded_file)
                
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.classifier_result = result
        else:
            st.info("Upload a cartoon face to identify the celebrity.")
    
    with col2:
        st.markdown("### 📊 Inference Results")
        
        if st.session_state.classifier_result:
            result = st.session_state.classifier_result
            if result.get('success'):
                predictions = result.get('predictions', [])
                for i, pred in enumerate(predictions[:3], 1):
                    name = format_identity_name(pred.get('display_name', pred.get('identity', 'Unknown')))
                    confidence = pred.get('confidence', 0)
                    
                    st.markdown(f"""
                        <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; color: var(--text-primary);">{name}</span>
                                <span style="color: var(--accent-blue); font-weight: 700;">{confidence:.1f}%</span>
                            </div>
                            <div style="height: 4px; background: var(--bg-tertiary); border-radius: 2px; margin-top: 0.5rem;">
                                <div style="height: 100%; width: {confidence}%; background: var(--accent-blue); border-radius: 2px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.button("🔄 Clear Results", use_container_width=True):
                    st.session_state.classifier_result = None
                    st.rerun()
        else:
            glass_card("Inference results will appear here after processing.", "No Data")


# ============ GENERATOR TAB ============

def render_generator_tab():
    """Render the AI cartoon generator tab."""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### ✨ GAN Generator")
        
        uploaded_file = st.file_uploader(
            "Upload photo",
            type=["jpg", "jpeg", "png", "webp"],
            key="generator_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Input Photo", use_column_width=True)
            
            if st.button("🎨 Generate Art", use_container_width=True):
                with st.spinner("Generating..."):
                    result, error = generate_cartoon(uploaded_file)
                
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.generator_result = result
        else:
            st.info("Upload a photo to generate a cartoon version.")
    
    with col2:
        st.markdown("### 🖼️ Generated Output")
        
        if st.session_state.generator_result:
            st.image(st.session_state.generator_result, caption="AI Generated", use_column_width=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    "📥 Download",
                    data=st.session_state.generator_result,
                    file_name="generated_art.png",
                    mime="image/png",
                    use_container_width=True
                )
            with col_b:
                if st.button("🔄 New Generation", use_container_width=True):
                    st.session_state.generator_result = None
                    st.rerun()
        else:
            glass_card("The generated cartoon will be displayed here.", "Awaiting Generation")


# ============ GALLERY TAB ============

def render_gallery_tab():
    """Render the user's gallery tab."""
    st.markdown("### 📚 Job History")
    
    result, error = get_user_jobs(per_page=50)
    if error:
        st.error(f"❌ {error}")
        return
    
    jobs = result.get("jobs", [])
    if not jobs:
        st.info("No transformations found in your history.")
        return
    
    # Grid layout
    cols = st.columns(3)
    for idx, job in enumerate(jobs):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                    <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;">{job['style']}</div>
                        <div style="font-weight: 500; margin-bottom: 0.5rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{job['original_filename']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if job['status'] == 'completed':
                    if st.button("View Result", key=f"view_{job['id']}", use_container_width=True):
                        st.session_state.current_job = job
                        st.rerun()
                else:
                    st.caption(f"Status: {job['status']}")

