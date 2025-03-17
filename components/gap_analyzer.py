# safety_standards_analyzer/components/gap_analyzer.py

import os
from typing import List, Dict, Any
from openai import OpenAI

class GapAnalyzer:
    """
    Analyzes research papers and incident reports to identify potential gaps
    in safety standards coverage.
    """
    
    def __init__(self):
        """Initialize the gap analyzer with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def identify_gaps(self, research_text: str, domain: str, doc_processor) -> List[Dict[str, Any]]:
        """
        Identify potential gaps in safety standards based on research texts.
        
        Args:
            research_text: Text from research papers or incident reports
            domain: Technology domain to focus on
            doc_processor: DocumentProcessor instance for searching standards
            
        Returns:
            List of identified gaps with metadata
        """
        # First, search for related standards in our database
        related_standards_results = doc_processor.search_standards(
            f"safety standards for {domain}", top_k=5
        )
        
        # Extract relevant information from search results
        related_standards = []
        related_standards_content = ""
        
        for result in related_standards_results:
            standard_info = f"{result['document']} - {result['section']}"
            related_standards.append(standard_info)
            related_standards_content += f"\n\nStandard: {standard_info}\nContent: {result['content']}"
        
        # Prompt the LLM to identify gaps
        prompt = f"""
        You are an expert in safety standards analysis. Your task is to identify potential gaps in 
        safety standards coverage for emerging technologies based on research papers and incident reports.

        TECHNOLOGY DOMAIN: {domain}

        RESEARCH TEXT:
        {research_text[:3000]}  # Limit text length

        EXISTING RELATED STANDARDS:
        {related_standards_content[:2000] if related_standards_content else "No directly related standards found."}

        Please identify 3-5 potential gaps in safety standards coverage based on the research text
        and existing standards. For each gap, provide:
        1. A clear title
        2. A detailed description
        3. Risk level (High, Medium, or Low)
        4. Related standards that partially address this gap, if any
        5. Evidence from the research text that suggests this gap exists

        Format your response as a JSON object with a "gaps" key containing an array of gap objects.
        """

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a safety standards expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        try:
            gaps = eval(response.choices[0].message.content)["gaps"]
            
            # Ensure consistent structure and add domain to each gap
            for gap in gaps:
                gap["domain"] = domain
                gap["related_standards"] = gap.get("related_standards", [])
                if isinstance(gap["related_standards"], str):
                    gap["related_standards"] = [gap["related_standards"]]
                
                # Ensure risk level is standardized
                if "risk_level" not in gap or gap["risk_level"] not in ["High", "Medium", "Low"]:
                    gap["risk_level"] = "Medium"
            
            return gaps
        except:
            # Return a default structure if response parsing fails
            return [{
                "title": f"Potential {domain} Safety Gap",
                "description": "The analysis identified a potential gap but couldn't structure the response.",
                "risk_level": "Medium",
                "domain": domain,
                "related_standards": related_standards,
                "evidence": "Based on provided research text."
            }]