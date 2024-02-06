from fastapi import FastAPI, Query, Path, Body, Cookie
from typing import Dict, Union, List
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import Annotated
from uuid import UUID
from datetime import datetime, time, timedelta

app = FastAPI()

''' Basics Started '''

@app.get("/")
async def root():
    return { "data": "This is root path", "path": "/" }

''' Basics Ended '''


''' Path Params '''

@app.get("/profile/me")
async def profile():
    return { "data": "returns the current user "}

@app.get("/profile/{user_id}")
async def profile(user_id: int):
    return { "data": "Here your profile data will be served", "path": "/profile", "user_id": user_id }


# defining an ENUM for the plan types 
class SubscriptionPlan(str, Enum):
    FREE = 'FREE'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'

@app.get("/plan/{plan_id}")
async def get_subscription_plan(plan_id: str):
    if plan_id is SubscriptionPlan.FREE:
        return { "Plan_type": SubscriptionPlan.FREE }

    if plan_id is SubscriptionPlan.WEEKLY:
        return { "Plan_type": SubscriptionPlan.WEEKLY }

    return { "Plan_type": "This plan does not exist any more" }

@app.get("/files/{file_path: path}")
async def read_file(file_path: str):
    return { "file_path": file_path, "file_name": "user.txt"}

# to call the above api use below URL
# http://localhost:8000/files/%7Bfile_path:%20path%7D?file_path=%2Fharsh%2Fuser%2Freadme.txt

''' Path Params Ended '''

''' Query Params Started '''

products = [i for i in range(100)]

@app.get("/products/{product_id}")
async def get_products(product_id: str, start: int = 0, end: int = 10):
    return { "products": products[start: start + end], "start": start, "end": end }

# optional query param - q is the optional query param
@app.get("/v2/products/{product_id}")
async def get_products(product_id: str, start: int = 0, end: int = 10,  q: Union[str, None] = None):
    if q:
        return { "products": products[start: start + end], "start": start, "end": end, "q": q }

    return { "products": products[start: start + end], "start": start, "end": end }

# required query param - token is required query param
@app.get("/v3/products/{product_id}")
async def get_products(product_id: str, token: str, start: int = 0, end: int = 10,  q: Union[str, None] = None):
    if q:
        return { "products": products[start: start + end], "start": start, "end": end, "q": q }

    return { "products": products[start: start + end], "start": start, "end": end }

''' Query Params Started '''

''' Request Body Started '''

class Product(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

# api to create a new product

@app.post("/create_products")
async def create_product(item: Product):
    return item

# post api with path and query params

@app.post("/v2/create_products/{product_id}")
async def create_product(product_id: str, item: Product, token: str, q: Union[str, None] = None):
    if q:
        return { "product_id": product_id, "product_details": item, "q": q }

    return { "product_id": product_id, "product_details": item }


# string validations on query parameters

@app.post("/v3/create_products/{product_id}")
async def create_product(product_id: str, item: Product, q: Annotated[Union[str, None], Query(min_length=5, max_length=50, pattern="^fixedquery$")] = None):
    if q:
        return { "product_id": product_id, "product_details": item, "q": q }

    return { "product_id": product_id, "product_details": item }

# numeric validations on path parameters

@app.post("/v3/create_products/{product_id}")
async def create_product(
    product_id: Annotated[int, Path(ge=0, le=1000)],
    item: Product,
    q: Annotated[Union[str, None], Query(min_length=5, max_length=10, pattern="^fixedquery$")] = None
):
    if q:
        return { "product_id": product_id, "product_details": item, "q": q }

    return { "product_id": product_id, "product_details": item }    


# multiple parameters - path, query, Body

class Event(BaseModel):
    title: str
    details: Union[str, None] = None
    is_paid: bool
    fee: float


@app.post("/events/{event_id}")
async def create_event(
    event_id: Annotated[int, Path(ge=1, le=999999)],
    event: Union[Event, None] = None,
    q: Annotated[Union[str, None], Query(min_length=5, max_length=10)] = None,
):
    response = { "event_id": event_id }
    if q:
        response["q"] = q

    if event:
        response["event"] = event

    return response

# singular value in body and multiple body params

class User(BaseModel):
    username: str
    email: str
    full_name: Union[str, None] = None


@app.post("/v2/events/{event_id}")
async def create_event(
    event_id: Annotated[int, Path(ge=1, le=999999)],
    is_premium: Annotated[int, Body()],
    user: User,
    event: Union[Event, None] = None,
    q: Annotated[Union[str, None], Query(min_length=5, max_length=10)] = None,
):
    response = { "event_id": event_id, "is_premium": is_premium, "user": user }
    if q:
        response["q"] = q

    if event:
        response["event"] = event

    return response

# embed a single value param

@app.put("/events/{event_id}")
async def update_event(event_id: int, event: Annotated[Event, Body(embed=True)]):
    response = { "event_id": event_id, "event": event }
    return response


'''
with embed=True, FastAPI expects request body like

{
  "event": {
    "title": "string",
    "details": "string",
    "is_paid": true,
    "fee": 0
  }
}

instead of,

{
  "title": "string",
  "details": "string",
  "is_paid": true,
  "fee": 0
}

'''

# validation and meta data inside a pydantic model using Pydantic's Field

class Student(BaseModel):
    name: str = Field(min_length=5, max_length=20, title="Student's Full Name")
    total_marks:float = Field(ge=0)
    subjects: List[str]

@app.post("/students/{student_id}")
async def create_students(student_id: int, student: Annotated[Student, Body(embed=True)]):
    response = { "student_id": student_id, "student": student }
    return response

# Sub models and Nested Models

class Image(BaseModel):
    url: HttpUrl
    name: str = Field(min_length=5, max_length=20, title="Employee's Full Name")

class Employee(BaseModel):
    name: str
    age: int
    teams: List[str]
    image: Union[Image, None] = None
    doc_images: Union[List[Image], None] = None

@app.post("/employee/{emp_id}")
async def create_employee(emp_id: int, employee: Employee):
    response = { "emp_id": emp_id, "employee": employee }
    return response

# model with extra data types - uuid, datetime

@app.post("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[Union[datetime, None], Body()] = None,
    end_datetime: Annotated[Union[datetime, None], Body()] = None,
    interval: Annotated[Union[time, None], Body()] = None,
    process_after: Annotated[Union[timedelta, None], Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process

    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": interval,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }

# cookie params

@app.get("/v2/items/")
async def read_items(ads_id: Annotated[Union[str, None], Cookie()] = None):
    return { "ads_id": ads_id }