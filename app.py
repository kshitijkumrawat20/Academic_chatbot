from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Initialize FastAPI app
app = FastAPI()

# Add CORS Middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup SQLite database connection via LangChain
db_path = (Path("database.db")).absolute()
engine = create_engine(f"sqlite:///{db_path}")

# Create SQLDatabase instance
db = SQLDatabase(engine)
api_key = "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"
llm = ChatGroq(api_key=api_key, model_name="llama-3.1-70b-versatile", streaming=True)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Initialize LangChain agent
agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    role: str
    message: str

class AssignmentRequest(BaseModel):
    subject: str
    deadline: str
    question: str
    professor: str  # Added professor field

class AttendanceRequest(BaseModel):
    student_id: str
    subject: str
    attendance: int

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = agent.run(request.message)
        return {"response": result}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.post("/add_assignment")
async def add_assignment(request: AssignmentRequest):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assignments (subject, deadline, question, professor) VALUES (?, ?, ?, ?)",
            (request.subject, request.deadline, request.question, request.professor)
        )
        conn.commit()
        conn.close()
        return JSONResponse(content={"response": "Assignment added successfully."})
    except sqlite3.Error as e:
        return JSONResponse(content={"response": f"Database error: {str(e)}"})
    except Exception as e:
        return JSONResponse(content={"response": f"Error: {str(e)}"})

@app.get("/get_assignments")
async def get_assignments():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT subject, deadline, question, professor FROM assignments")
        assignments = cursor.fetchall()
        conn.close()
        return {"assignments": [{"subject": a[0], "deadline": a[1], "question": a[2], "professor": a[3]} for a in assignments]}
    except sqlite3.Error as e:
        return {"response": f"Database error: {str(e)}"}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.post("/update_attendance")
async def update_attendance(request: AttendanceRequest):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE students SET {request.subject} = ? WHERE id = ?",
            (request.attendance, request.student_id)
        )
        conn.commit()
        conn.close()
        return JSONResponse(content={"response": "Attendance updated successfully."})
    except sqlite3.Error as e:
        return JSONResponse(content={"response": f"Database error: {str(e)}"})
    except Exception as e:
        return JSONResponse(content={"response": f"Error: {str(e)}"})

@app.get("/get_students")
async def get_students():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM students")
        students = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        conn.close()
        return {"students": students}
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}
