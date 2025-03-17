# AI-Powered Safety Standards Analyzer

## Overview

The AI-Powered Safety Standards Analyzer is a tool designed to help standards organizations, manufacturers, and safety professionals identify gaps in existing safety standards, particularly for emerging technologies. Using OpenAI's API, this application analyzes safety standards documents and compares them against research papers and incident reports to identify potential areas where standards need to be updated or expanded.

## Features

- **Document Processing**: Upload and analyze safety standards documents in PDF, DOCX, or TXT formats
- **Semantic Search**: Search through standards documents using natural language queries
- **Gap Analysis**: Identify potential gaps in standards coverage based on research papers and incident reports
- **Recommendation Engine**: Generate specific recommendations for standards updates
- **Interactive Dashboard**: Visualize standards coverage and identified gaps

## Use Cases

- Standards development organizations looking to identify areas for new or updated standards
- Manufacturers seeking to ensure their products meet comprehensive safety requirements
- Safety researchers wanting to translate research findings into standards recommendations
- Regulatory bodies evaluating the completeness of existing safety standards

## Technical Architecture

The application consists of four main components:

1. **Document Processor**: Handles the ingestion and analysis of standards documents
2. **Gap Analyzer**: Identifies potential gaps in standards coverage
3. **Recommendation Engine**: Generates specific recommendations for standards updates
4. **Visualization Module**: Creates visual representations of standards coverage and gaps

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Approximately 1GB of disk space for dependencies and data

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/safety-standards-analyzer.git
   cd safety-standards-analyzer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Project Structure

```
safety-standards-analyzer/
├── data/                    # Storage for processed documents and embeddings
├── components/              # Core application components
│   ├── __init__.py
│   ├── document_processor.py # Document processing and embedding
│   ├── gap_analyzer.py      # Gap analysis using OpenAI
│   ├── recommendation_engine.py # Recommendation generation
│   └── visualization.py     # Data visualization utilities
├── main.py                  # Main application entry point
├── requirements.txt         # Project dependencies
├── .env                     # Environment variables (not tracked in git)
└── README.md                # Project documentation
```

## Usage

1. Start the application:
   ```bash
   streamlit run main.py
   ```

2. Upload standards documents in the "Document Processing" tab.

3. Use the "Gap Analysis" tab to analyze research papers and identify potential gaps.

4. Generate recommendations in the "Recommendations" tab.

5. View summary statistics and visualizations in the "Dashboard" tab.

## Example Workflow

1. **Document Processing**:
   - Upload a safety standard document for IoT devices
   - The system will process the document, extract sections, and create embeddings

2. **Gap Analysis**:
   - Paste a research paper on emerging IoT security vulnerabilities
   - Select "IoT Devices" as the technology domain
   - The system will identify gaps in the standard's coverage of these vulnerabilities

3. **Recommendations**:
   - Select a specific gap from the analysis
   - Generate recommendations for updating the standard to address this gap

4. **Dashboard**:
   - View a summary of processed documents and identified gaps
   - Explore visualizations of standards coverage and relationships

## Sample Data

The repository includes sample data to demonstrate the application:

- `sample_standards/iot_security_standard.txt`: A sample IoT security standard
- `sample_research/iot_security_research.txt`: A sample research paper on IoT security vulnerabilities

## API Usage

This application uses the OpenAI API for several key functions:

- Creating embeddings for document sections
- Analyzing research papers to identify gaps
- Generating recommendations for standards updates

Be aware of OpenAI API usage costs when using this application extensively.

## Technical Details

### Document Processing

Documents are processed in the following steps:
1. Text extraction based on file type (PDF, DOCX, TXT)
2. Section identification and extraction
3. Embedding creation using OpenAI's embedding model
4. Storage of documents, sections, and embeddings

### Gap Analysis

Gap analysis uses the following approach:
1. Search for relevant standards sections
2. Compare research text against these sections
3. Identify potential gaps using GPT-4
4. Categorize gaps by risk level and domain

### Recommendation Engine

Recommendations are generated using the following process:
1. Analyze a specific gap
2. Generate specific recommendations to address the gap
3. Provide proposed text for standard updates
4. Include rationale and implementation difficulty

## Limitations

- The application can only analyze text content, not images or charts
- Analysis quality depends on the OpenAI API's capabilities
- Large documents may take significant time to process
- The semantic search has limitations in highly technical domains

## Future Enhancements

- Support for more document formats (HTML, XML, etc.)
- Improved section extraction for complex document structures
- Collaborative annotation features for identified gaps
- Integration with standards development workflows
- Automated tracking of standards updates over time

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the API that powers the analysis
- The open-source community for libraries used in this project
- Streamlit for the interactive web application framework

## Contact

For questions or support, please contact [aashikmathewss@gmail.com](mailto:aashikmathewss@gmail.com)