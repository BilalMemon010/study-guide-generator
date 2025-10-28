import streamlit as st
from groq import Groq
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Study Guide Generator",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stDownloadButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'study_guide' not in st.session_state:
    st.session_state.study_guide = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

# Header
st.markdown('<p class="main-header">📚 AI Study Guide Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform your notes into comprehensive study materials</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.api_key if st.session_state.api_key else "",
        help="Get your free API key from console.groq.com"
    )
    if api_key:
        st.session_state.api_key = api_key
    
    st.divider()
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768"
        ],
        help="llama-3.3-70b recommended for best results"
    )
    
    # Study guide type
    guide_type = st.selectbox(
        "Study Guide Type",
        [
            "Comprehensive (All sections)",
            "Summary Only",
            "Definitions Focus",
            "Practice Questions Focus"
        ]
    )
    
    # Detail level
    detail_level = st.select_slider(
        "Detail Level",
        options=["Brief", "Moderate", "Detailed", "Very Detailed"],
        value="Detailed"
    )
    
    # Number of questions
    num_questions = st.slider(
        "Practice Questions",
        min_value=3,
        max_value=20,
        value=10,
        step=1
    )
    
    # Question types
    st.subheader("Question Types")
    include_mcq = st.checkbox("Multiple Choice", value=True)
    include_short = st.checkbox("Short Answer", value=True)
    include_essay = st.checkbox("Essay Questions", value=False)
    
    st.divider()
    
    # Info section
    st.info("""
    **How to use:**
    1. Enter your Groq API key
    2. Paste your notes or upload a file
    3. Configure settings
    4. Click Generate
    5. Download your study guide
    """)

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📝 Input Your Study Material")
    
    # Tabs for different input methods
    tab1, tab2 = st.tabs(["✍️ Paste Text", "📄 Upload File"])
    
    with tab1:
        study_material = st.text_area(
            "Paste your notes, textbook excerpts, or lecture content here:",
            height=400,
            placeholder="Enter your study material here...\n\nExample:\n- Chapter notes\n- Lecture transcripts\n- Textbook excerpts\n- Any educational content"
        )
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload a text file (.txt, .md)",
            type=['txt', 'md'],
            help="Upload your notes as a text file"
        )
        
        if uploaded_file is not None:
            study_material = uploaded_file.read().decode('utf-8')
            st.success(f"✅ File loaded: {uploaded_file.name}")
            with st.expander("Preview uploaded content"):
                st.text(study_material[:500] + "..." if len(study_material) > 500 else study_material)

with col2:
    st.subheader("🎯 Quick Tips")
    st.markdown("""
    **Best Practices:**
    - 📖 Include complete concepts, not fragments
    - 🔑 Add key terms and definitions
    - 📊 Include examples if available
    - 📝 More content = better study guide
    
    **Optimal Length:**
    - Minimum: 200 words
    - Recommended: 500-2000 words
    - Maximum: No limit!
    """)
    
    if study_material:
        word_count = len(study_material.split())
        st.metric("Word Count", f"{word_count:,}")
        
        if word_count < 100:
            st.warning("⚠️ Content is quite short. Add more for better results.")
        elif word_count < 200:
            st.info("ℹ️ Decent length. More content will improve quality.")
        else:
            st.success("✅ Great! Sufficient content for a comprehensive guide.")

# Generate button
st.divider()
generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])

with generate_col2:
    generate_button = st.button("🚀 Generate Study Guide", use_container_width=True, type="primary")

# Generation logic
if generate_button:
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar!")
    elif not study_material or len(study_material.strip()) < 50:
        st.error("⚠️ Please provide study material (at least 50 characters)")
    else:
        try:
            with st.spinner("🤖 AI is crafting your study guide... This may take 30-60 seconds..."):
                # Initialize Groq client
                client = Groq(api_key=st.session_state.api_key)
                
                # Build the prompt based on user preferences
                detail_mapping = {
                    "Brief": "concise and to-the-point",
                    "Moderate": "balanced with good coverage",
                    "Detailed": "comprehensive and thorough",
                    "Very Detailed": "extremely detailed with in-depth explanations"
                }
                
                # Question type string
                question_types = []
                if include_mcq:
                    question_types.append("multiple choice questions")
                if include_short:
                    question_types.append("short answer questions")
                if include_essay:
                    question_types.append("essay questions")
                
                question_type_str = ", ".join(question_types) if question_types else "practice questions"
                
                # Main prompt construction
                if guide_type == "Comprehensive (All sections)":
                    prompt = f"""Create a {detail_mapping[detail_level]} study guide from the following material.

STUDY MATERIAL:
{study_material}

Generate a comprehensive study guide with these sections:

1. **OVERVIEW** - Brief summary of the main topic and its importance

2. **KEY CONCEPTS** - Main ideas explained clearly with examples where relevant

3. **IMPORTANT DEFINITIONS** - Essential terms with clear, concise definitions

4. **DETAILED NOTES** - {detail_mapping[detail_level].capitalize()} explanation of the content, organized by subtopics

5. **PRACTICE QUESTIONS** - Create {num_questions} {question_type_str}:
{f"   - Multiple choice questions (with 4 options and correct answer)" if include_mcq else ""}
{f"   - Short answer questions" if include_short else ""}
{f"   - Essay questions with key points to cover" if include_essay else ""}

6. **STUDY TIPS** - Memory aids, mnemonics, and connections to help remember the material

7. **SUMMARY** - Quick review of the most critical points

Format everything in clear markdown with proper headers, bullet points, and emphasis where needed."""

                elif guide_type == "Summary Only":
                    prompt = f"""Create a {detail_mapping[detail_level]} summary of the following study material.

STUDY MATERIAL:
{study_material}

Provide:
1. Main topic overview
2. Key points and concepts (organized logically)
3. Important takeaways
4. Quick review summary

Be {detail_mapping[detail_level]} and use clear markdown formatting."""

                elif guide_type == "Definitions Focus":
                    prompt = f"""Extract and explain all important terms and concepts from the following material.

STUDY MATERIAL:
{study_material}

Create a comprehensive definitions guide with:
1. **TERM**: Clear, {detail_mapping[detail_level]} definition
2. Context of how it's used
3. Examples where helpful
4. Related terms

Organize alphabetically and use clear markdown formatting."""

                else:  # Practice Questions Focus
                    prompt = f"""Create {num_questions} practice questions from the following study material.

STUDY MATERIAL:
{study_material}

Generate {question_type_str}:
{f"- Multiple choice questions with 4 options, correct answer, and brief explanation" if include_mcq else ""}
{f"- Short answer questions with sample answers" if include_short else ""}
{f"- Essay questions with key points that should be covered" if include_essay else ""}

Include a variety of difficulty levels and ensure questions cover all major concepts.
Format with clear markdown and proper numbering."""

                # Make API call
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert educational content creator who creates comprehensive, well-organized study guides. You excel at identifying key concepts, creating effective practice questions, and organizing information for optimal learning."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=model,
                    temperature=0.7,
                    max_tokens=8000
                )
                
                # Store the result
                st.session_state.study_guide = chat_completion.choices[0].message.content
                
            st.success("✅ Study guide generated successfully!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error generating study guide: {str(e)}")
            st.info("💡 Tip: Check your API key and make sure you have credits remaining")

# Display results
if st.session_state.study_guide:
    st.divider()
    st.header("📖 Your Study Guide")
    
    # Display the study guide
    st.markdown(st.session_state.study_guide)
    
    # Download options
    st.divider()
    st.subheader("💾 Download Your Study Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download as markdown
        st.download_button(
            label="📥 Download as Markdown",
            data=st.session_state.study_guide,
            file_name=f"study_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    with col2:
        # Download as text
        st.download_button(
            label="📥 Download as Text",
            data=st.session_state.study_guide,
            file_name=f"study_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col3:
        # Copy to clipboard button (visual only, actual copying happens on client side)
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.info("📋 Content displayed above - use your browser's copy function or download buttons")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Built with ❤️ using Streamlit and Groq AI | Made for students, by students</p>
    <p><small>Tip: For best results, provide well-organized notes with clear concepts</small></p>
</div>
""", unsafe_allow_html=True)
