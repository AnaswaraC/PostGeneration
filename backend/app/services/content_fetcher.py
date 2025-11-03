# app/services/content_fetcher.py
import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from collections import Counter
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time

logger = logging.getLogger(__name__)

class EnhancedDotNetFetcher:
    """Comprehensive Microsoft .NET content fetcher with automatic categorization"""
    
    def __init__(self):
        self.session = None
        self.semaphore = asyncio.Semaphore(5)
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    # Microsoft .NET RSS Feeds - No categories or priorities defined
    DOTNET_FEEDS = [
        {
            "name": ".NET Blog",
            "url": "https://devblogs.microsoft.com/dotnet/feed/"
        },
        {
            "name": "Visual Studio Blog", 
            "url": "https://devblogs.microsoft.com/visualstudio/feed/"
        },
        {
            "name": "ASP.NET Blog",
            "url": "https://devblogs.microsoft.com/aspnet/feed/"
        },
        {
            "name": "C# Language",
            "url": "https://devblogs.microsoft.com/dotnet/category/csharp/feed/"
        },
        {
            "name": ".NET Announcements",
            "url": "https://devblogs.microsoft.com/dotnet/category/announcements/feed/"
        },
        {
            "name": ".NET Releases",
            "url": "https://devblogs.microsoft.com/dotnet/category/releases/feed/"
        },
        {
            "name": "Azure .NET",
            "url": "https://devblogs.microsoft.com/dotnet/category/azure/feed/"
        },
        {
            "name": ".NET MAUI", 
            "url": "https://devblogs.microsoft.com/dotnet/category/maui/feed/"
        },
        {
            "name": ".NET Performance",
            "url": "https://devblogs.microsoft.com/dotnet/category/performance/feed/"
        },
        {
            "name": "Entity Framework",
            "url": "https://devblogs.microsoft.com/dotnet/category/entity-framework/feed/"
        },
        {
            "name": ".NET Core",
            "url": "https://devblogs.microsoft.com/dotnet/category/dotnet-core/feed/"
        },
        {
            "name": "Blazor",
            "url": "https://devblogs.microsoft.com/aspnet/category/blazor/feed/"
        },
        {
            "name": ".NET Community",
            "url": "https://devblogs.microsoft.com/dotnet/category/community/feed/"
        },
    ]

    # Category patterns for automatic classification
    CATEGORY_PATTERNS = {
        "News & Announcements": [
            r'announcement', r'announce', r'news', r'update', r'what\'s new',
            r'released', r'general availability', r'ga', r'preview', r'rtm'
        ],
        "Product Releases": [
            r'release', r'version', r'v\d+\.\d+', r'\.net \d+', r'net\d+',
            r'visual studio \d+', r'vs \d+', r'available now', r'now available'
        ],
        "Web Development": [
            r'asp\.net', r'blazor', r'mvc', r'web api', r'razor', r'signalr',
            r'web development', r'web app', r'http', r'rest', r'api'
        ],
        "Mobile Development": [
            r'maui', r'xamarin', r'mobile', r'ios', r'android', r'cross.platform',
            r'phone', r'tablet', r'app'
        ],
        "Cloud & Azure": [
            r'azure', r'cloud', r'aws', r'google cloud', r'deploy', r'scale',
            r'container', r'docker', r'kubernetes', r'aks', r'app service'
        ],
        "Data & ORM": [
            r'entity framework', r'ef core', r'database', r'sql', r'orm',
            r'linq', r'data access', r'migration', r'query'
        ],
        "Programming Language": [
            r'c#', r'csharp', r'f#', r'fsharp', r'vb\.net', r'visual basic',
            r'language', r'syntax', r'compiler', r'roslyn'
        ],
        "Performance & Optimization": [
            r'performance', r'optimization', r'speed', r'memory', r'gc',
            r'garbage collection', r'fast', r'efficient', r'benchmark'
        ],
        "Tools & IDE": [
            r'visual studio', r'vs code', r'vscode', r'ide', r'debug',
            r'intellisense', r'editor', r'tool', r'extension'
        ],
        "Core Platform": [
            r'\.net core', r'netcore', r'core', r'platform', r'runtime',
            r'framework', r'sdk', r'cli'
        ],
        "Web UI Framework": [
            r'blazor', r'web assembly', r'wasm', r'component', r'ui',
            r'frontend', r'javascript', r'interop'
        ],
        "Security": [
            r'security', r'authentication', r'authorization', r'identity',
            r'jwt', r'oauth', r'https', r'encryption', r'secure'
        ],
        "Community": [
            r'community', r'contributor', r'open source', r'oss',
            r'meetup', r'conference', r'user group', r'feedback'
        ],
        "Official Blog": [
            r'\.net blog', r'official', r'microsoft', r'team'
        ]
    }

    async def fetch_all_content(self, max_articles_per_feed: int = 20) -> Dict[str, Any]:
        """
        Fetch all .NET content from Microsoft sources with automatic categorization
        """
        logger.info("🚀 Starting comprehensive .NET content fetch...")
        start_time = time.time()
        
        all_articles = []
        feed_results = []
        
        async with self:
            tasks = []
            for feed in self.DOTNET_FEEDS:
                task = self._fetch_feed_with_semaphore(feed, max_articles_per_feed)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                feed = self.DOTNET_FEEDS[i]
                if isinstance(result, Exception):
                    logger.error(f"❌ Feed {feed['name']} failed: {str(result)}")
                    feed_results.append({
                        "feed_name": feed['name'],
                        "status": "error",
                        "error": str(result),
                        "articles_fetched": 0
                    })
                elif isinstance(result, list):
                    all_articles.extend(result)
                    feed_results.append({
                        "feed_name": feed['name'],
                        "status": "success", 
                        "articles_fetched": len(result)
                    })
                    logger.info(f"✅ {feed['name']}: {len(result)} articles")
            
            # Remove duplicates and sort
            unique_articles = self._deduplicate_articles(all_articles)
            unique_articles.sort(
                key=lambda x: x.get('published_timestamp', datetime.min),
                reverse=True
            )
            
            elapsed_time = time.time() - start_time
            
            # Enhanced response with automatic categorization
            response = {
                "success": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fetch_duration_seconds": round(elapsed_time, 2),
                "summary": {
                    "total_articles": len(unique_articles),
                    "total_feeds_processed": len(self.DOTNET_FEEDS),
                    "successful_feeds": len([r for r in feed_results if r['status'] == 'success']),
                    "failed_feeds": len([r for r in feed_results if r['status'] == 'error']),
                    "total_images": sum(len(a.get('images', [])) for a in unique_articles),
                    "articles_with_content": len([a for a in unique_articles if a.get('has_full_content')]),
                    "articles_with_images": len([a for a in unique_articles if a.get('has_images')]),
                    "average_reading_time_minutes": round(
                        sum(a.get('reading_time_minutes', 0) for a in unique_articles) / len(unique_articles)
                        if unique_articles else 0, 1
                    )
                },
                "feed_results": feed_results,
                "content_categories": self._analyze_categories(unique_articles),
                "articles": unique_articles
            }
            
            logger.info(f"✅ Fetch complete! {len(unique_articles)} unique articles in {elapsed_time:.2f}s")
            return response

    async def _fetch_feed_with_semaphore(self, feed: Dict, max_articles: int) -> List[Dict]:
        async with self.semaphore:
            return await self._fetch_single_feed(feed, max_articles)

    async def _fetch_single_feed(self, feed: Dict, max_articles: int) -> List[Dict]:
        """Fetch and process a single RSS feed"""
        articles = []
        
        try:
            logger.info(f"📡 Fetching: {feed['name']} from {feed['url']}")
            
            async with self.session.get(feed['url']) as response:
                logger.info(f"📊 {feed['name']} - HTTP Status: {response.status}")
                
                if response.status != 200:
                    logger.warning(f"⚠️ HTTP {response.status} for {feed['name']} - {feed['url']}")
                    return articles
                
                content = await response.text()
                parsed_feed = feedparser.parse(content)
                
                if not hasattr(parsed_feed, 'entries') or not parsed_feed.entries:
                    logger.warning(f"⚠️ No entries found in {feed['name']} - {feed['url']}")
                    if hasattr(parsed_feed, 'bozo') and parsed_feed.bozo:
                        logger.warning(f"⚠️ Feed parsing error: {parsed_feed.bozo_exception}")
                    return articles
                
                logger.info(f"📊 {feed['name']}: Processing {len(parsed_feed.entries[:max_articles])} entries")
                
                successful_articles = 0
                for entry in parsed_feed.entries[:max_articles]:
                    try:
                        article = await self._process_entry(entry, feed)
                        if article:
                            articles.append(article)
                            successful_articles += 1
                        await asyncio.sleep(0.2)
                    except Exception as e:
                        logger.error(f"❌ Error processing entry in {feed['name']}: {str(e)}")
                        continue
                
                logger.info(f"✅ {feed['name']}: Successfully processed {successful_articles}/{len(parsed_feed.entries[:max_articles])} articles")
        
        except Exception as e:
            logger.error(f"❌ Error fetching feed {feed['name']} from {feed['url']}: {str(e)}")
        
        return articles

    async def _process_entry(self, entry, feed: Dict) -> Optional[Dict[str, Any]]:
        """Process a single RSS entry with automatic categorization"""
        try:
            url = entry.get('link', '').strip()
            title = entry.get('title', '').strip()
            
            # Skip invalid entries
            if not url or not title or url == 'javascript:void(0)' or url.startswith('#'):
                return None
            
            # Basic article structure
            article = {
                'title': title,
                'url': url,
                'author': self._clean_author(entry.get('author', 'Microsoft .NET Team')),
                'published': entry.get('published', ''),
                'published_timestamp': self._parse_date(entry),
                'feed_source': feed['name'],
                'summary': self._clean_html(entry.get('summary', ''))[:500],
                'tags': self._extract_tags(entry),
            }
            
            # Fetch enhanced full content
            content_data = await self._fetch_enhanced_article_content(url)
            article.update(content_data)
            
            # Combine all text for analysis
            full_text = article.get('full_content', '') + ' ' + article.get('summary', '') + ' ' + title
            
            # Automatic categorization
            article['category'] = self._auto_categorize(full_text, url, title)
            article['keywords'] = self._extract_enhanced_keywords(full_text)
            article['reading_time_minutes'] = self._calculate_reading_time(article.get('full_content', ''))
            
            return article
            
        except Exception as e:
            logger.error(f"❌ Error processing entry: {str(e)}")
            return None

    def _auto_categorize(self, content: str, url: str, title: str) -> str:
        """Automatically categorize content based on patterns"""
        # Combine all text for analysis
        analysis_text = (content + ' ' + title + ' ' + url).lower()
        
        category_scores = {}
        
        # Score each category based on pattern matches
        for category, patterns in self.CATEGORY_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, analysis_text, re.IGNORECASE)
                score += len(matches) * 2  # Weight matches
            
            # Additional scoring based on URL patterns
            if category.lower() in url.lower():
                score += 3
            
            if score > 0:
                category_scores[category] = score
        
        # Return the highest scoring category, or "General" if none found
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            logger.debug(f"📊 Categorized as '{best_category}' with score {category_scores[best_category]}")
            return best_category
        else:
            return "General"

    async def _fetch_enhanced_article_content(self, url: str) -> Dict[str, Any]:
        """Fetch enhanced article content with better parsing"""
        try:
            async with self.session.get(url, timeout=20) as response:
                if response.status != 200:
                    return self._empty_content_response()
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove unwanted elements but keep structure
                for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
                    element.decompose()
                
                # Find main content area with multiple strategies
                main_content = self._find_main_content(soup)
                
                if not main_content:
                    main_content = soup
                
                # Extract structured content
                content_data = self._extract_structured_content(main_content, url)
                
                return content_data
        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Timeout fetching content from {url}")
            return self._empty_content_response()
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch enhanced content from {url}: {str(e)}")
            return self._empty_content_response()

    def _find_main_content(self, soup) -> BeautifulSoup:
        """Find main content area using multiple strategies"""
        content_selectors = [
            'article',
            '.entry-content',
            '.post-content', 
            '.article-content',
            '.main-content',
            '.content',
            'main',
            '[role="main"]',
            '.blog-post-content',
            '.single-content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return content
        
        # Fallback: look for div with most paragraphs
        divs_with_paragraphs = soup.find_all('div')
        if divs_with_paragraphs:
            best_div = max(divs_with_paragraphs, 
                         key=lambda d: len(d.find_all(['p', 'h1', 'h2', 'h3', 'h4'])))
            if len(best_div.find_all(['p', 'h1', 'h2', 'h3', 'h4'])) > 3:
                return best_div
        
        return soup

    def _extract_structured_content(self, content, base_url: str) -> Dict[str, Any]:
        """Extract structured content with paragraphs and images"""
        # Extract text content
        paragraphs = []
        for p in content.find_all(['p', 'h1', 'h2', 'h3', 'h4']):
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                paragraphs.append(text)
        
        full_content = '\n\n'.join(paragraphs)
        
        # Enhanced image extraction
        images = self._extract_enhanced_images(content, base_url)
        
        # Extract code snippets
        code_blocks = []
        for block in content.find_all(['pre', 'code']):
            code_text = block.get_text(strip=True)
            if len(code_text) > 10:
                code_blocks.append(code_text)
        
        return {
            'full_content': full_content[:20000],
            'content_length': len(full_content),
            'paragraph_count': len(paragraphs),
            'images': images,
            'has_full_content': bool(full_content.strip()),
            'has_images': len(images) > 0,
            'has_code': len(code_blocks) > 0,
            'code_snippet_count': len(code_blocks),
        }

    def _extract_enhanced_images(self, content, base_url: str) -> List[Dict[str, Any]]:
        """Extract images with enhanced metadata"""
        images = []
        seen_urls = set()
        
        for img in content.find_all('img'):
            # Try multiple src attributes
            src = (img.get('src') or 
                  img.get('data-src') or 
                  img.get('data-lazy-src') or
                  img.get('data-original'))
            
            if not src or src.startswith('data:') or 'pixel' in src.lower():
                continue
            
            # Make absolute URL
            full_url = urljoin(base_url, src)
            
            # Skip duplicates and tracking pixels
            if (full_url in seen_urls or 
                self._is_tracking_pixel(full_url, img) or
                'avatar' in full_url.lower()):
                continue
            
            seen_urls.add(full_url)
            
            # Enhanced image metadata
            image_data = {
                'url': full_url,
                'alt': img.get('alt', '')[:300],
                'title': img.get('title', '')[:300],
                'width': img.get('width'),
                'height': img.get('height'),
                'type': self._categorize_image(img, full_url),
                'caption': self._extract_image_caption(img),
            }
            
            images.append(image_data)
        
        return images[:25]

    def _extract_image_caption(self, img_tag) -> str:
        """Extract image caption from surrounding elements"""
        # Check for figcaption
        parent = img_tag.parent
        if parent and parent.name == 'figure':
            caption = parent.find('figcaption')
            if caption:
                return caption.get_text(strip=True)[:500]
        
        # Check next sibling paragraph
        next_elem = img_tag.find_next_sibling()
        if (next_elem and next_elem.name == 'p' and 
            len(next_elem.get_text(strip=True)) < 200):
            return next_elem.get_text(strip=True)[:500]
        
        return ""

    def _clean_author(self, author: str) -> str:
        """Clean author name"""
        if not author:
            return "Microsoft .NET Team"
        
        # Remove email addresses and extra whitespace
        author = re.sub(r'<[^>]+>', '', author)
        author = re.sub(r'\s+', ' ', author).strip()
        
        return author[:100]

    def _extract_enhanced_keywords(self, text: str, top_n: int = 15) -> List[str]:
        """Extract enhanced keywords with .NET focus"""
        if not text:
            return []
        
        words = re.findall(r'\b[A-Za-z#\+\.]{2,}\b', text.lower())
        
        dotnet_terms = {
            'dotnet', 'net', 'csharp', 'fsharp', 'aspnet', 'blazor', 'maui',
            'entity', 'framework', 'core', 'web', 'api', 'mvc', 'razor',
            'visual', 'studio', 'azure', 'cloud', 'performance', 'security',
            'update', 'release', 'announcement', 'tutorial', 'guide', 'code',
            'development', 'programming', 'windows', 'linux', 'macos',
            'github', 'copilot', 'ai', 'machine', 'learning', 'docker',
            'kubernetes', 'microservices', 'asp.net', '.net'
        }
        
        common_stop_words = {
            'the', 'and', 'for', 'that', 'with', 'this', 'have', 'from',
            'will', 'are', 'can', 'was', 'were', 'been', 'what', 'when',
            'where', 'which', 'who', 'how', 'your', 'their', 'our', 'its'
        }
        
        filtered = [w for w in words if w in dotnet_terms and w not in common_stop_words]
        common = Counter(filtered).most_common(top_n)
        
        return [word for word, _ in common]

    # Utility methods
    def _categorize_image(self, img_tag, url: str) -> str:
        alt = (img_tag.get('alt', '') or '').lower()
        title = (img_tag.get('title', '') or '').lower()
        url_lower = url.lower()
        
        if any(word in alt + title for word in ['logo', 'brand', 'icon']):
            return 'logo'
        elif any(word in alt + title for word in ['screenshot', 'screen', 'ui', 'interface']):
            return 'screenshot'
        elif any(word in alt + title for word in ['diagram', 'architecture', 'chart', 'graph', 'flow']):
            return 'diagram'
        elif any(word in alt + title for word in ['code', 'snippet', 'example']):
            return 'code_example'
        elif any(word in url_lower for word in ['banner', 'hero', 'header']):
            return 'banner'
        else:
            return 'content_image'

    def _is_tracking_pixel(self, url: str, img_tag) -> bool:
        width = img_tag.get('width', '')
        height = img_tag.get('height', '')
        
        if width == '1' or height == '1':
            return True
        
        tracking_patterns = ['track', 'pixel', 'analytics', 'beacon', 'spacer']
        return any(pattern in url.lower() for pattern in tracking_patterns)

    def _extract_tags(self, entry) -> List[str]:
        tags = []
        if hasattr(entry, 'tags'):
            tags.extend([tag.term for tag in entry.tags if hasattr(tag, 'term')])
        if hasattr(entry, 'categories'):
            tags.extend([cat for cat in entry.categories if isinstance(cat, str)])
        return list(set(tags))[:15]

    def _parse_date(self, entry) -> datetime:
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_tuple = getattr(entry, field)
                    return datetime(*time_tuple[:6], tzinfo=timezone.utc)
                except:
                    pass
        return datetime.now(timezone.utc)

    def _clean_html(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _calculate_reading_time(self, content: str) -> float:
        if not content:
            return 0.0
        word_count = len(content.split())
        return round(word_count / 200, 1)

    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        seen_urls = set()
        unique = []
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(article)
        return unique

    def _analyze_categories(self, articles: List[Dict]) -> Dict[str, int]:
        categories = {}
        for article in articles:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))

    def _empty_content_response(self) -> Dict[str, Any]:
        return {
            'full_content': '',
            'content_length': 0,
            'paragraph_count': 0,
            'images': [],
            'has_full_content': False,
            'has_images': False,
            'has_code': False,
            'code_snippet_count': 0,
        }


# FastAPI integration function
async def fetch_dotnet_content(max_articles_per_feed: int = 20) -> Dict[str, Any]:
    """
    Fetch all Microsoft .NET content with automatic categorization
    """
    fetcher = EnhancedDotNetFetcher()
    return await fetcher.fetch_all_content(max_articles_per_feed)