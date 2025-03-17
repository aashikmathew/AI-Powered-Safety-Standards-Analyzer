# safety_standards_analyzer/
# main.py - Entry point for the application

import os
import streamlit as st
from dotenv import load_dotenv
from components.document_processor import DocumentProcessor
from components.gap_analyzer import GapAnalyzer
from components.recommendation_engine import RecommendationEngine
from components.visualization import create_gap_visualization, create_standards_network

# Load environment variables
load_dotenv()

# Check if API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found. Please set it in your .env file.")
    st.stop()

def main():
    st.set_page_config(page_title="Safety Standards Analyzer", layout="wide")
    
    st.title("AI-Powered Safety Standards Analyzer")
    st.markdown("""
    This tool analyzes safety standards documents, identifies potential gaps, and generates 
    recommendations for standards updates based on current safety research and emerging technologies.
    """)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", 
                           ["Document Processing", "Gap Analysis", "Recommendations", "Dashboard"])
    
    # Initialize components
    doc_processor = DocumentProcessor()
    gap_analyzer = GapAnalyzer()
    recommendation_engine = RecommendationEngine()
    
    # Route to appropriate page
    if page == "Document Processing":
        show_document_processing(doc_processor)
    elif page == "Gap Analysis":
        show_gap_analysis(gap_analyzer, doc_processor)
    elif page == "Recommendations":
        show_recommendations(recommendation_engine, gap_analyzer)
    elif page == "Dashboard":
        show_dashboard(doc_processor, gap_analyzer, recommendation_engine)

def show_document_processing(doc_processor):
    st.header("Document Processing")
    
    st.subheader("Upload Standards Documents")
    uploaded_files = st.file_uploader("Choose documents to process", 
                                     type=["pdf", "docx", "txt"], 
                                     accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process Documents"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                doc_processor.process_document(file)
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("All documents processed successfully!")
            st.session_state['documents_processed'] = True
    
    if st.session_state.get('documents_processed', False):
        st.subheader("Document Database")
        st.write(f"Total documents: {doc_processor.get_document_count()}")
        st.write(f"Total sections: {doc_processor.get_section_count()}")
        
        st.subheader("Search Standards")
        search_query = st.text_input("Enter search terms")
        if search_query:
            results = doc_processor.search_standards(search_query)
            st.write(f"Found {len(results)} relevant sections")
            for i, result in enumerate(results):
                with st.expander(f"Result {i+1}: {result['title']}"):
                    st.write(f"**Document**: {result['document']}")
                    st.write(f"**Section**: {result['section']}")
                    st.write(f"**Content**: {result['content']}")
                    st.write(f"**Relevance Score**: {result['score']:.2f}")

def show_gap_analysis(gap_analyzer, doc_processor):
    st.header("Gap Analysis")
    
    st.subheader("Analyze Emerging Technology Gaps")
    
    # Input for research papers and incident reports
    research_text = st.text_area("Enter research paper abstracts or incident report summaries", 
                               height=200,
                               placeholder="Paste text from safety research or incident reports...")
    
    # Select technology domain
    tech_domain = st.selectbox("Select technology domain", 
                             ["IoT Devices", "AI Systems", "Autonomous Vehicles", 
                              "Smart Home Appliances", "Medical Devices", "Other"])
    
    if tech_domain == "Other":
        tech_domain = st.text_input("Specify the technology domain")
    
    if st.button("Analyze Gaps") and research_text:
        with st.spinner("Analyzing potential standard gaps..."):
            # Perform gap analysis
            gaps = gap_analyzer.identify_gaps(research_text, tech_domain, doc_processor)
            
            # Store results in session state
            st.session_state['gap_analysis'] = gaps
    
    # Display previous gap analysis results if available
    if 'gap_analysis' in st.session_state:
        st.subheader("Gap Analysis Results")
        
        gaps = st.session_state['gap_analysis']
        for i, gap in enumerate(gaps):
            with st.expander(f"Gap {i+1}: {gap['title']}"):
                st.write(f"**Description**: {gap['description']}")
                st.write(f"**Risk Level**: {gap['risk_level']}")
                st.write(f"**Technology Domain**: {gap['domain']}")
                st.write(f"**Related Standards**: {', '.join(gap['related_standards'])}")
                st.write(f"**Evidence**: {gap['evidence']}")
        
        # Visualization
        st.subheader("Gap Visualization")
        fig = create_gap_visualization(gaps)
        st.pyplot(fig)

def show_recommendations(recommendation_engine, gap_analyzer):
    st.header("Recommendations")
    
    if 'gap_analysis' not in st.session_state:
        st.warning("Please perform gap analysis first before generating recommendations.")
        return
    
    gaps = st.session_state['gap_analysis']
    
    # Select gap to address
    gap_titles = [f"Gap {i+1}: {gap['title']}" for i, gap in enumerate(gaps)]
    selected_gap_index = st.selectbox("Select gap to address", range(len(gap_titles)), format_func=lambda x: gap_titles[x])
    
    selected_gap = gaps[selected_gap_index]
    
    st.write("**Selected Gap:**")
    st.write(f"**Title**: {selected_gap['title']}")
    st.write(f"**Description**: {selected_gap['description']}")
    st.write(f"**Risk Level**: {selected_gap['risk_level']}")
    
    if st.button("Generate Recommendations"):
        with st.spinner("Generating recommendations..."):
            recommendations = recommendation_engine.generate_recommendations(selected_gap)
            st.session_state['recommendations'] = recommendations
    
    if 'recommendations' in st.session_state:
        st.subheader("Recommended Standard Updates")
        
        recommendations = st.session_state['recommendations']
        for i, rec in enumerate(recommendations):
            with st.expander(f"Recommendation {i+1}: {rec['title']}"):
                st.write(f"**Description**: {rec['description']}")
                st.write(f"**Proposed Text**: {rec['proposed_text']}")
                st.write(f"**Rationale**: {rec['rationale']}")
                st.write(f"**References**: {rec['references']}")
                st.write(f"**Implementation Difficulty**: {rec['implementation_difficulty']}")

def show_dashboard(doc_processor, gap_analyzer, recommendation_engine):
    st.header("Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Document Statistics")
        if hasattr(doc_processor, 'get_document_count'):
            st.metric("Total Documents", doc_processor.get_document_count())
            st.metric("Total Sections", doc_processor.get_section_count())
    
    with col2:
        st.subheader("Gap Analysis Summary")
        if 'gap_analysis' in st.session_state:
            gaps = st.session_state['gap_analysis']
            st.metric("Identified Gaps", len(gaps))
            
            # Count gaps by risk level
            high_risk = sum(1 for gap in gaps if gap['risk_level'] == 'High')
            medium_risk = sum(1 for gap in gaps if gap['risk_level'] == 'Medium')
            low_risk = sum(1 for gap in gaps if gap['risk_level'] == 'Low')
            
            st.metric("High Risk Gaps", high_risk)
            st.metric("Medium Risk Gaps", medium_risk)
            st.metric("Low Risk Gaps", low_risk)
    
    st.subheader("Standards Network")
    if hasattr(doc_processor, 'get_standards_network'):
        network_data = doc_processor.get_standards_network()
        fig = create_standards_network(network_data)
        st.pyplot(fig)
    else:
        st.info("Process documents to generate standards network visualization")
    
    st.subheader("Recent Activity")
    st.write("No recent activity to display")

if __name__ == "__main__":
    main()