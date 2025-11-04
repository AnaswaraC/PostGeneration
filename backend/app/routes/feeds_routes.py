# app/routes/dotnet_routes.py
from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Import the enhanced fetcher
from app.services.content_fetcher import fetch_dotnet_content, EnhancedDotNetFetcher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dotnet", tags=["Microsoft .NET Content"])


@router.get("/articles", response_model=Dict[str, Any])
async def get_all_dotnet_articles(
    max_per_feed: int = Query(default=15, ge=1, le=50, description="Max articles per feed"),
    category: Optional[str] = Query(default=None, description="Filter by automatically detected category")
) -> Dict[str, Any]:
    """
    🚀 Fetch ALL Microsoft .NET articles with full content and images
    """
    try:
        logger.info(f"🚀 Fetching .NET articles (max_per_feed={max_per_feed})")
        
        # Fetch all content
        result = await fetch_dotnet_content(max_articles_per_feed=max_per_feed)
        
        # Apply category filter if provided
        articles = result.get('articles', [])
        
        if category:
            filtered_articles = [a for a in articles if a.get('category', '').lower() == category.lower()]
            result['articles'] = filtered_articles
            result['summary']['total_articles'] = len(filtered_articles)
            result['summary']['filtered'] = True
            result['summary']['filters_applied'] = {'category': category}
            logger.info(f"🔍 Filtered by category '{category}': {len(filtered_articles)} articles")
        
        logger.info(f"✅ Successfully fetched {len(articles)} articles")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error fetching articles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to fetch .NET content",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/articles/latest", response_model=Dict[str, Any])
async def get_latest_articles(
    limit: int = Query(default=10, ge=1, le=100, description="Number of latest articles")
) -> Dict[str, Any]:
    """
    📰 Get the latest .NET articles (sorted by publication date)
    """
    try:
        logger.info(f"📰 Fetching {limit} latest articles")
        
        result = await fetch_dotnet_content(max_articles_per_feed=20)
        articles = result.get('articles', [])[:limit]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "count": len(articles),
            "articles": articles
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching latest articles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch latest articles: {str(e)}"
        )


@router.get("/articles/by-category/{category}", response_model=Dict[str, Any])
async def get_articles_by_category(
    category: str,
    limit: int = Query(default=20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    📑 Get articles filtered by automatically detected category
    """
    try:
        logger.info(f"📑 Fetching articles for category: {category}")
        
        result = await fetch_dotnet_content(max_articles_per_feed=20)
        articles = result.get('articles', [])
        
        # Filter by automatically detected category
        filtered = [
            a for a in articles 
            if a.get('category', '').lower() == category.lower()
        ][:limit]
        
        if not filtered:
            available_categories = list(set([a.get('category', 'Unknown') for a in articles]))
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": f"No articles found for category: {category}",
                    "available_categories": available_categories,
                    "total_articles_available": len(articles)
                }
            )
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "count": len(filtered),
            "articles": filtered
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/articles/search", response_model=Dict[str, Any])
async def search_articles(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(default=20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    🔍 Search articles by keyword in title, content, or keywords
    """
    try:
        logger.info(f"🔍 Searching for: {q}")
        
        result = await fetch_dotnet_content(max_articles_per_feed=30)
        articles = result.get('articles', [])
        
        query_lower = q.lower()
        
        matches = []
        for article in articles:
            if (query_lower in article.get('title', '').lower() or
                query_lower in article.get('full_content', '').lower() or
                query_lower in article.get('summary', '').lower() or
                any(query_lower in kw.lower() for kw in article.get('keywords', []))):
                matches.append(article)
        
        matches = matches[:limit]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "query": q,
            "count": len(matches),
            "total_searched": len(articles),
            "articles": matches
        }
        
    except Exception as e:
        logger.error(f"❌ Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/categories", response_model=Dict[str, Any])
async def get_available_categories() -> Dict[str, Any]:
    """
    📋 Get all automatically detected content categories with article counts
    """
    try:
        result = await fetch_dotnet_content(max_articles_per_feed=10)
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "categories": result.get('content_categories', {}),
            "total_categories": len(result.get('content_categories', {}))
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/feeds/status", response_model=Dict[str, Any])
async def get_feeds_status() -> Dict[str, Any]:
    """
    🔧 Check status of all RSS feeds
    """
    try:
        fetcher = EnhancedDotNetFetcher()
        
        feeds_info = []
        for feed in fetcher.DOTNET_FEEDS:
            feeds_info.append({
                "name": feed['name'],
                "url": feed['url']
            })
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_feeds": len(feeds_info),
            "feeds": feeds_info
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    ❤️ API Health Check
    """
    return {
        "status": "healthy",
        "service": "Microsoft .NET Content Fetcher",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "automatic_categorization": "Enabled",
            "full_content_extraction": "Enabled", 
            "image_extraction": "Enabled",
            "keyword_extraction": "Enabled"
        },
        "endpoints": {
            "articles": "/api/dotnet/articles - Get all articles with full content",
            "latest": "/api/dotnet/articles/latest - Get latest articles",
            "by_category": "/api/dotnet/articles/by-category/{category} - Filter by auto-detected category",
            "search": "/api/dotnet/articles/search?q=query - Search articles",
            "categories": "/api/dotnet/categories - List all auto-detected categories",
            "feeds_status": "/api/dotnet/feeds/status - Check feed status",
            "health": "/api/dotnet/health - This endpoint"
        }
    }


@router.get("/articles/export/json")
async def export_articles_json(
    max_per_feed: int = Query(default=50, ge=1, le=100)
) -> Dict[str, Any]:
    """
    💾 Export all articles as JSON (for external use)
    """
    try:
        result = await fetch_dotnet_content(max_articles_per_feed=max_per_feed)
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_articles": len(result.get('articles', [])),
            "sources": result.get('feed_results', []),
            "articles": result.get('articles', [])
        }
        
        return export_data
        
    except Exception as e:
        logger.error(f"❌ Export error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Debug endpoint
@router.get("/debug/categories-with-articles", response_model=Dict[str, Any])
async def debug_categories_with_articles():
    """
    🔍 Debug endpoint to see automatically detected categories
    """
    try:
        result = await fetch_dotnet_content(max_articles_per_feed=10)
        articles = result.get('articles', [])
        
        category_counts = {}
        for article in articles:
            cat = article.get('category', 'Unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_articles_fetched": len(articles),
            "category_distribution": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)),
            "all_categories_available": list(category_counts.keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Error in categories debug: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )