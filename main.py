from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Shopping List API",
    description="A simple and elegant RESTful API for managing shopping lists",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for request/response validation
class ItemRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the item to add")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Milk"
            }
        }

# In-memory storage for shopping list
shopping_list: List[str] = []

# Helper function to normalize item names
def normalize_item_name(name: str) -> str:
    return name.strip().title()

@app.get("/", response_class=PlainTextResponse, summary="Welcome Message")
async def root() -> str:
    """Welcome endpoint for the Shopping List API."""
    return "🛒 Welcome to Shopping List API\n📄 Documentation: /docs\n🔢 Version: 1.0.0"

@app.post(
    "/items",
    response_class=PlainTextResponse,
    status_code=201,
    summary="Add Item to Shopping List",
    description="Add a new item to the shopping list. Item names are case-insensitive and duplicates are not allowed."
)
async def add_item(item: ItemRequest) -> str:
    """Add a new item to the shopping list."""
    normalized_name = normalize_item_name(item.name)
    
    # Check if item already exists (case-insensitive)
    if normalized_name.lower() in [existing_item.lower() for existing_item in shopping_list]:
        raise HTTPException(
            status_code=400,
            detail=f"❌ Item '{normalized_name}' already exists in the list"
        )
    
    shopping_list.append(normalized_name)
    items_text = "\n".join([f"• {item}" for item in shopping_list])
    
    return f"✅ Item '{normalized_name}' added to the list.\n\n🛒 Current Shopping List:\n{items_text}"

@app.get(
    "/items",
    response_class=PlainTextResponse,
    summary="Get All Items",
    description="Retrieve all items currently in the shopping list."
)
async def get_items() -> str:
    """Get all items in the shopping list."""
    if not shopping_list:
        return "📝 Your shopping list is empty."
    
    items_text = "\n".join([f"• {item}" for item in shopping_list])
    return f"🛒 Shopping List ({len(shopping_list)} items):\n{items_text}"

@app.delete(
    "/items/{item_name}",
    response_class=PlainTextResponse,
    summary="Remove Specific Item",
    description="Remove a specific item from the shopping list by name (case-insensitive)."
)
async def remove_item(item_name: str) -> str:
    """Remove a specific item from the shopping list."""
    normalized_name = normalize_item_name(item_name)
    
    # Find and remove item (case-insensitive)
    item_found = False
    for i, existing_item in enumerate(shopping_list):
        if existing_item.lower() == normalized_name.lower():
            removed_item = shopping_list.pop(i)
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(
            status_code=404,
            detail=f"❌ Item '{normalized_name}' not found."
        )
    
    if not shopping_list:
        return f"🗑️ Item '{removed_item}' removed.\n\n📝 Your shopping list is now empty."
    
    items_text = "\n".join([f"• {item}" for item in shopping_list])
    return f"🗑️ Item '{removed_item}' removed.\n\n🛒 Remaining Items:\n{items_text}"

@app.delete(
    "/items",
    response_class=PlainTextResponse,
    summary="Clear All Items",
    description="Remove all items from the shopping list."
)
async def clear_items() -> str:
    """Clear all items from the shopping list."""
    items_count = len(shopping_list)
    shopping_list.clear()
    
    return f"🧹 All items deleted. ({items_count} items removed)\n📝 Your shopping list is now empty."

@app.get(
    "/items/count",
    response_class=PlainTextResponse,
    summary="Count Items",
    description="Get the total count of items in the shopping list along with the items themselves."
)
async def count_items() -> str:
    """Get the count of items in the shopping list."""
    count = len(shopping_list)
    
    if count == 0:
        return "🔢 Count: 0 items\n📝 Your shopping list is empty."
    
    items_text = "\n".join([f"• {item}" for item in shopping_list])
    return f"🔢 Count: {count} items\n\n🛒 Shopping List:\n{items_text}"

# Custom exception handlers for better error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(
        content=exc.detail,
        status_code=exc.status_code
    )

# Health check endpoint
@app.get(
    "/health",
    response_class=PlainTextResponse,
    summary="Health Check",
    description="Check if the API is running properly."
)
async def health_check() -> str:
    """Health check endpoint."""
    return f"✅ Status: Healthy\n🛒 Service: Shopping List API\n📊 Items Count: {len(shopping_list)}"

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )