# app/services/enhanced_poster_generator.py
import logging
import os
import uuid
import aiofiles
import aiohttp # pyright: ignore[reportMissingImports]
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import base64
import requests
import re

from app.services.poml_generator import POMLGenerator
logger = logging.getLogger(__name__)

class EnhancedImageStorageManager:
    """Enhanced image storage with better format handling"""
    
    def __init__(self):
        self.base_dir = Path(os.getenv('IMAGE_STORAGE_PATH', './storage/images'))
        self.cache_dir = self.base_dir / 'cache'
        self.previews_dir = self.base_dir / 'previews'
        
        for directory in [self.base_dir, self.cache_dir, self.previews_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def download_and_store_image(self, image_url: str, image_id: str) -> Dict[str, Any]:
        """Download and store image with better error handling"""
        try:
            file_extension = self._get_file_extension_from_url(image_url)
            filename = f"{image_id}{file_extension}"
            
            cache_path = self.cache_dir / filename
            preview_path = self.previews_dir / f"preview_{filename}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Validate image data
                        if len(image_data) < 100:  # Too small to be a real image
                            raise Exception("Downloaded image data is too small")
                        
                        # Save files
                        async with aiofiles.open(cache_path, 'wb') as f:
                            await f.write(image_data)
                        async with aiofiles.open(preview_path, 'wb') as f:
                            await f.write(image_data)
                        
                        return {
                            "success": True,
                            "image_id": image_id,
                            "cache_path": str(cache_path),
                            "preview_path": str(preview_path),
                            "file_size": len(image_data),
                            "file_extension": file_extension,
                            "filename": filename
                        }
                    else:
                        raise Exception(f"HTTP {response.status}: Failed to download image")
                        
        except Exception as e:
            logger.error(f"❌ Image download failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_file_extension_from_url(self, url: str) -> str:
        """Extract file extension from URL more accurately"""
        # Check URL path for extension
        path = url.split('?')[0]  # Remove query parameters
        if '.' in path:
            ext = path.split('.')[-1].lower()
            if ext in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return f'.{ext}'
        
        # Default based on common patterns
        if 'png' in url.lower():
            return '.png'
        elif 'jpg' in url.lower() or 'jpeg' in url.lower():
            return '.jpg'
        elif 'webp' in url.lower():
            return '.webp'
        else:
            return '.png'

class EnhancedPosterGenerator:
    """Enhanced generator with better content and image handling"""
    
    def __init__(self, content_fetcher=None):
        self.content_fetcher = content_fetcher
        self.image_storage = EnhancedImageStorageManager()
        
        # API Configuration
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        self.headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_enhanced_post(self, topic: str = None, image_count: int = 3) -> Dict[str, Any]:
        """Generate enhanced post with proper content and images"""
        try:
            logger.info("🚀 Starting enhanced post generation")
            
            # Step 1: Generate comprehensive content
            content_data = await self._generate_comprehensive_content(topic)
            if not content_data['success']:
                return content_data
            
            # Step 2: Create detailed structure
            structure_result = await self._create_detailed_structure(
                content_data['content'], 
                image_count
            )
            if not structure_result['success']:
                return structure_result
            
            # Step 3: Generate high-quality images
            carousel_data = structure_result['carousel_data']
            enhanced_slides = await self._generate_enhanced_images(carousel_data['slides'])
            
            # Step 4: Process and store images
            carousel_data['slides'] = await self._process_enhanced_slides(enhanced_slides)
            
            # Step 5: Format response
            return self._format_enhanced_response(
                structure_result['poml_content'],
                structure_result['captions'],
                carousel_data,
                structure_result['analysis'],
                content_data
            )
            
        except Exception as e:
            logger.error(f"❌ Enhanced post generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _generate_comprehensive_content(self, topic: str) -> Dict[str, Any]:
        """Generate comprehensive and detailed content"""
        try:
            prompt = f"""
            Create a comprehensive, detailed technical article about {topic or 'latest .NET technologies'}.
            
            Requirements:
            - Minimum 500 words
            - Include specific technical details, code examples, and best practices
            - Cover architecture, implementation, and real-world use cases
            - Focus on Microsoft .NET ecosystem
            - Include recent updates and features
            
            Structure:
            1. Introduction and overview
            2. Key features and capabilities
            3. Technical implementation details
            4. Code examples and snippets
            5. Best practices and patterns
            6. Performance considerations
            7. Integration with other technologies
            8. Future developments
            
            Make it professionally written and technically accurate.
            """
            
            content = await self._call_groq_api(prompt)
            
            return {
                "success": True,
                "content": content,
                "source": "ai_generated",
                "topic": topic,
                "word_count": len(content.split()),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_detailed_structure(self, content: str, image_count: int) -> Dict[str, Any]:
        """Create detailed structure with proper image assignments"""
        try:
            analysis_prompt = f"""
            Analyze this technical content and create a detailed structure for {image_count} visual slides.
            
            Content: {content[:2000]}...
            
            Return JSON with:
            - content_analysis (detailed breakdown)
            - key_sections (array of main sections)
            - visual_elements (array of visual concepts)
            - slide_details (array of {image_count} slides with: title, detailed_content, image_type, image_description, recommended_engine)
            - social_captions (linkedin, twitter, instagram)
            
            For image types, use: architecture_diagram, code_visualization, workflow, infographic, performance_chart, system_design
            For engines, recommend: dall-e for creative/realistic, mermaid for technical/diagrams
            
            Return valid JSON only.
            """
            
            response = await self._call_groq_api(analysis_prompt)
            
            try:
                analysis_data = json.loads(response)
            except json.JSONDecodeError:
                analysis_data = self._create_enhanced_fallback(content, image_count)
            
            # Generate POML content
            poml_content = self._generate_enhanced_poml(content, analysis_data)
            
            # Create carousel data
            carousel_data = {
                "carousel_id": f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "total_slides": image_count,
                "aspect_ratio": "16:9",
                "slides": analysis_data.get('slide_details', [])
            }
            
            return {
                "success": True,
                "analysis": analysis_data,
                "poml_content": poml_content,
                "captions": analysis_data.get('social_captions', {}),
                "carousel_data": carousel_data
            }
            
        except Exception as e:
            logger.error(f"❌ Structure creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_enhanced_fallback(self, content: str, image_count: int) -> Dict[str, Any]:
        """Enhanced fallback structure"""
        slides = []
        topics = [".NET Architecture", "Performance Optimization", "Code Implementation", "Best Practices", "System Design"]
        
        for i in range(image_count):
            topic = topics[i % len(topics)]
            is_diagram = i % 2 == 0  # Alternate between diagram and creative
            
            slides.append({
                "slide_number": i + 1,
                "title": f"{topic} - Detailed Overview",
                "detailed_content": f"Comprehensive analysis of {topic} in .NET ecosystem with implementation details and best practices.",
                "image_type": "architecture_diagram" if is_diagram else "infographic",
                "image_description": f"Professional {'technical diagram' if is_diagram else 'visualization'} showing {topic.lower()} concepts with .NET framework elements",
                "recommended_engine": "mermaid" if is_diagram else "dall-e"
            })
        
        return {
            "content_analysis": "Comprehensive .NET technical content analysis",
            "key_sections": [".NET Fundamentals", "Advanced Features", "Implementation", "Best Practices"],
            "visual_elements": ["Architecture diagrams", "Code visualizations", "Performance metrics", "Workflow charts"],
            "slide_details": slides,
            "social_captions": {
                "linkedin": f"Exploring {image_count} key aspects of .NET technology. Comprehensive analysis and visual explanations. #DotNet #Microsoft #Programming",
                "twitter": f"Deep dive into .NET technologies! {image_count} visual explanations. #DotNet #CSharp #Tech",
                "instagram": f"Visual journey through .NET technology 🚀 {image_count} detailed slides #DotNet #Microsoft #Code"
            }
        }
    
    def _generate_enhanced_poml(self, content: str, analysis: Dict[str, Any]) -> str:
        """Generate enhanced POML content"""
        title = analysis.get('slide_details', [{}])[0].get('title', 'Enhanced .NET Technology')
        
        return f"""# poster.style.poml - {title}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[metadata]
version = "2.0.0"
type = "enhanced_technical_poster"
category = "detailed_analysis"
source = "EnhancedDotNetAI"
content_quality = "comprehensive"

[layout]
type = "adaptive"
width = 1200
height = 800
columns = 16
rows = 12
responsive = true

[style]
theme = "microsoft_enhanced"
primary_color = "#0078d4"
secondary_color = "#005a9e"
accent_color = "#107c10"
background_gradient = "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)"
text_color = "#323130"
shadow_intensity = 0.1

[typography]
title_font = "Segoe UI, system-ui, sans-serif"
title_size = 52
title_weight = 700
body_font = "Segoe UI, system-ui, sans-serif"
body_size = 20
body_weight = 400
code_font = "Cascadia Code, Consolas, monospace"

[content]
title = "{title}"
summary = "Comprehensive technical analysis with detailed visual explanations"
key_points = {json.dumps(analysis.get('key_sections', []))}
audience_level = "intermediate_to_advanced"
technical_depth = "detailed"

[generation]
engine = "enhanced_poster_generator"
timestamp = "{datetime.now().isoformat()}"
content_quality = "high"
image_count = {len(analysis.get('slide_details', []))}
"""

    async def _generate_enhanced_images(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate enhanced images with proper error handling"""
        processed_slides = []
        
        for slide in slides:
            try:
                image_desc = slide.get('image_description', '')
                image_type = slide.get('image_type', 'architecture_diagram')
                engine = slide.get('recommended_engine', 'dall-e')
                
                if engine == 'dall-e':
                    image_result = await self._generate_enhanced_dall_e(image_desc, image_type)
                elif engine == 'mermaid':
                    image_result = await self._generate_enhanced_mermaid(image_desc, image_type)
                else:
                    image_result = await self._generate_enhanced_dall_e(image_desc, image_type)
                
                processed_slides.append({
                    **slide,
                    "engine_used": engine,
                    "image_generation": image_result,
                    "generation_status": "success"
                })
                
                logger.info(f"✅ Generated {engine} image for: {slide['title']}")
                
            except Exception as e:
                logger.error(f"❌ Image generation failed for slide {slide.get('slide_number')}: {str(e)}")
                processed_slides.append({
                    **slide,
                    "engine_used": "failed",
                    "image_generation": {"success": False, "error": str(e)},
                    "generation_status": "failed"
                })
        
        return processed_slides
    
    async def _generate_enhanced_dall_e(self, description: str, image_type: str) -> Dict[str, Any]:
        """Generate enhanced DALL-E images"""
        try:
            if not self.openai_api_key:
                raise Exception("OpenAI API key not configured")
            
            enhanced_prompt = await self._enhance_dall_e_prompt(description, image_type)
            
            url = "https://api.openai.com/v1/images/generations"
            headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
            
            payload = {
                "model": "dall-e-3",
                "prompt": enhanced_prompt,
                "size": "1024x1024",
                "quality": "standard",
                "style": "vivid",
                "n": 1
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "engine": "dall-e-3",
                    "image_url": result['data'][0]['url'],
                    "prompt_used": enhanced_prompt,
                    "size": "1024x1024"
                }
            else:
                raise Exception(f"DALL-E API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ DALL-E generation failed: {str(e)}")
            raise e
    
    async def _generate_enhanced_mermaid(self, description: str, image_type: str) -> Dict[str, Any]:
        """Generate enhanced Mermaid diagrams"""
        try:
            mermaid_code = await self._create_detailed_mermaid(description, image_type)
            image_url = await self._render_mermaid(mermaid_code)
            
            return {
                "success": True,
                "engine": "mermaid",
                "image_url": image_url,
                "mermaid_code": mermaid_code,
                "description": description
            }
            
        except Exception as e:
            logger.error(f"❌ Mermaid generation failed: {str(e)}")
            raise e
    
    async def _enhance_dall_e_prompt(self, description: str, image_type: str) -> str:
        """Create enhanced DALL-E prompts"""
        prompt_templates = {
            "architecture_diagram": "Professional software architecture diagram: {description}. Clean modern design, blue color scheme, abstract technology concepts, no text",
            "infographic": "Technology infographic: {description}. Modern design, data visualization, professional style, vibrant colors",
            "workflow": "Software workflow visualization: {description}. Process flow, modern UI elements, clear progression",
            "performance_chart": "Performance metrics visualization: {description}. Charts, graphs, modern analytics style",
            "system_design": "System design diagram: {description}. Components, connections, modern architecture style"
        }
        
        template = prompt_templates.get(image_type, "Professional technology concept: {description}. Modern digital art")
        return template.format(description=description)
    
    async def _create_detailed_mermaid(self, description: str, image_type: str) -> str:
        """Create detailed Mermaid diagrams"""
        base_diagrams = {
            "architecture_diagram": """graph TB
    A[Client Layer] --> B[API Gateway]
    B --> C[Microservice 1]
    B --> D[Microservice 2]
    B --> E[Microservice 3]
    
    C --> F[Database 1]
    D --> G[Database 2]
    E --> H[Cache Layer]
    
    H --> I[Redis Cluster]
    F --> J[SQL Database]
    G --> K[NoSQL Database]
    
    style A fill:#0078d4,color:#fff
    style B fill:#107c10,color:#fff
    style C fill:#d83b01,color:#fff
    style D fill:#d83b01,color:#fff
    style E fill:#d83b01,color:#fff
    style F fill:#005a9e,color:#fff
    style G fill:#005a9e,color:#fff
    style H fill:#ffb900,color:#000
    style I fill:#e81123,color:#fff
    style J fill:#737373,color:#fff
    style K fill:#737373,color:#fff""",
            
            "workflow": """flowchart TD
    A[Start Request] --> B[Authentication]
    B --> C{Valid?}
    C -->|Yes| D[Process Request]
    C -->|No| E[Return Error]
    
    D --> F[Business Logic]
    F --> G[Data Access]
    G --> H[Database]
    H --> I[Format Response]
    I --> J[Return Success]
    
    style A fill:#0078d4,color:#fff
    style B fill:#107c10,color:#fff
    style D fill:#d83b01,color:#fff
    style F fill:#ffb900,color:#000
    style J fill:#107c10,color:#fff
    style E fill:#e81123,color:#fff"""
        }
        
        return base_diagrams.get(image_type, base_diagrams["architecture_diagram"])
    
    async def _render_mermaid(self, mermaid_code: str) -> str:
        """Render Mermaid code to image"""
        try:
            clean_code = " ".join(mermaid_code.split())
            encoded_code = base64.b64encode(clean_code.encode()).decode()
            image_url = f"https://mermaid.ink/img/{encoded_code}?bgColor=ffffff"
            
            # Verify URL
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                return image_url
            else:
                raise Exception(f"Mermaid rendering failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Mermaid rendering failed: {str(e)}")
            return "https://via.placeholder.com/1024x1024/0078D4/FFFFFF?text=Mermaid+Diagram"
    
    async def _process_enhanced_slides(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and store enhanced slides"""
        processed_slides = []
        
        for slide in slides:
            image_gen = slide.get('image_generation', {})
            
            if image_gen.get('success') and image_gen.get('image_url'):
                image_id = f"enhanced_{slide['slide_number']}_{uuid.uuid4().hex[:8]}"
                
                download_result = await self.image_storage.download_and_store_image(
                    image_gen['image_url'],
                    image_id
                )
                
                if download_result['success']:
                    slide['local_images'] = {
                        "image_id": image_id,
                        "preview_url": f"/api/poster/preview/{image_id}",
                        "download_url": f"/api/poster/download/{image_id}",
                        **download_result
                    }
                    
                    # Generate base64 preview
                    preview_base64 = await self._generate_base64_preview(download_result['cache_path'])
                    slide['preview_data'] = {
                        "base64": preview_base64,
                        "type": f"image/{download_result['file_extension'].replace('.', '')}",
                        "dimensions": "1024x1024"
                    }
            
            processed_slides.append(slide)
        
        return processed_slides
    
    async def _generate_base64_preview(self, image_path: str) -> str:
        """Generate base64 preview"""
        try:
            async with aiofiles.open(image_path, 'rb') as f:
                image_data = await f.read()
                return f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"
        except Exception as e:
            logger.error(f"❌ Base64 preview failed: {str(e)}")
            return ""
    
    async def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API with enhanced error handling"""
        if not self.groq_api_key:
            raise Exception("Groq API key not configured")
        
        try:
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                raise Exception(f"Groq API error {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {str(e)}")
            raise e
    
    def _format_enhanced_response(self, poml_content: str, captions: Dict[str, Any], 
                                carousel_data: Dict[str, Any], analysis: Dict[str, Any],
                                content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format enhanced response"""
        successful_slides = [s for s in carousel_data['slides'] if s.get('generation_status') == 'success']
        
        return {
            "success": True,
            "summary": {
                "total_slides": len(carousel_data['slides']),
                "successful_images": len(successful_slides),
                "content_quality": "enhanced",
                "generation_time": datetime.now().isoformat()
            },
            "content_info": content_data,
            "analysis": analysis,
            "captions": captions,
            "poml_content": poml_content,
            "carousel_data": carousel_data,
            "previews": [s.get('preview_data', {}) for s in carousel_data['slides'] if s.get('preview_data')]
        }

# FastAPI integration
async def create_enhanced_generator():
    """Create enhanced poster generator"""
    from app.services.content_fetcher import EnhancedDotNetFetcher
    content_fetcher = EnhancedDotNetFetcher()
    return EnhancedPosterGenerator(content_fetcher)