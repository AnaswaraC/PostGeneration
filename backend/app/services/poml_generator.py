# app/services/poml_generator.py
import logging
import requests
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class POMLGenerator:
    """Generate professional poster.style.poml files using Groq AI"""
    
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.groq_model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        self.groq_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_complete_poml(self, user_content: str, image_count: int = 3) -> Dict[str, Any]:
        """Generate complete POML content with analysis and carousel support"""
        try:
            logger.info("🚀 Starting complete POML generation process")
            
            # Step 1: Content Analysis
            analysis_result = await self._analyze_content(user_content, image_count)
            if not analysis_result['success']:
                return analysis_result
            
            analysis = analysis_result['analysis']
            
            # Step 2: Generate Carousel Slides
            carousel_result = await self._generate_carousel_slides(user_content, image_count, analysis)
            if not carousel_result['success']:
                return carousel_result
            
            carousel_data = carousel_result['carousel_data']
            
            # Step 3: Generate Main POML
            poml_result = await self._generate_main_poml(user_content, analysis, carousel_data)
            
            return {
                "success": True,
                "analysis": analysis,
                "poml_content": poml_result['poml_content'],
                "carousel_data": carousel_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Complete POML generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_content(self, user_content: str, image_count: int) -> Dict[str, Any]:
        """Analyze content using Groq AI"""
        try:
            # Create a simpler, more reliable prompt
            prompt = f"""
            Analyze this .NET technical content and return JSON with:
            - content_type (announcement, tutorial, architecture, performance, release, roadmap)
            - primary_topics (array of main topics)
            - recommended_layout (split, vertical, hero, grid, timeline)
            - image_suggestions (array of image types like architecture_diagram, workflow, infographic)
            - key_points (array of 3-5 key points)
            - title_suggestion (professional title)
            - audience_level (beginner, intermediate, expert)
            - technologies (array of .NET technologies mentioned)

            Content: {user_content}

            Return ONLY valid JSON, no other text.
            """
            
            response = await self._call_groq_api(prompt)
            
            # Try to parse JSON with better error handling
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed. Response: {response}")
                # Create fallback analysis
                analysis = self._create_fallback_analysis(user_content)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Content analysis failed: {str(e)}")
            # Return fallback analysis
            return {
                "success": True,
                "analysis": self._create_fallback_analysis(user_content)
            }
    
    def _create_fallback_analysis(self, user_content: str) -> Dict[str, Any]:
        """Create fallback analysis when Groq fails"""
        content_lower = user_content.lower()
        
        # Simple keyword-based analysis
        if any(word in content_lower for word in ['performance', 'speed', 'optimization']):
            content_type = "performance"
        elif any(word in content_lower for word in ['tutorial', 'guide', 'how to']):
            content_type = "tutorial"
        elif any(word in content_lower for word in ['release', 'announce', 'available']):
            content_type = "release"
        elif any(word in content_lower for word in ['architecture', 'design', 'pattern']):
            content_type = "architecture"
        else:
            content_type = "technical"
        
        return {
            "content_type": content_type,
            "primary_topics": [".NET", "ASP.NET Core", "Performance"],
            "recommended_layout": "split",
            "image_suggestions": ["architecture_diagram", "workflow"],
            "key_points": ["Technical content analysis", "Key features", "Benefits"],
            "title_suggestion": "Microsoft .NET Technology Update",
            "audience_level": "intermediate",
            "technologies": [".NET", "C#", "ASP.NET Core"]
        }
    
    async def _generate_carousel_slides(self, user_content: str, image_count: int, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate carousel slides configuration"""
        try:
            # Create a simpler prompt for carousel generation
            prompt = f"""
            Create {image_count} carousel slides for this .NET content.
            For each slide, suggest the best image engine (dall-e for creative/realistic, mermaid for technical/diagrams).
            
            Return JSON with: carousel_id, total_slides, aspect_ratio, and slides array.
            Each slide should have: slide_number, title, content, image_type, image_prompt, layout, recommended_engine.
            
            Available engines: dall-e, mermaid
            
            Content Analysis: {json.dumps(analysis, indent=2)}
            User Content: {user_content}
            
            Return ONLY valid JSON.
            """
            
            response = await self._call_groq_api(prompt)
            
            try:
                carousel_data = json.loads(response)
                
                # Ensure each slide has an engine recommendation
                for slide in carousel_data.get('slides', []):
                    if 'recommended_engine' not in slide:
                        # Auto-detect based on image type
                        image_type = slide.get('image_type', '').lower()
                        if any(term in image_type for term in ['diagram', 'architecture', 'chart', 'flow', 'graph']):
                            slide['recommended_engine'] = 'mermaid'
                        else:
                            slide['recommended_engine'] = 'dall-e'
                            
            except json.JSONDecodeError:
                carousel_data = self._create_fallback_carousel(analysis, image_count)
            
            return {
                "success": True,
                "carousel_data": carousel_data
            }
            
        except Exception as e:
            logger.error(f"❌ Carousel generation failed: {str(e)}")
            return {
                "success": True,
                "carousel_data": self._create_fallback_carousel(analysis, image_count)
            }
    
    def _create_fallback_carousel(self, analysis: Dict[str, Any], image_count: int) -> Dict[str, Any]:
        """Create fallback carousel with engine variety"""
        image_types = analysis.get('image_suggestions', ['architecture_diagram', 'workflow', 'infographic'])
        
        slides = []
        for i in range(image_count):
            image_type = image_types[i % len(image_types)]
            
            # Determine engine based on image type
            if any(term in image_type.lower() for term in ['diagram', 'architecture', 'chart', 'flow']):
                recommended_engine = 'mermaid'
                image_prompt = f"Professional {image_type} for {analysis.get('title_suggestion', '.NET technology')}"
            else:
                recommended_engine = 'dall-e'
                image_prompt = f"High-quality {image_type} for {analysis.get('title_suggestion', '.NET technology')}, professional style"
            
            slides.append({
                "slide_number": i + 1,
                "title": f"Slide {i + 1} - {analysis.get('title_suggestion', '.NET Technology')}",
                "content": f"Key insights about {analysis.get('primary_topics', ['.NET'])[0]}",
                "image_type": image_type,
                "image_prompt": image_prompt,
                "layout": "split",
                "recommended_engine": recommended_engine
            })
        
        return {
            "carousel_id": f"carousel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_slides": image_count,
            "aspect_ratio": "1:1",
            "slides": slides
        }
    
    async def _generate_main_poml(self, user_content: str, analysis: Dict[str, Any], carousel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate main POML content"""
        try:
            # Create a comprehensive POML template
            title = analysis.get('title_suggestion', 'Microsoft .NET Technology')
            content_type = analysis.get('content_type', 'technical')
            
            poml_content = f"""# poster.style.poml - {title}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[metadata]
version = "1.0.0"
type = "technical_poster"
category = "{content_type}"
source_content = "{user_content[:100]}..."
carousel_id = "{carousel_data.get('carousel_id', 'default')}"
total_slides = {carousel_data.get('total_slides', 3)}

[layout]
type = "{analysis.get('recommended_layout', 'split')}"
width = 1200
height = 630
columns = 12
rows = 8

[style]
theme = "microsoft_light"
primary_color = "#0078d4"
secondary_color = "#005a9e"
accent_color = "#ffb900"
background_color = "#ffffff"
text_color = "#323130"
border_radius = 8

[typography]
title_font = "Segoe UI, sans-serif"
title_size = 48
title_weight = "bold"
body_font = "Segoe UI, sans-serif"
body_size = 18
body_weight = "normal"

[content]
title = "{title}"
key_points = \"\"\"{chr(10).join(['• ' + point for point in analysis.get('key_points', ['Technical content'])[:3]])}\"\"\"
audience = "{analysis.get('audience_level', 'intermediate')}"
technologies = "{', '.join(analysis.get('technologies', ['.NET', 'C#'])[:5])}"

[image]
type = "{analysis.get('image_suggestions', ['architecture_diagram'])[0]}"
generation_prompt = "Professional {analysis.get('image_suggestions', ['architecture_diagram'])[0]} for {title}"
recommended_engine = "{'mermaid' if 'diagram' in analysis.get('image_suggestions', [''])[0].lower() else 'dall-e'}"

[carousel]
enabled = true
slide_count = {carousel_data.get('total_slides', 3)}
aspect_ratio = "{carousel_data.get('aspect_ratio', '1:1')}"

[footer]
text_content = "Generated by DotNetPosterAI • {datetime.now().strftime('%Y-%m-%d')}"
show_branding = true

[generation]
engine = "groq_enhanced"
timestamp = "{datetime.now().isoformat()}"
"""
            
            return {
                "success": True,
                "poml_content": poml_content
            }
            
        except Exception as e:
            logger.error(f"❌ POML generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API with better error handling"""
        if not self.groq_api_key:
            logger.warning("⚠️ GROQ_API_KEY not configured, using fallback")
            return "{}"
        
        try:
            payload = {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.groq_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"❌ Groq API error: {response.status_code} - {response.text}")
                return "{}"  # Return empty JSON as fallback
                
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {str(e)}")
            return "{}"  # Return empty JSON as fallback