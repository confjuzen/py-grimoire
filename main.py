import os
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from pymongo import MongoClient
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel
from bson import ObjectId
import jwt
from fastapi.middleware.cors import CORSMiddleware
import datetime
from typing import List
from fastapi.staticfiles import StaticFiles


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey") 
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
books_collection = db["books"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()



origins = [
    "*",
    "http://localhost",
    "http://localhost:3000/*",
    "http://localhost:4000/*",
    "http://localhost:4000/api/books",
    "http://localhost:3000/static/js/bundle.js",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory="images"), name="images")



class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def create_jwt_token(data: dict, expires_delta: int = TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 

def hash_password(password: str) -> str:
    return pwd_context.hash(password)   

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/api/auth/signup")
async def register_user(user: UserCreate):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    user_id = users_collection.insert_one({
        "email": user.email,
        "password": hashed_pw
    }).inserted_id
    return {"message": "User created"}

@app.post("/api/auth/login")
async def login_user(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token({"sub": user.email})

    return {"userId": str(db_user["_id"]), "token": token}

class Rating(BaseModel):
    userId: str
    rating: int

# Define the Book model
#class Book(BaseModel):
#    print("log3")
#    userId: str
#    title: str
#    author: str
#    imageUrl: str = None  # Set later
#    year: int
#    genre: str
#    ratings: List[Rating]  # Now a proper list
#    avrgRating: int = 0.0  # Default 0.0
#
#    @classmethod
#    def calcAvrgRating(cls, ratings: List[Rating]) -> float:
#        print("log2")
#        if not ratings:
#            return 0.0  # Avoid division by zero
#        return sum(r.rating for r in ratings) / len(ratings)
#
#    @classmethod
#    def img_url(cls, book_id: str, extension: str) -> str:
#        """Generate an image URL based on book ID and extension."""
#        return f"http://localhost:8000/images/{book_id}.{extension}"
#
## Endpoint to post a book with an image
#@app.post("/api/books")
#async def post_book(book: Book, file: UploadFile = File(...)):
#    print("log1", book.dict())
#    if img.content_type not in ["image/jpeg", "image/png", "image/webp"]:
#        raise HTTPException(status_code=400, detail="Invalid image format")
#
#    # Extract file extension
#    extension = img.filename.split(".")[-1]
#
#    # Calculate average rating
#    book.avrgRating = Book.calcAvrgRating(book.ratings)
#
#    # Convert book model to dictionary and remove imageUrl (set later)
#    book_dict = book.dict()
#    book_dict.pop("imageUrl")  # Remove for now
#
#    # Insert book into MongoDB and get the generated ID
#    result = books_collection.insert_one(book_dict)
#    book_id = str(result.inserted_id)
#
#    # Save the image with the book ID as filename
#    img_filename = f"images/{book_id}.{extension}"
#    os.makedirs("images", exist_ok=True)  # Ensure the images directory exists
#    with open(img_filename, "wb") as buffer:
#        shutil.copyfileobj(img.file, buffer)
#
#    # Generate public image URL
#    image_url = Book.img_url(book_id, extension)
#
#    # Update MongoDB document with the image URL
#    books_collection.update_one({"_id": result.inserted_id}, {"$set": {"imageUrl": image_url}})
#
#    return {
#        "message": "Book added successfully",
#        "book_id": book_id,
#        "imageUrl": image_url
#    }
#



# FastAPI route
@app.get("/api/books")
async def get_books():
    books = books_collection.find_one({"title": "A Clockwork Orange"})
    for book in books:
        
        return {
            "id": str(books["_id"]),
            "book":{
                "title": books["title"],
                "author": books["author"],
                "year": books["year"],
                "genre": books["genre"],
                "ratings": books["ratings"],
                "avrgRating": books["averageRating"],
                "userId": books["userId"],
                "imageUrl": books["imageUrl"]
            },
            }



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/add")
def add_data(data: dict):
    collection.insert_one(data)
    return {"message": "Data added successfully", "data": data}

@app.get("/get")
def get_data():
    data = list(books_collection.find({}, {}))
    return {"data": data}

