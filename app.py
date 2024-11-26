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
    
    
# Add these new endpoints to app.py

@app.post("/add_student")
async def add_student(student: dict):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, iwt_attendance, toc_attendance, cybersecurity_attendance, 
            dbms_attendance, iwt_marks, toc_marks, cybersecurity_marks, dbms_marks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student['name'], 0, 0, 0, 0, 0, 0, 0, 0))
        conn.commit()
        conn.close()
        return JSONResponse(content={"response": "Student added successfully."})
    except sqlite3.Error as e:
        return JSONResponse(content={"response": f"Database error: {str(e)}"})

@app.delete("/remove_student/{student_id}")
async def remove_student(student_id: int):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return JSONResponse(content={"response": "Student removed successfully."})
    except sqlite3.Error as e:
        return JSONResponse(content={"response": f"Database error: {str(e)}"})

@app.post("/add_notice")
async def add_notice(notice: dict):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO announcements (subject, professor, announcement, date) VALUES (?, ?, ?, ?)",
            (notice['subject'], notice['professor'], notice['announcement'], notice['date'])
        )
        conn.commit()
        conn.close()
        return JSONResponse(content={"response": "Notice added successfully."})
    except sqlite3.Error as e:
        return JSONResponse(content={"response": f"Database error: {str(e)}"})

@app.get("/get_assignments_by_subject/{subject}")
async def get_assignments_by_subject(subject: str):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, subject, deadline, question, professor FROM assignments WHERE subject = ?",
            (subject,)
        )
        assignments = cursor.fetchall()
        conn.close()
        return {
            "assignments": [
                {
                    "id": a[0],
                    "subject": a[1],
                    "deadline": a[2],
                    "question": a[3],
                    "professor": a[4]
                } for a in assignments
            ]
        }
    except sqlite3.Error as e:
        return {"response": f"Database error: {str(e)}"}
# ... (previous code remains unchanged)

@app.get("/get_notices")
async def get_notices():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT subject, professor, announcement, date FROM announcements")
        notices = cursor.fetchall()
        conn.close()
        return {
            "notices": [
                {
                    "subject": n[0],
                    "professor": n[1],
                    "announcement": n[2],
                    "date": n[3]
                } for n in notices
            ]
        }
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

@app.get("/get_notices_by_subject/{subject}")
async def get_notices_by_subject(subject: str):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject, professor, announcement, date FROM announcements WHERE subject = ?",
            (subject,)
        )
        notices = cursor.fetchall()
        conn.close()
        return {
            "notices": [
                {
                    "subject": n[0],
                    "professor": n[1],
                    "announcement": n[2],
                    "date": n[3]
                } for n in notices
            ]
        }
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


