'''from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
print("RUNNING NEW CODE")
app = FastAPI()

# DB connection (global)
conn = sqlite3.connect('products.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    quantity INTEGER
)
""")
conn.commit()

class Product(BaseModel):
    name: str
    price: float
    quantity: int


@app.get("/")
def home():
    return {"message": "DB connected"}


@app.post("/add_product")  # 👈 SAME name use karo
def add_product(product: Product):
    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
        (product.name, product.price, product.quantity)
    )
    conn.commit()
    return {"message": "Product added"}
@app.get("/products")
def get_products():
    print("PRODUCT API HIT")
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()

    result = []
    for row in data:
        result.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "quantity": row[3]
        })

    return {"products": result}'''
'''from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}
@app.get("/students")
def get_students():
    return [
        {"name": "Kunal", "age": 25},
        {"name": "Rahul", "age": 22}
    ]'''
'''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Temporary database (list)
students = []

# Model (data structure)
class Student(BaseModel):
    name: str
    age: int

# GET API → sab students dikhayega
@app.get("/students")
def get_students():
    return students

# POST API → new student add karega
@app.post("/add-student")
def add_student(student: Student):
    students.append(student)
    return {
        "message": "Student added successfully",
        "data": student
    }'''

from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel

# DB setup
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Table
class StudentDB(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)

Base.metadata.create_all(bind=engine)

# App
app = FastAPI()

class Student(BaseModel):
    name: str
    age: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/add_student")
def add_student(student: Student, db: Session = Depends(get_db)):
    new_student = StudentDB(name=student.name, age=student.age)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(StudentDB).all()


@app.put("/update-student/{student_id}")
def update_student(student_id: int, student: Student, db: Session = Depends(get_db)):
    # 🔍 Step 1: DB se student find karo
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()

    # ❌ Step 2: Agar nahi mila
    if not db_student:
        return {"error": "Student not found"}

    # ✏️ Step 3: Update values
    db_student.name = student.name
    db_student.age = student.age

    # 💾 Step 4: Save changes
    db.commit()

    return {"message": "Student updated successfully"}


