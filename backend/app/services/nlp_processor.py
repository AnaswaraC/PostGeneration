import logging
import re
import spacy
import torch
from transformers import pipeline
from typing import Dict, Any, List, Optional
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)
 
class AdvancedNLPProcessor:
    """
    Advanced NLP processor for analyzing, summarizing, and classifying technical content.
    Uses spaCy for structure, transformers for summarization & sentiment.
    """
 
    def __init__(self):
        logger.info("🔍 Initializing Advanced NLP Processor...")
        
        self.nlp = None
        self.summarizer = None
        self.sentiment_analyzer = None
        
        # Suppress specific warnings
        import warnings
        warnings.filterwarnings("ignore", message=".*torch_dtype.*")
        warnings.filterwarnings("ignore", message=".*device.*")
        
        try:
            # Initialize spaCy with better error handling
            try:
                self.nlp = spacy.load("en_core_web_sm")  # Start with small model for reliability
            except OSError:
                logger.warning("⚠️ spaCy model not found. Using fallback mode.")
                self.nlp = None
                
        except Exception as e:
            logger.error(f"❌ Failed to load spaCy: {e}")
            self.nlp = None

        # Initialize transformers with better error handling and updated parameters
        try:
            device = -1  # Use CPU for stability and to avoid warnings
            logger.info("🔄 Initializing transformers on CPU...")
            
            self.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn", 
                device=device,
                dtype=torch.float32  # Use dtype instead of torch_dtype
            )
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=device
            )
            logger.info("✅ Transformers initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Transformers initialization failed: {e}")
            logger.info("🔄 Using lightweight fallback methods")
            self.summarizer = None
            self.sentiment_analyzer = None
 
        # Enhanced technical keyword patterns for .NET
        self.tech_terms = {
            "dotnet", ".net", "asp.net", "blazor", "csharp", "c#", "visual studio", "maui",
            "entity framework", "ef core", "azure", "web api", "vs code", "nuget", "docker",
            "performance", "sdk", "runtime", "framework", "core", "api", "cli", "linq",
            "aspnet", "xamarin", "windows forms", "wpf", "signalr", "razor", "mvc",
            "kubernetes", "microservices", "cloud", "aws", "gcp", "serverless"
        }
        
        # Intent detection patterns
        self.intent_patterns = {
            "announcement": ["release", "announce", "launch", "introduce", "available", "general availability"],
            "update": ["update", "upgrade", "improve", "enhance", "fix", "patch", "bug", "security"],
            "tutorial": ["tutorial", "guide", "learn", "how to", "step by step", "example", "demo"],
            "performance": ["performance", "benchmark", "speed", "fast", "optimize", "memory", "gc"],
            "migration": ["migrate", "upgrade", "port", "compatibility", "breaking change"]
        }

        # Enhanced positive/negative word lists for better sentiment analysis
        self.positive_words = {
            "great", "excellent", "amazing", "improved", "better", "fast", "easy", "new",
            "enhanced", "powerful", "exciting", "innovative", "efficient", "reliable",
            "robust", "scalable", "productive", "intuitive", "seamless", "optimized",
            "performance", "success", "achievement", "breakthrough", "milestone"
        }
        
        self.negative_words = {
            "issue", "problem", "bug", "slow", "difficult", "broken", "deprecated",
            "warning", "error", "failed", "crash", "vulnerability", "security",
            "limitation", "incompatible", "outdated", "legacy", "complex", "challenging"
        }
 
    def process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full NLP analysis and return enriched metadata"""
        
        # Extract text with fallbacks
        text = article.get("full_content") or article.get("summary") or article.get("title", "")
        
        if not text or not text.strip():
            logger.warning("⚠️ No text content for NLP processing")
            return self._get_fallback_analysis(article)
 
        logger.info(f"🧠 Processing NLP for: {article.get('title', 'Unknown')[:50]}...")
 
        try:
            # 1️⃣ Summarization
            summary = self._summarize_text(text)
 
            # 2️⃣ Sentiment & tone
            sentiment_data = self._analyze_sentiment(text)
            tone = self._map_tone(sentiment_data)
 
            # 3️⃣ Entity extraction
            entities = self._extract_entities(text)
 
            # 4️⃣ Keyword extraction
            keywords = self._extract_keywords(text)
 
            # 5️⃣ Technical focus scoring
            tech_score = self._compute_tech_relevance(text)
 
            # 6️⃣ Intent classification
            intent = self._detect_intent(text)
 
            # 7️⃣ Topic modeling
            topic = self._infer_topic(text)

            # 8️⃣ Enhanced analysis for .NET content
            enhanced_sentiment = self._enhance_sentiment_for_dotnet(text, sentiment_data)
 
            return {
                "summary_generated": summary,
                "sentiment": enhanced_sentiment,
                "tone": tone,
                "entities": entities[:10],  # Limit to top 10
                "keywords_nlp": keywords,
                "intent": intent,
                "tech_focus_score": tech_score,
                "topic": topic,
                "processing_success": True
            }
            
        except Exception as e:
            logger.error(f"❌ NLP processing failed: {e}")
            return self._get_fallback_analysis(article)
 
    def _get_fallback_analysis(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Provide basic analysis when full processing fails"""
        title = article.get("title", "")
        return {
            "summary_generated": title[:200],
            "sentiment": {"label": "neutral", "confidence": 0.5, "polarity": 0},
            "tone": "neutral / descriptive",
            "entities": [],
            "keywords_nlp": self._extract_fallback_keywords(article),
            "intent": "general information",
            "tech_focus_score": 0.5,
            "topic": "General",
            "processing_success": False
        }
 
    # --------------------------------------------------------------------
    # SUMMARIZATION
    # --------------------------------------------------------------------
 
    def _summarize_text(self, text: str) -> str:
        """Smart summarization with fallbacks"""
        
        # If transformers not available, use extractive summarization
        if not self.summarizer:
            return self._extractive_summarize(text)
        
        try:
            if len(text.split()) < 50:
                return text.strip()[:300]
                
            # Clean and prepare text
            clean_text = self._clean_text_for_summarization(text)
            
            result = self.summarizer(
                clean_text[:2000],  # More conservative truncation
                max_length=150,
                min_length=30,
                do_sample=False
            )
            return result[0]["summary_text"].strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Transformer summarization failed, using extractive: {e}")
            return self._extractive_summarize(text)
 
    def _extractive_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Fallback extractive summarization"""
        try:
            if self.nlp:
                doc = self.nlp(text[:5000])
                sentences = [sent.text for sent in doc.sents]
                # Simple heuristic: take first few sentences (often contain main points)
                return " ".join(sentences[:num_sentences])
            else:
                # Basic sentence splitting
                sentences = re.split(r'[.!?]+', text)
                clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
                return " ".join(clean_sentences[:num_sentences])
        except:
            return text[:400]
 
    def _clean_text_for_summarization(self, text: str) -> str:
        """Clean text for better summarization"""
        # Remove code blocks, URLs, etc.
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
 
    # --------------------------------------------------------------------
    # SENTIMENT - ENHANCED VERSION
    # --------------------------------------------------------------------
 
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Enhanced sentiment analysis with fallback"""
        if not self.sentiment_analyzer:
            return self._fallback_sentiment(text)
            
        try:
            # Use shorter text for sentiment
            clean_text = text[:512]  # BERT limit
            result = self.sentiment_analyzer(clean_text)[0]
            label = result["label"].lower()
            score = float(result["score"])
            polarity = 1 if "pos" in label else -1 if "neg" in label else 0
            
            return {"label": label, "confidence": score, "polarity": polarity}
            
        except Exception as e:
            logger.warning(f"⚠️ Sentiment analysis failed: {e}")
            return self._fallback_sentiment(text)
 
    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """Enhanced rule-based sentiment as fallback"""
        text_lower = text.lower()
        pos_count = sum(1 for word in self.positive_words if word in text_lower)
        neg_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Bias towards positive for technical announcements
        tech_bias = 1 if any(term in text_lower for term in ["release", "announce", "update", "new"]) else 0
        
        total_words = len(text_lower.split())
        if total_words > 0:
            pos_ratio = pos_count / total_words
            neg_ratio = neg_count / total_words
            
            if pos_ratio > neg_ratio + 0.02 or (pos_count > neg_count and tech_bias):
                confidence = min(0.95, 0.7 + (pos_ratio * 0.3))
                return {"label": "positive", "confidence": confidence, "polarity": 1}
            elif neg_ratio > pos_ratio + 0.02:
                confidence = min(0.95, 0.7 + (neg_ratio * 0.3))
                return {"label": "negative", "confidence": confidence, "polarity": -1}
        
        return {"label": "neutral", "confidence": 0.5, "polarity": 0}

    def _enhance_sentiment_for_dotnet(self, text: str, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance sentiment analysis specifically for .NET technical content"""
        text_lower = text.lower()
        
        # Technical announcements are usually positive
        announcement_terms = ["release", "announce", "launch", "introduce", "available", "general availability"]
        if any(term in text_lower for term in announcement_terms):
            if sentiment["polarity"] < 0:
                # Override negative sentiment for announcements
                return {"label": "positive", "confidence": 0.8, "polarity": 1}
            elif sentiment["polarity"] == 0:
                # Boost neutral sentiment for announcements
                return {"label": "positive", "confidence": 0.75, "polarity": 1}
        
        return sentiment
 
    def _map_tone(self, sentiment: Dict[str, Any]) -> str:
        """Map sentiment to appropriate tone for social media"""
        label = sentiment.get("label", "neutral")
        polarity = sentiment.get("polarity", 0)
        
        if polarity > 0:
            return "exciting / positive"
        elif polarity < 0:
            return "analytical / informative"
        else:
            return "professional / neutral"
 
    # --------------------------------------------------------------------
    # ENTITIES
    # --------------------------------------------------------------------
 
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract entities with fallback"""
        if not self.nlp:
            return []
            
        try:
            doc = self.nlp(text[:5000])  # Limit for performance
            entities = []
            
            for ent in doc.ents:
                # Filter relevant entity types
                if ent.label_ in {"ORG", "PRODUCT", "PERSON", "GPE", "TECH"}:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "relevance": self._entity_relevance(ent.text)
                    })
            
            # Sort by relevance and remove duplicates
            entities.sort(key=lambda x: x["relevance"], reverse=True)
            seen = set()
            unique_entities = []
            
            for entity in entities:
                if entity["text"] not in seen:
                    unique_entities.append(entity)
                    seen.add(entity["text"])
                    
            return unique_entities[:15]  # Return top 15
            
        except Exception as e:
            logger.warning(f"⚠️ Entity extraction failed: {e}")
            return []
 
    def _entity_relevance(self, entity_text: str) -> float:
        """Score entity relevance for .NET content"""
        entity_lower = entity_text.lower()
        
        # High relevance for Microsoft/.NET terms
        if any(term in entity_lower for term in ["microsoft", ".net", "azure", "visual studio"]):
            return 1.0
        # Medium relevance for other tech terms
        elif any(term in entity_lower for term in self.tech_terms):
            return 0.7
        else:
            return 0.3
 
    # --------------------------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------------------------
 
    def _extract_keywords(self, text: str, top_n: int = 12) -> List[str]:
        """Extract keywords with multiple strategies"""
        
        # Strategy 1: Technical term matching
        tech_keywords = []
        text_lower = text.lower()
        for term in self.tech_terms:
            if term in text_lower:
                tech_keywords.append(term)
        
        # Strategy 2: Frequency-based (if spaCy available)
        freq_keywords = []
        if self.nlp:
            try:
                doc = self.nlp(text_lower[:3000])
                tokens = [
                    t.lemma_ for t in doc
                    if t.is_alpha and not t.is_stop 
                    and len(t.lemma_) > 2
                    and t.lemma_ not in tech_keywords
                ]
                freq = Counter(tokens)
                freq_keywords = [word for word, count in freq.most_common(10)]
            except:
                pass
        
        # Combine and deduplicate
        all_keywords = list(set(tech_keywords + freq_keywords))
        return all_keywords[:top_n]
 
    def _extract_fallback_keywords(self, article: Dict[str, Any]) -> List[str]:
        """Extract keywords without NLP dependencies"""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        keywords = []
        
        for term in self.tech_terms:
            if term in text:
                keywords.append(term)
                
        return keywords[:8]
 
    # --------------------------------------------------------------------
    # TECH FOCUS
    # --------------------------------------------------------------------
 
    def _compute_tech_relevance(self, text: str) -> float:
        """Compute technical relevance with normalization"""
        text_lower = text.lower()
        matches = sum(1 for term in self.tech_terms if term in text_lower)
        
        # Normalize by text length to avoid bias for long articles
        word_count = len(text_lower.split())
        if word_count == 0:
            return 0.0
            
        density = matches / max(10, word_count / 100)  # Normalize per 100 words
        return min(1.0, round(density, 2))
 
    # --------------------------------------------------------------------
    # INTENT
    # --------------------------------------------------------------------
 
    def _detect_intent(self, text: str) -> str:
        """Enhanced intent detection"""
        text_lower = text.lower()
        
        # Check each intent pattern
        scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            scores[intent] = score
        
        # Find highest scoring intent
        best_intent = max(scores.items(), key=lambda x: x[1])
        
        if best_intent[1] > 0:
            return best_intent[0]
        else:
            return "general information"
 
    # --------------------------------------------------------------------
    # TOPIC MODELING
    # --------------------------------------------------------------------
 
    def _infer_topic(self, text: str) -> str:
        """Enhanced topic inference"""
        themes = {
            "Web Development": ["asp.net", "blazor", "mvc", "razor", "signalr", "web api"],
            "Mobile Development": ["maui", "xamarin", "android", "ios", "mobile"],
            "Cloud & Azure": ["azure", "cloud", "container", "kubernetes", "docker", "serverless"],
            "Data & ORM": ["entity framework", "ef core", "database", "sql", "linq", "data"],
            "Performance": ["performance", "optimize", "benchmark", "speed", "memory", "gc"],
            "Security": ["authentication", "authorization", "encryption", "identity", "jwt", "oauth"],
            "Tools & IDE": ["visual studio", "vs code", "debug", "intellisense", "tooling"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for topic, keywords in themes.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[topic] = score
        
        best_topic = max(scores.items(), key=lambda x: x[1])
        
        if best_topic[1] > 0:
            return best_topic[0]
        else:
            return "General .NET"