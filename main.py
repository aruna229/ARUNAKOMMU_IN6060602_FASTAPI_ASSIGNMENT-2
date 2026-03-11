#DAY2
#TASK2
#PROBLEM1
from fastapi import FastAPI, Query

app = FastAPI()

# Sample product list
products = [
    {"name": "Wireless Mouse", "price": 499, "category": "electronics"},
    {"name": "USB Hub", "price": 799, "category": "electronics"},
    {"name": "Notebook", "price": 99, "category": "stationery"},
]

@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description="Filter by category"),
    max_price: int = Query(None, description="Maximum price"),
    min_price: int = Query(None, description="Minimum price")
):
    # Start with all products
    result = products

    # Filter by category
    if category:
        result = [p for p in result if p["category"] == category]

    # Filter by maximum price
    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    # Filter by minimum price
    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return result
    #PROBLEM2
    from fastapi import FastAPI

app = FastAPI()

# Sample product list with IDs
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "electronics"},
]

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}
   #PROBLEM3
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Sample product list with IDs
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "electronics"},
]

# Feedback storage
feedback = []

# Pydantic model for customer feedback
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback),
    }
#PROBLEM4
from fastapi import FastAPI

app = FastAPI()

# Example product data
products = [
    {"name": "USB Hub", "price": 799, "in_stock": True,  "category": "Electronics"},
    {"name": "Pen Set", "price": 49,  "in_stock": True,  "category": "Stationery"},
    {"name": "Notebook", "price": 199, "in_stock": False, "category": "Stationery"},
    {"name": "Wireless Mouse", "price": 499, "in_stock": True, "category": "Electronics"},
]

@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))

    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }
    #PROBLEM5
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# Example product data with IDs
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 199, "in_stock": False},
    {"id": 3, "name": "USB Hub",        "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,  "in_stock": True},
]

# 🛡️ OrderItem model
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

# 🛡️ BulkOrder model
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

# 📨 Bulk Order Endpoint
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
    }
    #BONUS
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# In-memory store for orders
orders = []
order_counter = 1

# Example product data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 199, "in_stock": False},
    {"id": 3, "name": "USB Hub",        "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,  "in_stock": True},
]

# Models
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

# POST /orders → new orders start as "pending"
@app.post("/orders")
def place_order(order: BulkOrder):
    global order_counter
    confirmed, failed, grand_total = [], [], 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})

    new_order = {
        "order_id": order_counter,
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
        "status": "pending"   # ✏️ start as pending
    }
    orders.append(new_order)
    order_counter += 1
    return {"message": "Order placed", "order": new_order}

# GET /orders/{order_id} → fetch order by ID
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}

# PATCH /orders/{order_id}/confirm → change status to confirmed
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}
# GET all pending orders
@app.get("/orders/pending")
def get_pending_orders():
    pending = [order for order in orders if order["status"] == "pending"]
    return {"pending_orders": pending}    