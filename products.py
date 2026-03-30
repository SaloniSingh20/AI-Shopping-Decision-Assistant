import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_FIELDS = {
	"id",
	"name",
	"category",
	"price",
	"rating",
	"features",
	"tags",
	"description",
}


def _normalize_product(raw: Dict[str, Any]) -> Dict[str, Any]:
	product = dict(raw)
	product["id"] = str(product.get("id", "")).strip()
	product["name"] = str(product.get("name", "")).strip()
	product["category"] = str(product.get("category", "")).strip()
	product["description"] = str(product.get("description", "")).strip()

	try:
		product["price"] = float(product.get("price", 0) or 0)
	except Exception:
		product["price"] = 0.0

	try:
		product["rating"] = float(product.get("rating", 0) or 0)
	except Exception:
		product["rating"] = 0.0

	features = product.get("features", [])
	tags = product.get("tags", [])
	product["features"] = [str(x).strip() for x in (features if isinstance(features, list) else []) if str(x).strip()]
	product["tags"] = [str(x).strip() for x in (tags if isinstance(tags, list) else []) if str(x).strip()]
	return product


def _is_valid_product(product: Dict[str, Any]) -> bool:
	if not REQUIRED_FIELDS.issubset(product.keys()):
		return False
	if not product.get("id") or not product.get("name") or not product.get("category"):
		return False
	if not isinstance(product.get("features"), list) or not isinstance(product.get("tags"), list):
		return False
	return True


def load_products(file_path: str = "products.json") -> List[Dict[str, Any]]:
	path = Path(__file__).resolve().parent / file_path
	if not path.exists():
		return []

	try:
		with path.open("r", encoding="utf-8") as handle:
			data = json.load(handle)
	except Exception:
		return []

	if not isinstance(data, list):
		return []

	cleaned: List[Dict[str, Any]] = []
	for item in data:
		if not isinstance(item, dict):
			continue
		normalized = _normalize_product(item)
		if _is_valid_product(normalized):
			cleaned.append(normalized)
	return cleaned


products = load_products()
