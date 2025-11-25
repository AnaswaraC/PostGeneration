# app/services/groq_image_generator.py
import logging
import requests
import os
import json
import base64
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GroqImageGenerator:
    """Generate images using Stable Diffusion, Mermaid, and Groq AI enhancement"""
    
    def __init__(self):
        # Groq Configuration
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.groq_model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        self.groq_url = "https://api.groq.com/openai/v1"
        
        # Stable Diffusion Configuration
        self.sd_api_url = os.getenv('STABLE_DIFFUSION_API_URL')
        self.sd_api_key = os.getenv('STABLE_DIFFUSION_API_KEY')
        self.sd_engine_id = os.getenv('STABLE_DIFFUSION_ENGINE_ID', 'stable-diffusion-v1-6')
        
        self.headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        self._log_configuration()
    
    def _log_configuration(self):
        """Log the current configuration status"""
        logger.info("🖼️ Image Generator Configuration:")
        logger.info(f"   Stable Diffusion: {'✅ Configured' if self.sd_api_key else '❌ Missing API Key'}")
        logger.info(f"   Groq AI: {'✅ Configured' if self.groq_api_key else '❌ Missing API Key'}")
        logger.info(f"   Mermaid: {'✅ Enabled' if os.getenv('ENABLE_MERMAID', 'true').lower() == 'true' else '❌ Disabled'}")
    
    async def generate_image(self, prompt: str, image_type: str, engine: str = None) -> Dict[str, Any]:
        """Generate image with intelligent engine selection and fallbacks"""
        if not engine:
            engine = os.getenv('DEFAULT_IMAGE_ENGINE', 'stable-diffusion')
        
        logger.info(f"🚀 Generating {engine} image for: {image_type}")
        
        try:
            if engine == 'stable-diffusion':
                return await self._generate_stable_diffusion_image(prompt, image_type)
            elif engine == 'mermaid':
                return await self._generate_mermaid_diagram(prompt, image_type)
            else:
                return await self._generate_placeholder_image(prompt, image_type)
                
        except Exception as e:
            logger.error(f"❌ {engine} image generation failed: {str(e)}")
            # Smart fallback based on image type
            if any(term in image_type.lower() for term in ['diagram', 'architecture', 'chart', 'flow']):
                logger.info("🔄 Falling back to Mermaid for technical content")
                return await self._generate_mermaid_diagram(prompt, image_type)
            else:
                logger.info("🔄 Falling back to placeholder")
                return await self._generate_placeholder_image(prompt, image_type)
    
    async def _generate_stable_diffusion_image(self, prompt: str, image_type: str) -> Dict[str, Any]:
        """Generate high-quality image using Stable Diffusion"""
        try:
            if not self.sd_api_key:
                error_msg = "Stable Diffusion API key not configured. Please set STABLE_DIFFUSION_API_KEY in your environment variables."
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            logger.info(f"🎨 Generating Stable Diffusion image: {prompt[:80]}...")
            
            # Enhanced prompt engineering for Stable Diffusion
            enhanced_prompt = await self._create_enhanced_sd_prompt(prompt, image_type)
            
            # Stable Diffusion API call
            headers = {
                "Authorization": f"Bearer {self.sd_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "text_prompts": [
                    {
                        "text": enhanced_prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,
                "clip_guidance_preset": "FAST_BLUE",
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
                "style_preset": "digital-art"  # Better for technical content
            }
            
            logger.debug(f"Stable Diffusion Payload: {payload}")
            
            response = requests.post(self.sd_api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract base64 image data
                if result.get('artifacts') and len(result['artifacts']) > 0:
                    base64_image = result['artifacts'][0]['base64']
                    
                    # Convert to URL or store directly
                    image_url = await self._store_sd_image(base64_image)
                    
                    logger.info("✅ Stable Diffusion image generated successfully")
                    
                    return {
                        "success": True,
                        "engine": "stable-diffusion",
                        "image_url": image_url,
                        "base64_data": base64_image,  # Keep base64 for immediate use
                        "prompt_used": enhanced_prompt,
                        "model_used": self.sd_engine_id,
                        "size": "1024x1024",
                        "steps": 30,
                        "cfg_scale": 7,
                        "generated_at": datetime.now().isoformat()
                    }
                else:
                    raise Exception("No image artifacts returned from Stable Diffusion")
            else:
                error_data = response.json()
                error_msg = f"Stable Diffusion API error {response.status_code}: {error_data.get('message', 'Unknown error')}"
                logger.error(f"❌ {error_msg}")
                
                # Handle specific Stable Diffusion errors
                if "credit" in error_msg.lower() or "balance" in error_msg.lower():
                    error_msg += " - Please check your Stability AI credit balance."
                elif "content_policy" in error_msg.lower():
                    error_msg += " - Prompt was rejected by content safety system."
                
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "Stable Diffusion API timeout - request took too long"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"❌ Stable Diffusion generation failed: {str(e)}")
            raise e
    
    async def _store_sd_image(self, base64_data: str) -> str:
        """Store Stable Diffusion base64 image and return URL"""
        try:
            # Generate unique filename
            image_id = f"sd_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(base64_data) % 10000:04d}"
            filename = f"{image_id}.png"
            
            # Store in your image storage system
            storage_path = os.getenv('IMAGE_STORAGE_PATH', './storage/images')
            os.makedirs(storage_path, exist_ok=True)
            file_path = os.path.join(storage_path, filename)
            
            # Save base64 as image file
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(base64_data))
            
            # Return the path or URL that your API can serve
            return f"/api/poster/preview/{image_id}"
            
        except Exception as e:
            logger.error(f"❌ Failed to store Stable Diffusion image: {str(e)}")
            # Fallback: return data URL
            return f"data:image/png;base64,{base64_data}"
    
    async def _create_enhanced_sd_prompt(self, original_prompt: str, image_type: str) -> str:
        """Create optimized Stable Diffusion prompts using Groq AI"""
        try:
            if not self.groq_api_key:
                logger.warning("⚠️ Groq API key not available, using basic prompt enhancement")
                return self._basic_sd_prompt_enhancement(original_prompt, image_type)
            
            enhancement_prompt = f"""
            Create an optimized Stable Diffusion image generation prompt for a {image_type}.
            
            Original concept: {original_prompt}
            
            Requirements for Stable Diffusion:
            - Make it visually descriptive and specific
            - Focus on technical accuracy for .NET/software content
            - Use professional digital art style
            - Include specific visual elements that represent the technology
            - Use appropriate technical terminology
            - Avoid ambiguous or abstract descriptions
            - Use appropriate color schemes (blues, modern tech colors)
            - Include style keywords: professional, detailed, clean, modern
            
            Return ONLY the enhanced prompt, no explanations.
            """
            
            enhanced_prompt = await self._call_groq_api(enhancement_prompt)
            
            # Clean up the response
            enhanced_prompt = enhanced_prompt.strip().strip('"').strip()
            
            if len(enhanced_prompt) < 10:  # If Groq returns empty or invalid response
                enhanced_prompt = self._basic_sd_prompt_enhancement(original_prompt, image_type)
            
            logger.info(f"📝 Enhanced SD prompt: {enhanced_prompt[:100]}...")
            return enhanced_prompt
            
        except Exception as e:
            logger.warning(f"⚠️ SD prompt enhancement failed: {str(e)}")
            return self._basic_sd_prompt_enhancement(original_prompt, image_type)
    
    def _basic_sd_prompt_enhancement(self, original_prompt: str, image_type: str) -> str:
        """Basic prompt enhancement for Stable Diffusion"""
        base_prompts = {
            "architecture_diagram": f"professional software architecture diagram: {original_prompt}. clean lines, blue color scheme, abstract technology representation, digital art, highly detailed, 4k",
            "performance": f"visual representation of software performance: {original_prompt}. speed elements, optimization concepts, modern digital art, technical illustration, highly detailed",
            "infographic": f"technology infographic: {original_prompt}. clean design, data visualization, professional style, modern UI elements, digital art",
            "workflow": f"software workflow diagram: {original_prompt}. process flow, modern UI elements, professional design, digital illustration"
        }
        
        return base_prompts.get(image_type, f"professional technology concept: {original_prompt}. modern digital art, clean design, highly detailed, 4k")

    # Keep the existing Mermaid and placeholder methods unchanged...
    async def _generate_mermaid_diagram(self, prompt: str, image_type: str) -> Dict[str, Any]:
        """Generate Mermaid diagram for technical content"""
        try:
            logger.info(f"📊 Generating Mermaid diagram: {image_type}")
            
            mermaid_code = await self._generate_mermaid_code(prompt, image_type)
            image_url = await self._render_mermaid_to_image(mermaid_code)
            
            return {
                "success": True,
                "engine": "mermaid",
                "image_url": image_url,
                "mermaid_code": mermaid_code,
                "prompt_used": prompt,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Mermaid generation failed: {str(e)}")
            raise e

    async def _generate_mermaid_code(self, prompt: str, image_type: str) -> str:
        """Generate Mermaid diagram code"""
        try:
            mermaid_prompt = f"""
            Create a Mermaid diagram for: {prompt}
            Diagram type: {image_type}
            
            Focus on .NET technologies, software architecture, or technical processes.
            Use Microsoft brand colors (#0078d4, #107c10, #d83b01).
            Make it professional and technically accurate.
            
            Return ONLY the Mermaid code.
            """
            
            if self.groq_api_key:
                return await self._call_groq_api(mermaid_prompt)
            else:
                # Fallback Mermaid template
                return f"""graph TB
    A[.NET Application] --> B[Performance Optimization]
    B --> C[Faster Startup]
    B --> D[Reduced Memory]
    B --> E[Improved Throughput]
    
    style A fill:#0078d4,color:#fff
    style B fill:#107c10,color:#fff
    style C fill:#d83b01,color:#fff"""
                
        except Exception as e:
            logger.error(f"❌ Mermaid code generation failed: {str(e)}")
            return """graph TB
    A[.NET Technology] --> B[Features]
    B --> C[Performance]
    B --> D[Scalability]
    
    style A fill:#0078d4,color:#fff
    style B fill:#107c10,color:#fff"""

    async def _render_mermaid_to_image(self, mermaid_code: str) -> str:
        """Render Mermaid code to image"""
        try:
            # Clean the code
            clean_code = " ".join(mermaid_code.split())
            encoded_code = base64.b64encode(clean_code.encode()).decode()
            image_url = f"https://mermaid.ink/img/{encoded_code}"
            
            # Verify the URL works
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                return image_url
            else:
                raise Exception(f"Mermaid rendering failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Mermaid rendering failed: {str(e)}")
            return "https://via.placeholder.com/1024x1024/0078D4/FFFFFF?text=Mermaid+Error"

    async def _generate_placeholder_image(self, prompt: str, image_type: str) -> Dict[str, Any]:
        """Generate placeholder image as fallback"""
        try:
            # Create a more descriptive placeholder
            text = f".NET {image_type.replace('_', ' ').title()}"
            encoded_text = urllib.parse.quote(text)
            
            return {
                "success": True,
                "engine": "placeholder",
                "image_url": f"https://via.placeholder.com/1024x1024/0078D4/FFFFFF?text={encoded_text}",
                "prompt_used": prompt,
                "width": 1024,
                "height": 1024,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Placeholder generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API with error handling"""
        if not self.groq_api_key:
            raise Exception("Groq API key not configured")
        
        try:
            payload = {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                f"{self.groq_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                error_msg = f"Groq API error {response.status_code}: {response.text}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {str(e)}")
            raise e

    async def generate_carousel_images(self, carousel_slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate images for carousel slides with optimal engine selection"""
        processed_slides = []
        
        for slide in carousel_slides:
            try:
                image_prompt = slide.get('image_prompt', '')
                image_type = slide.get('image_type', 'architecture_diagram')
                engine = slide.get('recommended_engine') or slide.get('engine') or 'stable-diffusion'
                
                # Generate image
                image_result = await self.generate_image(image_prompt, image_type, engine)
                
                processed_slides.append({
                    **slide,
                    "engine_used": engine,
                    "image_generation": image_result
                })
                
                logger.info(f"✅ Generated {image_result['engine']} image for slide {slide['slide_number']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to generate image for slide {slide['slide_number']}: {str(e)}")
                processed_slides.append({
                    **slide,
                    "engine_used": "failed",
                    "image_generation": {
                        "success": False,
                        "error": str(e),
                        "engine": "none"
                    }
                })
        
        return processed_slides