# safety_standards_analyzer/components/document_processor.py

import os
import PyPDF2
import docx
import uuid
import json
import numpy as np
from typing import List, Dict, Any, BinaryIO
from openai import OpenAI
import pandas as pd

class DocumentProcessor:
    """
    Processes standards documents, extracts content, creates embeddings,
    and provides search capabilities.
    """
    
    def __init__(self):
        """Initialize the document processor with OpenAI client and storage."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.documents = []
        self.sections = []
        self.embeddings = []  # Initialize as a list, not a NumPy array
        self.document_db_path = "data/documents.json"
        self.sections_db_path = "data/sections.json"
        self.embeddings_db_path = "data/embeddings.npy"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing document data from files."""
        try:
            if os.path.exists(self.document_db_path):
                with open(self.document_db_path, 'r') as f:
                    self.documents = json.load(f)
            
            if os.path.exists(self.sections_db_path):
                with open(self.sections_db_path, 'r') as f:
                    self.sections = json.load(f)
            
            if os.path.exists(self.embeddings_db_path):
                # Convert NumPy array to list when loading
                embeddings_array = np.load(self.embeddings_db_path)
                self.embeddings = embeddings_array.tolist()
        except Exception as e:
            print(f"Error loading data: {e}")
            # Ensure embeddings is always a list
            self.embeddings = []
    
    def _save_data(self):
        """Save document data to files."""
        try:
            with open(self.document_db_path, 'w') as f:
                json.dump(self.documents, f)
            
            with open(self.sections_db_path, 'w') as f:
                json.dump(self.sections, f)
            
            if len(self.embeddings) > 0:
                # Convert list to NumPy array when saving
                embeddings_array = np.array(self.embeddings)
                np.save(self.embeddings_db_path, embeddings_array)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def process_document(self, file: BinaryIO) -> None:
        """
        Process a document file, extract text, split into sections,
        and create embeddings.
        
        Args:
            file: File object to process
        """
        # Extract text based on file type
        file_content = file.read()
        file_name = file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if file_extension == '.pdf':
            text = self._extract_text_from_pdf(file_content)
        elif file_extension == '.docx':
            text = self._extract_text_from_docx(file_content)
        elif file_extension == '.txt':
            text = file_content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Create document record
        doc_id = str(uuid.uuid4())
        document = {
            'id': doc_id,
            'filename': file_name,
            'type': file_extension[1:],  # Remove the dot
            'size': len(file_content),
            'processed_date': pd.Timestamp.now().isoformat()
        }
        self.documents.append(document)
        
        # Split into sections
        sections = self._split_into_sections(text, doc_id)
        
        # Process each section
        for section in sections:
            # Create embedding for section
            embedding = self._create_embedding(section['content'])
            
            # Add section to database
            self.sections.append(section)
            self.embeddings.append(embedding)  # This will work now because embeddings is a list
        
        # Save updated data
        self._save_data()
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content."""
        from io import BytesIO
        
        text = ""
        with BytesIO(content) as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        return text
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        from io import BytesIO
        
        text = ""
        with BytesIO(content) as file:
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        return text
    
    
    def _split_into_sections(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """
        Split document text into sections using a combination of rule-based
        approach and AI assistance.
        """
        # Simple split by double newlines for sections (in a real app, this would be more sophisticated)
        sections_text = text.split("\n\n")
        
        # Use OpenAI to identify proper section titles and organize content
        prompt = f"""
        I have a safety standards document that I need to split into proper sections. 
        Here's the raw text split by paragraph breaks:
        
        {sections_text[:10]}  # Just sending first 10 paragraphs for brevity
        
        Please identify the main sections and their titles. Return as a JSON list where each 
        item has 'title' and 'content' keys. Merge paragraphs that belong to the same section.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes safety standards documents."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        try:
            parsed_sections = json.loads(response.choices[0].message.content)['sections']
        except (json.JSONDecodeError, KeyError):
            # Fallback to simple section splitting if AI processing fails
            parsed_sections = [{"title": f"Section {i+1}", "content": s} 
                              for i, s in enumerate(sections_text) if s.strip()]
        
        # Format sections with metadata
        result = []
        for i, section in enumerate(parsed_sections):
            section_id = str(uuid.uuid4())
            result.append({
                'id': section_id,
                'document_id': doc_id,
                'index': i,
                'title': section.get('title', f"Section {i+1}"),
                'content': section.get('content', '').strip(),
                'word_count': len(section.get('content', '').split())
            })
        
        return result
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create an embedding vector for the provided text."""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text[:8000]  # Limit to first 8000 chars due to token limits
        )
        return response.data[0].embedding
    
    def search_standards(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for standards sections relevant to the query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant sections with metadata
        """
        # Create embedding for query
        query_embedding = self._create_embedding(query)
        
        # If no embeddings exist yet, return empty list
        if len(self.embeddings) == 0:
            return []
        
        # Convert list to numpy array for efficient computation
        embeddings_array = np.array(self.embeddings)
        
        # Calculate cosine similarity
        similarities = np.dot(embeddings_array, query_embedding) / (
            np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get indices of top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Collect results
        results = []
        for idx in top_indices:
            section = self.sections[idx]
            document = next((d for d in self.documents if d['id'] == section['document_id']), {})
            
            results.append({
                'id': section['id'],
                'document': document.get('filename', 'Unknown'),
                'section': section['title'],
                'content': section['content'][:300] + '...' if len(section['content']) > 300 else section['content'],
                'score': float(similarities[idx]),
                'title': section['title']
            })
        
        return results
    
    def get_document_count(self) -> int:
        """Get the number of processed documents."""
        return len(self.documents)
    
    def get_section_count(self) -> int:
        """Get the number of sections across all documents."""
        return len(self.sections)
    
    def get_standards_network(self) -> Dict[str, Any]:
        """
        Create a network representation of standards relationships.
        This creates connections between standards based on semantic similarity.
        
        Returns:
            Dict with nodes and edges for network visualization
        """
        if len(self.sections) < 2:
            return {"nodes": [], "edges": []}
        
        # Create nodes for each document
        nodes = [{"id": doc["id"], "label": os.path.basename(doc["filename"]), "size": 10} 
                for doc in self.documents]
        
        # Create edges between documents based on section similarity
        edges = []
        doc_ids = [doc["id"] for doc in self.documents]
        
        # Calculate document-level embeddings by averaging section embeddings
        doc_embeddings = {}
        for doc_id in doc_ids:
            doc_sections = [i for i, s in enumerate(self.sections) if s["document_id"] == doc_id]
            if doc_sections:
                doc_embedding = np.mean([self.embeddings[i] for i in doc_sections], axis=0)
                doc_embeddings[doc_id] = doc_embedding
        
        # Create edges between similar documents
        for i, doc1_id in enumerate(doc_ids):
            if doc1_id not in doc_embeddings:
                continue
                
            for j, doc2_id in enumerate(doc_ids[i+1:], i+1):
                if doc2_id not in doc_embeddings:
                    continue
                    
                # Calculate similarity
                similarity = np.dot(doc_embeddings[doc1_id], doc_embeddings[doc2_id]) / (
                    np.linalg.norm(doc_embeddings[doc1_id]) * np.linalg.norm(doc_embeddings[doc2_id])
                )
                
                # Add edge if similarity is above threshold
                if similarity > 0.8:  # Arbitrary threshold
                    edges.append({
                        "source": doc1_id,
                        "target": doc2_id,
                        "weight": float(similarity)
                    })
        
        return {"nodes": nodes, "edges": edges}