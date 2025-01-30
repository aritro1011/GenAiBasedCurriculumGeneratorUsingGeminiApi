import streamlit as st
import google.generativeai as genai
#from config import GEMINI_API_KEY   Use this when running locally
from docx import Document
from io import BytesIO
import datetime
import os

# Configure the API key securely from Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] #remove this line when running locally

# Configure the API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

# Set up Streamlit page configuration
st.set_page_config(page_title="CURRICULA-GEN", page_icon="🤖")
st.title("CURRICULA-GEN")

# Initialize chat in session state if it doesn't exist
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()
    
    # Send initial message to set up the assistant's role
    initial_message = """You are an advanced human curriculum designer.
 Your Response should appear as human as possible(Simulate a 21 year old human who is interning at an edtech startup as a curriculum designer).
You will create structured curricula with:
1. Create structured curricula with:
   - Context and Background 
   - Course Objectives
   - Module Structure (topics and sub-topics)
   - Learning Outcomes
   - Resources and References Should be in the form of a list of links, all of which should be perfectly valid and functional

You will:
- Ensure well-researched, properly cited information
- Maintain logical organization
- Ask clarifying questions when needed
- Follow best practices for curriculum design"""
    
    st.session_state.chat.send_message(initial_message)

# Curriculum Generator Interface
st.subheader("Curriculum Parameters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    course_type = st.selectbox(
        "Course Type",
        ["Course", "Workshop"],
        help="Workshop: One-day basic learning. Course: Detailed, comprehensive learning"
    )
with col2:
    num_modules = st.number_input("Number of Modules", min_value=1, max_value=10, value=3)
with col3:
    topics_per_module = st.number_input("Topics per Module", min_value=1, max_value=8, value=3)
col4, _, _ = st.columns([1, 1, 1]) 
with col4:
    subtopics_per_topic = st.number_input("Maximum Sub-topics per Topic", min_value=0, max_value=5, value=2)

# Radio button to enable proficiency selection
enable_proficiency = st.radio("Do you want to select a Proficiency Level?", ["No", "Yes"], index=0)

# Show proficiency level only if user selects "Yes"
if enable_proficiency == "Yes":
    proficiency_level = st.selectbox("Select Proficiency Level", ["Beginner", "Intermediate", "Professional"])
else:
    proficiency_level = None  # Set to None if not selected

st.subheader("Course Details")
course_topic = st.text_area("Enter Course Topic:", height=100)
primary_resource_url = st.text_input("Primary Resource URL (optional):", "")

if st.button("Generate Curriculum Structure"):
    if course_topic:
        with st.spinner("Generating curriculum structure..."):
            # Modify prompt to include proficiency level if selected
            proficiency_prompt = f" and should be suitable for a {proficiency_level.lower()} level" if proficiency_level else ""
            
            detailed_prompt = f"""Please create a {course_type.lower()} curriculum structure for:
            Course Topic: {course_topic}
            Number of modules: {num_modules}
            Topics per module: {topics_per_module}
            Maximum sub-topics per topic: {subtopics_per_topic}
            Primary resource URL: {primary_resource_url if primary_resource_url else 'Not provided'}
            
            {'For this workshop, please ensure:'  if course_type == "Workshop" else 'For this course, please ensure:'}
            {'''- Content is suitable for one-day delivery
            - Topics are fundamental and beginner-friendly
            - Practical exercises are quick and engaging
            - Time management suggestions for each module
            - Focus on essential concepts only''' if course_type == "Workshop" else '''- Comprehensive coverage of topics
            - Progressive difficulty levels
            - In-depth theoretical and practical components
            - Detailed exploration of advanced concepts
            - Long-term learning objectives'''}

            {proficiency_prompt} 
            
            Please follow the specified format:
            1. Context 
            2. Objectives
            3. Module Structure (with topics and sub-topics)
            4. Learning Outcomes
            5. Resources(Please provide a list of links, all of which should be perfectly valid and functional.)

            For research and references, please consider:
            - Academic articles and research papers available online
            - Contemporary EdTech platforms' curriculum structures(Include atleast one such platform in the research)
            - Reputable online educational resources and articles
            - Industry standards and best practices
            
            Ensure to cite or reference key sources used in the curriculum structure.
            """
            
            response = st.session_state.chat.send_message(detailed_prompt)
            st.markdown(response.text)
            
            # Create Word document
            doc = Document()
            
            # Add title
            doc.add_heading(f'{course_type}: {course_topic}', 0)
            
            # Add generation date
            doc.add_paragraph(f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Add content
            doc.add_paragraph(response.text)
            
            # Save to BytesIO object
            doc_io = BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)
            
            # Add download button
            st.download_button(
                label="Download as Word Document",
                data=doc_io,
                file_name=f"curriculum_{course_topic.lower().replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Please enter a course topic.")

# Sidebar content
st.sidebar.markdown("""
## How to use
1. Enter the course topic
2. Set the number of modules, topics, and sub-topics
3. (Optional) Provide a primary resource URL
4. Click 'Generate Curriculum Structure' to get your curriculum outline

## Note
The curriculum expert will provide:
- Context and background
- Clear objectives
- Structured modules with topics
- Defined learning outcomes
- Integrated resources
""")
