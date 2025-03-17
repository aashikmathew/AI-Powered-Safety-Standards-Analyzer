# safety_standards_analyzer/components/recommendation_engine.py

import os
from typing import List, Dict, Any
from openai import OpenAI

class RecommendationEngine:
    """
    Generates recommendations for standards updates based on identified gaps.
    """
    
    def __init__(self):
        """Initialize the recommendation engine with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_recommendations(self, gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations for standards updates based on an identified gap.
        
        Args:
            gap: The gap dictionary with metadata
            
        Returns:
            List of recommendations with metadata
        """
        prompt = f"""
        You are an expert in safety standards development. You need to generate specific recommendations 
        to address the following gap in safety standards:
        
        GAP TITLE: {gap['title']}
        
        GAP DESCRIPTION: {gap['description']}
        
        TECHNOLOGY DOMAIN: {gap['domain']}
        
        RISK LEVEL: {gap['risk_level']}
        
        RELATED STANDARDS: {', '.join(gap['related_standards']) if gap['related_standards'] else 'None identified'}
        
        EVIDENCE: {gap['evidence']}
        
        Please provide 2-3 specific recommendations to address this gap. For each recommendation, include:
        1. A concise title
        2. A detailed description of the recommendation
        3. Proposed text for a new standard or standard update
        4. Rationale explaining why this recommendation addresses the gap
        5. References to relevant research or industry best practices
        6. Implementation difficulty (Easy, Moderate, or Difficult)
        
        Format your response as a JSON object with a "recommendations" key containing an array of 
        recommendation objects.
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
            recommendations = eval(response.choices[0].message.content)["recommendations"]
            
            # Ensure consistent structure
            for rec in recommendations:
                # Ensure implementation difficulty is standardized
                if "implementation_difficulty" not in rec or rec["implementation_difficulty"] not in ["Easy", "Moderate", "Difficult"]:
                    rec["implementation_difficulty"] = "Moderate"
                
                # Ensure all required fields exist
                for field in ["title", "description", "proposed_text", "rationale", "references"]:
                    if field not in rec:
                        rec[field] = f"No {field} provided"
            
            return recommendations
        except:
            # Return a default structure if response parsing fails
            return [{
                "title": f"Address {gap['title']}",
                "description": f"Create or update standards to address the identified gap in {gap['domain']} safety.",
                "proposed_text": "Standards organizations should develop comprehensive requirements for...",
                "rationale": "This recommendation directly addresses the identified gap by providing clear guidance.",
                "references": "Based on industry best practices and research evidence.",
                "implementation_difficulty": "Moderate"
            }]