import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any


class R2StorageService:
    """
    Local filesystem storage service (drop-in replacement for R2).
    Keeps the same method signatures so the rest of the app doesn't need changes.
    """

    def __init__(self):
        self.base_path = Path("local_storage")
        self.base_path.mkdir(exist_ok=True)

    def _full_path(self, key: str) -> Path:
        path = self.base_path / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def get_object(self, key: str) -> Optional[str]:
        try:
            path = self._full_path(key)
            if not path.exists():
                return None
            return path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching {key}: {e}")
            return None

    def put_object(self, key: str, data: str, content_type: str = "text/plain") -> bool:
        try:
            path = self._full_path(key)
            path.write_text(data, encoding="utf-8")
            print(f"Saved locally: {path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save {key} locally: {e}")
            return False

    def get_json(self, key: str) -> Optional[List[Dict[str, Any]]]:
        data = self.get_object(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                print(f"[WARN] Failed to decode JSON from {key}. Starting fresh start.")
                return []
        return []

    def get_articles_json(self, domain: str) -> List[Dict[str, Any]]:
        return self.get_json(f"blogs/{domain}/articles.json") or []

    def save_articles_json(self, domain: str, articles: List[Dict[str, Any]]) -> bool:
        json_str = json.dumps(articles, indent=2, ensure_ascii=False)
        return self.put_object(f"blogs/{domain}/articles.json", json_str, content_type="application/json")

    def get_recent_history(self, domain: str, limit: int = 3) -> List[Dict[str, Any]]:
        articles = self.get_articles_json(domain)
        sorted_articles = sorted(articles, key=lambda x: x.get("date", ""), reverse=True)
        recent = sorted_articles[:limit]
        return [{
            "title": a.get("title"),
            "topic": a.get("topic"),
            "subtopics": a.get("subtopics", "")
        } for a in recent]

    def get_all_domains_last_updated(self) -> Dict[str, str]:
        from blogboard.config.settings import app_settings
        latest_dates = {}
        for domain_slug in app_settings.tags.model_dump().keys():
            articles = self.get_articles_json(domain_slug)
            if not articles:
                latest_dates[domain_slug] = "Never"
            else:
                sorted_articles = sorted(articles, key=lambda x: x.get("date", ""), reverse=True)
                latest_dates[domain_slug] = sorted_articles[0].get("date", "Unknown")
        return latest_dates