"""
智能学情分析SaaS管理平台 - 完整后端服务
技术栈：FastAPI + SQLAlchemy + Pydantic + JWT
启动命令：python app.py
访问地址：http://localhost:8000
API文档：http://localhost:8000/docs
"""
import os

os.environ["PASSLIB_BCRYPT_COMPAT"] = "true"
import math
import re
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from enum import Enum
import httpx
from fastapi import UploadFile, File
import os
import uuid
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, Enum as SQLEnum, ForeignKey, JSON, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
import uvicorn


# ========== 配置 ==========
class Settings:
    APP_NAME: str = "智能学情分析SaaS管理平台"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "mykey2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./data/learning.db")


settings = Settings()

# ========== DeepSeek AI 配置 ==========
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-0f1f0438d56346f0b0a9cf941c2cd578")  # 生产部署请用环境变量覆盖
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
# 创建目录
os.makedirs("./data", exist_ok=True)

# ========== 日志配置 ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== 枚举定义 ==========
class UserRole(str, Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"  # 👈 加这一行
    ADMIN = "admin"


class Subject(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"


class MasteryLevel(str, Enum):
    MASTERED = "mastered"
    MEDIUM = "medium"
    WEAK = "weak"
    CRITICAL = "critical"


class AlertType(str, Enum):
    WEAK = "weak_knowledge"
    DECAY = "decay_risk"
    DANGER = "danger_zone"


class MessageType(str, Enum):
    SYSTEM = "system"
    USER = "user"


# ========== 数据库模型 ==========
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    original_role = Column(String(20), nullable=True)
    current_subject = Column(SQLEnum(Subject), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)
    grade = Column(String(20), nullable=True)
    school = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(200), nullable=True)
    total_learning_hours = Column(Float, default=0.0)
    average_accuracy = Column(Float, default=0.0)
    weak_knowledge_count = Column(Integer, default=0)
    knowledge_mastery = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Integer, nullable=False)
    correct_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    subject = Column(SQLEnum(Subject), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    subject = Column(SQLEnum(Subject), nullable=False)
    mastery_level = Column(SQLEnum(MasteryLevel), default=MasteryLevel.MEDIUM)
    accuracy = Column(Float, default=0.0)
    correct_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    consecutive_low_count = Column(Integer, default=0)
    consecutive_high_count = Column(Integer, default=0)
    last_review_date = Column(DateTime, default=datetime.utcnow)
    is_alert = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=0)
    due_date = Column(DateTime, nullable=True)
    scheduled_date = Column(DateTime, default=datetime.utcnow)
    is_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(50), nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False)
    content = Column(Text, nullable=False)
    chart_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 班级表
class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 教师ID
    name = Column(String(50), nullable=False)  # 班级名称
    grade = Column(String(20), nullable=True)  # 年级
    class_code = Column(String(20), unique=True, nullable=False)  # 班级邀请码
    created_at = Column(DateTime, default=datetime.utcnow)


# 班级-学生关联表
class ClassStudent(Base):
    __tablename__ = "class_students"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)


# 家长-孩子关联表
class ParentChild(Base):
    __tablename__ = "parent_children"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



# ========== 数据库引擎 ==========
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ========= 密码工具 =========
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """获取密码哈希值，自动截断过长的密码"""
    if password and len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if plain_password and len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


# ========== JWT工具 ==========
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ========== 业务工具函数 ==========
def calculate_percentage(part: float, total: float) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def calculate_growth_rate(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def calculate_mastery_level(accuracy: float) -> MasteryLevel:
    if accuracy >= 90:
        return MasteryLevel.MASTERED
    elif accuracy >= 50:
        return MasteryLevel.MEDIUM
    else:
        return MasteryLevel.CRITICAL


def calculate_knowledge_mastery(knowledge_points: List) -> float:
    if not knowledge_points:
        return 0.0
    total_accuracy = sum(kp.accuracy for kp in knowledge_points)
    return round(total_accuracy / len(knowledge_points), 2)


def check_weak_alert(consecutive_low_count: int) -> bool:
    return consecutive_low_count >= 3


def check_mastered_condition(consecutive_high_count: int) -> bool:
    return consecutive_high_count >= 5


def check_decay_risk(last_review_date: datetime) -> bool:
    days_since_review = (datetime.utcnow() - last_review_date).days
    return days_since_review >= 5


def taylor_series_expansion(x: float, terms: int = 5) -> float:
    result = 0.0
    factorial = 1
    for n in range(terms):
        if n > 0:
            factorial *= n
        result += (x ** n) / factorial
    return round(result, 6)


def generate_chart_data_for_taylor(x_range: List[float], terms: int = 5) -> Dict[str, Any]:
    actual = [math.exp(x) for x in x_range]
    approximate = [taylor_series_expansion(x, terms) for x in x_range]
    return {
        "chart_type": "line",
        "title": f"泰勒展开多项式拟合 (前{terms}项)",
        "labels": [round(x, 2) for x in x_range],
        "datasets": [
            {"label": "实际值 e^x", "data": [round(v, 4) for v in actual], "borderColor": "#4CAF50"},
            {"label": f"泰勒拟合 (n={terms})", "data": [round(v, 4) for v in approximate], "borderColor": "#FF5722"}
        ]
    }


def generate_smart_questions(knowledge_point: str, difficulty: str = "medium", count: int = 5) -> List[Dict]:
    difficulty_map = {"easy": 0.3, "medium": 0.6, "hard": 0.9}
    diff_factor = difficulty_map.get(difficulty, 0.6)
    questions = []
    for i in range(count):
        questions.append({
            "id": f"q_{i + 1}_{int(datetime.utcnow().timestamp())}",
            "knowledge_point": knowledge_point,
            "difficulty": difficulty,
            "score": int(10 + diff_factor * 10),
            "content": f"{knowledge_point}练习题 {i + 1}",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "correct_answer": chr(65 + i % 4),
            "analysis": f"本题考查{knowledge_point}的核心概念"
        })
    return questions


def generate_mindmap_data(knowledge_points: List) -> Dict[str, Any]:
    return {
        "root": {
            "id": "root",
            "label": "知识体系",
            "children": [
                {
                    "id": f"kp_{kp.id}",
                    "label": kp.name,
                    "mastery": kp.mastery_level.value,
                    "accuracy": kp.accuracy,
                    "children": [{"id": f"sub_{kp.id}_{i}", "label": f"子知识点 {i + 1}"} for i in range(2)]
                }
                for kp in knowledge_points[:5]
            ]
        }
    }


# ========== Pydantic Schemas ==========
class Response(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

    @classmethod
    def success(cls, data=None, message="success"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message="error", code=400, data=None):
        return cls(code=code, message=message, data=data)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v


# ✅ 新增：用户注册模型
class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: str = Field("student", description="角色: student/parent/teacher")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ["student", "parent", "teacher"]
        if v not in valid_roles:
            return "student"
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "zhangsan",
                "password": "123456",
                "role": "student"
            }
        }
    )


# ✅ 新增：用户更新模型
class UserUpdate(BaseModel):
    """用户信息更新模型"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    current_subject: Optional[Subject] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('邮箱格式不正确')
        return v


# ✅ 新增：修改密码模型
class PasswordChange(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., min_length=6, max_length=50)
    new_password: str = Field(..., min_length=6, max_length=50)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码至少6位')
        return v


class UserInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: Optional[str]
    role: UserRole
    current_subject: Optional[Subject]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRoleSwitch(BaseModel):
    role: UserRole
    subject: Optional[Subject] = None


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=150)
    grade: Optional[str] = Field(None, max_length=20)
    school: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=200)


class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None


class CustomerUpdate(CustomerBase):
    pass


class CustomerInfo(CustomerBase):
    id: int
    user_id: int
    total_learning_hours: float
    average_accuracy: float
    weak_knowledge_count: int
    knowledge_mastery: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    knowledge_mastery: float = Field(..., ge=0, le=100)
    weekly_learning_hours: float
    weak_knowledge_count: int
    average_accuracy: float = Field(..., ge=0, le=100)
    weekly_growth_rate: float
    weekly_data: Dict[str, Any]


class KnowledgePointBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subject: Subject
    tags: Optional[List[str]] = []


class KnowledgePointCreate(KnowledgePointBase):
    user_id: int


class KnowledgePointUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    mastery_level: Optional[MasteryLevel] = None
    accuracy: Optional[float] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None


class KnowledgePointInfo(KnowledgePointBase):
    id: int
    user_id: int
    mastery_level: MasteryLevel
    accuracy: float
    correct_count: int
    total_count: int
    consecutive_low_count: int
    consecutive_high_count: int
    is_alert: bool
    last_review_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    priority: int = Field(0, ge=0, le=10)
    due_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    is_review: bool = False


class TaskCreate(TaskBase):
    user_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=10)
    due_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None


class TaskInfo(TaskBase):
    id: int
    user_id: int
    status: str
    scheduled_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskProgress(BaseModel):
    total_tasks: int
    completed_tasks: int
    progress_percentage: float = Field(..., ge=0, le=100)
    pending_tasks: int
    doing_tasks: int


class ChatMessageCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    message_type: MessageType


class ChatMessageInfo(BaseModel):
    id: int
    user_id: int
    session_id: str
    message_type: MessageType
    content: str
    chart_data: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertInfo(BaseModel):
    id: int
    user_id: int
    knowledge_point_id: Optional[int]
    alert_type: AlertType
    title: str
    description: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== 数据库初始化 ==========
def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                full_name="系统管理员",
                role=UserRole.ADMIN,
                current_subject=Subject.MATH
            )
            db.add(admin)
            db.commit()

            student = db.query(User).filter(User.username == "xiaoli").first()
            if not student:
                student = User(
                    username="xiaoli",
                    password_hash=get_password_hash("123456"),
                    full_name="小李",
                    role=UserRole.STUDENT,
                    current_subject=Subject.MATH
                )
                db.add(student)
                db.commit()

                customer = Customer(
                    user_id=student.id,
                    name="小李",
                    age=18,
                    grade="高三",
                    school="重点中学",
                    phone="13800138000",
                    total_learning_hours=120.5,
                    average_accuracy=73.5,
                    weak_knowledge_count=5,
                    knowledge_mastery=68.0
                )
                db.add(customer)
                db.commit()

                kp_data = [("函数与导数", 65.0), ("三角函数", 70.0), ("数列", 75.0), ("立体几何", 80.0),
                           ("解析几何", 60.0)]
                for name, acc in kp_data:
                    kp = KnowledgePoint(
                        user_id=student.id,
                        name=name,
                        subject=Subject.MATH,
                        mastery_level=MasteryLevel.MEDIUM,
                        accuracy=acc,
                        total_count=10,
                        tags=["高中数学", "重点"]
                    )
                    db.add(kp)

                for i in range(30):
                    record = LearningRecord(
                        customer_id=customer.id,
                        date=datetime.utcnow() - timedelta(days=i),
                        duration_minutes=random.randint(30, 90),
                        correct_count=random.randint(5, 10),
                        total_count=10,
                        accuracy=random.randint(50, 90),
                        subject=Subject.MATH
                    )
                    db.add(record)
                db.commit()
                logger.info("示例数据初始化完成")
    except Exception as e:
        logger.error(f"初始化数据失败: {e}")
        db.rollback()
    finally:
        db.close()


# ========== 依赖注入 ==========
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# ========== 创建FastAPI应用 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在初始化数据库...")
    init_database()
    logger.info("数据库初始化完成")
    yield
    logger.info("应用正在关闭...")


app = FastAPI(
    title="智能学情分析SaaS管理平台",
    description="商用学情分析SaaS系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"请求: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"响应: {request.method} {request.url.path} - 状态: {response.status_code} - 耗时: {process_time:.3f}s")
        return response
    except Exception as e:
        logger.error(f"请求处理异常: {str(e)}")
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": f"系统内部错误: {str(exc)}", "data": None}
    )


# ============================================================
# ==================== 路由定义 ===============================
# ============================================================

# ---------- 用户认证路由 ----------
auth_router = APIRouter(prefix="/api/auth", tags=["用户认证"])


@auth_router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        return Response.error("用户名或密码错误", 401)
    if not user.is_active:
        return Response.error("账户已被禁用", 403)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Response.success({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "original_role": user.original_role,
            "current_subject": user.current_subject.value if user.current_subject else None
        }
    })


# 注册接口
@auth_router.post("/register")
async def register(
        user_data: UserRegister,
        db: Session = Depends(get_db)
):
    role_map = {
        "student": UserRole.STUDENT,
        "parent": UserRole.PARENT,
        "teacher": UserRole.ADMIN,
        "admin": UserRole.ADMIN
    }
    """
    用户注册接口（支持角色选择）
    """


    # 1. 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return Response.error("用户名已存在", 400)

    # 2. 角色映射
    role_map = {
        "student": UserRole.STUDENT,
        "parent": UserRole.PARENT,
        "teacher": UserRole.ADMIN,  # ✅ 改回 ADMIN
        "admin": UserRole.ADMIN
    }

    # 3. 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.username,
        role=role_map.get(user_data.role, UserRole.STUDENT),
        original_role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. ✅ 所有角色都创建客户档案（修改这里）
    try:
        customer = Customer(
            user_id=new_user.id,
            name=new_user.username,
            age=None,
            grade=None,
            school=None,
            phone=None,
            address=None,
            total_learning_hours=0.0,
            average_accuracy=0.0,
            weak_knowledge_count=0,
            knowledge_mastery=0.0,
            created_at=datetime.utcnow()
        )
        db.add(customer)
        db.commit()
        logger.info(f"为用户 {new_user.username} 创建客户档案成功")
    except Exception as e:
        logger.error(f"创建客户档案失败: {e}")
        # 不影响用户注册成功

    # 5. 生成访问令牌（自动登录）
    access_token = create_access_token(
        data={
            "sub": new_user.username,
            "user_id": new_user.id,
            "role": new_user.role.value
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # 6. 返回响应
    return Response.success({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "role": new_user.role.value,
            "current_subject": new_user.current_subject.value if new_user.current_subject else None,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat()
        }
    }, "注册成功")


# ✅ 新增：获取所有用户（管理员功能）
@auth_router.get("/users")
async def get_all_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取所有用户列表（仅管理员）"""
    # 检查是否是管理员
    if current_user.role != UserRole.ADMIN:
        return Response.error("权限不足，仅管理员可查看所有用户", 403)

    users = db.query(User).offset(skip).limit(limit).all()
    return Response.success([UserInfo.from_orm(user) for user in users])


# ✅ 新增：更新用户信息
@auth_router.put("/user/{user_id}")
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新用户信息（用户自己或管理员）"""
    # 检查权限：只能更新自己的信息，或者是管理员
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        return Response.error("权限不足，只能修改自己的信息", 403)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response.error("用户不存在", 404)

    # 更新字段
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return Response.success(UserInfo.from_orm(user), "用户信息更新成功")


# ✅ 新增：修改密码
@auth_router.post("/change-password")
async def change_password(
        password_data: PasswordChange,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """修改当前用户密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        return Response.error("原密码错误", 400)

    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return Response.success(message="密码修改成功")


# ✅ 新增：删除用户（管理员功能）
@auth_router.delete("/user/{user_id}")
async def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    # 检查权限
    if current_user.role != UserRole.ADMIN:
        return Response.error("权限不足，仅管理员可删除用户", 403)

    # 不能删除自己
    if current_user.id == user_id:
        return Response.error("不能删除当前登录的管理员账户", 400)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response.error("用户不存在", 404)

    # 软删除（标记为不活跃）
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()

    return Response.success(message=f"用户 {user.username} 已禁用")


# ✅ 新增：激活用户（管理员功能）
@auth_router.put("/user/{user_id}/activate")
async def activate_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """激活用户（仅管理员）"""
    if current_user.role != UserRole.ADMIN:
        return Response.error("权限不足，仅管理员可激活用户", 403)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response.error("用户不存在", 404)

    user.is_active = True
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return Response.success(UserInfo.from_orm(user), f"用户 {user.username} 已激活")


@auth_router.post("/switch-role")
async def switch_role(role_data: UserRoleSwitch, current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    user.role = role_data.role
    if role_data.subject:
        user.current_subject = role_data.subject
    db.commit()
    db.refresh(user)
    return Response.success({"message": f"角色已切换为 {role_data.role.value}", "user": UserInfo.from_orm(user)})


@auth_router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return Response.success(UserInfo.from_orm(current_user))


# ===== AI对话路由 =====
ai_router = APIRouter(prefix="/api/ai", tags=["AI对话"])


@ai_router.post("/chat/message")
async def send_chat_message(
        msg_data: ChatMessageCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """发送对话消息 - 使用 DeepSeek AI"""

    # 保存用户消息
    user_message = ChatMessage(
        user_id=current_user.id,
        session_id=msg_data.session_id,
        message_type=msg_data.message_type,
        content=msg_data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # 如果是系统引擎消息，调用 DeepSeek API
    if msg_data.message_type == MessageType.SYSTEM:
        # 获取历史对话（最近10条）
        history = db.query(ChatMessage).filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.session_id == msg_data.session_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        history.reverse()

        # 构建消息列表
        messages = []
        for h in history:
            role = "user" if h.message_type == MessageType.USER else "assistant"
            messages.append({"role": role, "content": h.content})

        # 添加系统提示
        system_prompt = """你是一个智能学习助手，帮助学生解决学习问题。你的名字叫"学伴"。
你擅长：
1. 讲解数学、物理、化学等学科知识
2. 分析学习问题，给出学习建议
3. 生成练习题和复习计划
4. 用通俗易懂的方式解释复杂概念

回答要简洁、清晰、有条理。如果涉及公式，用文字描述。
"""

        messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            # 调用 DeepSeek API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    DEEPSEEK_API_URL,
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                reply = data["choices"][0]["message"]["content"]

        except Exception as e:
            reply = f"❌ AI 服务暂时不可用，请稍后重试。\n\n错误信息：{str(e)}"

        # 保存 AI 回复
        ai_message = ChatMessage(
            user_id=current_user.id,
            session_id=msg_data.session_id,
            message_type=MessageType.SYSTEM,
            content=reply
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        return Response.success(ChatMessageInfo.from_orm(ai_message), "AI回复成功")

    return Response.success(ChatMessageInfo.from_orm(user_message), "消息发送成功")


@ai_router.get("/chart/taylor")
async def get_taylor_chart_data(terms: int = 5):
    """获取泰勒展开图表数据"""
    x_range = [round(x * 0.5, 1) for x in range(-6, 7)]
    chart_data = generate_chart_data_for_taylor(x_range, terms)
    return Response.success(chart_data)


# ===== 工具能力路由 =====
tools_router = APIRouter(prefix="/api/tools", tags=["工具能力"])


@tools_router.post("/ocr/recognize")
async def ocr_recognize(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """OCR 图片识别接口"""
    try:
        contents = await file.read()

        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)

        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        temp_path = f"{temp_dir}/{uuid.uuid4()}.{file_ext}"

        with open(temp_path, "wb") as f:
            f.write(contents)

        # 模拟 OCR 识别
        recognized_text = "识别到的文字：答案是2x"

        os.remove(temp_path)

        return Response.success({
            "recognized_text": recognized_text,
            "confidence": 95.5,
            "result": {"text": recognized_text}
        }, "OCR识别成功")

    except Exception as e:
        return Response.error(f"OCR识别失败：{str(e)}", 500)


@tools_router.post("/analyze/homework")
async def analyze_homework(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """作业图片分析接口（模拟AI生成检测）"""
    try:
        contents = await file.read()
        file_size = len(contents)

        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        temp_path = f"{temp_dir}/{uuid.uuid4()}.{file_ext}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        os.remove(temp_path)

        # 模拟 AI 生成检测分析
        ai_probability = round(random.uniform(15, 85), 1)
        is_ai_generated = ai_probability > 50
        confidence = round(random.uniform(70, 98), 1)
        avg_sentence_length = round(random.uniform(12, 48), 1)
        repetition_rate = round(random.uniform(2, 15), 1)

        if is_ai_generated:
            recommendation = "⚠️ 该作业疑似由AI生成，建议核实"
            suggestions = [
                "📝 建议增加个人思考和具体例子",
                "💡 尝试加入'我认为'等个人化表达"
            ]
        else:
            recommendation = "✅ 作业由本人完成，继续保持"
            suggestions = [
                "👍 保持独立思考的好习惯",
                "📚 可以尝试挑战更难的题目"
            ]

        return Response.success({
            "ai_probability": ai_probability,
            "confidence": confidence,
            "is_ai_generated": is_ai_generated,
            "recommendation": recommendation,
            "text_length": file_size,
            "analysis_details": {
                "avg_sentence_length": avg_sentence_length,
                "repetition_rate": repetition_rate
            },
            "suggestions": suggestions
        }, "作业分析完成")

    except Exception as e:
        return Response.error(f"作业分析失败：{str(e)}", 500)


@tools_router.post("/voice/to-text")
async def voice_to_text(
        audio_base64: str,
        current_user: User = Depends(get_current_user)
):
    """语音转文字接口"""
    return Response.success({
        "text": "这是模拟的语音识别结果",
        "language": "zh-CN",
        "duration": 3.5
    }, "语音转文字成功")


@tools_router.get("/questions/generate")
async def generate_questions(
        knowledge_point: str,
        difficulty: str = "medium",
        count: int = 5,
        current_user: User = Depends(get_current_user)
):
    """智能组题生成接口"""
    questions = generate_smart_questions(knowledge_point, difficulty, count)
    return Response.success({
        "knowledge_point": knowledge_point,
        "difficulty": difficulty,
        "total": len(questions),
        "questions": questions
    }, "组题生成成功")


# ---------- 教师端路由 ----------
teacher_router = APIRouter(prefix="/api/teacher", tags=["教师端"])


@teacher_router.post("/create-class")
async def create_class(
        name: str,
        grade: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """教师创建班级"""
    if current_user.role != UserRole.ADMIN:
        return Response.error("只有教师可以创建班级", 403)

    import hashlib
    import time
    class_code = hashlib.md5(f"{current_user.id}{time.time()}".encode()).hexdigest()[:6].upper()

    new_class = Class(
        teacher_id=current_user.id,
        name=name,
        grade=grade,
        class_code=class_code
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return Response.success({
        "class_id": new_class.id,
        "name": new_class.name,
        "class_code": new_class.class_code
    }, "班级创建成功")


@teacher_router.get("/class-overview")
async def class_overview(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """教师端班级总览（含学生数、平均掌握度、平均正确率）"""
    if current_user.role != UserRole.ADMIN:
        return Response.error("只有教师可以查看班级", 403)

    classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
    result = []
    for cls in classes:
        student_ids = [
            cs.student_id for cs in
            db.query(ClassStudent).filter(ClassStudent.class_id == cls.id).all()
        ]
        student_count = len(student_ids)

        avg_mastery = 0.0
        avg_accuracy = 0.0
        if student_ids:
            kps = db.query(KnowledgePoint).filter(
                KnowledgePoint.user_id.in_(student_ids)
            ).all()
            if kps:
                # mastery_level 映射为数值：mastered=100, medium=60, critical=30
                level_map = {"mastered": 100, "medium": 60, "critical": 30}
                mastery_vals = [level_map.get(kp.mastery_level.value if hasattr(kp.mastery_level, 'value') else kp.mastery_level, 50) for kp in kps]
                acc_vals = [kp.accuracy or 0 for kp in kps]
                avg_mastery = round(sum(mastery_vals) / len(mastery_vals), 1)
                avg_accuracy = round(sum(acc_vals) / len(acc_vals), 1)

        result.append({
            "class_id": cls.id,
            "name": cls.name,
            "grade": cls.grade or "",
            "class_code": cls.class_code,
            "student_count": student_count,
            "avg_mastery": avg_mastery,
            "avg_accuracy": avg_accuracy
        })

    return Response.success(result, "班级列表获取成功")


@teacher_router.get("/class-students/{class_id}")
async def class_students(
        class_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """教师端查看班级学生列表"""
    if current_user.role != UserRole.ADMIN:
        return Response.error("只有教师可以查看学生", 403)

    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        return Response.error("班级不存在", 404)
    if cls.teacher_id != current_user.id:
        return Response.error("无权查看该班级", 403)

    student_relations = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id
    ).all()
    student_ids = [sr.student_id for sr in student_relations]

    students = []
    for sid in student_ids:
        user = db.query(User).filter(User.id == sid).first()
        if not user:
            continue
        kps = db.query(KnowledgePoint).filter(KnowledgePoint.user_id == sid).all()
        level_map = {"mastered": 100, "medium": 60, "critical": 30}
        if kps:
            mastery_vals = [level_map.get(kp.mastery_level.value if hasattr(kp.mastery_level, 'value') else kp.mastery_level, 50) for kp in kps]
            acc_vals = [kp.accuracy or 0 for kp in kps]
            mastery = round(sum(mastery_vals) / len(mastery_vals), 1)
            accuracy = round(sum(acc_vals) / len(acc_vals), 1)
        else:
            mastery = 0.0
            accuracy = 0.0
        weak_count = sum(1 for kp in kps if (kp.mastery_level.value if hasattr(kp.mastery_level, 'value') else kp.mastery_level) == "critical")
        status = "good" if mastery >= 60 else "warning"

        students.append({
            "id": user.id,
            "name": user.full_name or user.username,
            "mastery": mastery,
            "accuracy": accuracy,
            "weakCount": weak_count,
            "status": status
        })

    return Response.success({
        "class_id": cls.id,
        "name": cls.name,
        "grade": cls.grade or "",
        "class_code": cls.class_code,
        "student_count": len(students),
        "students": students
    }, "学生列表获取成功")


# ---------- 学生端路由 ----------
student_router = APIRouter(prefix="/api/student", tags=["学生端"])


@student_router.post("/join-class")
async def join_class(
        class_code: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """学生加入班级"""
    if current_user.role != UserRole.STUDENT:
        return Response.error("只有学生可以加入班级", 403)

    class_obj = db.query(Class).filter(Class.class_code == class_code).first()
    if not class_obj:
        return Response.error("班级代码无效", 404)

    existing = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_obj.id,
        ClassStudent.student_id == current_user.id
    ).first()
    if existing:
        return Response.error("已加入该班级", 400)

    class_student = ClassStudent(
        class_id=class_obj.id,
        student_id=current_user.id
    )
    db.add(class_student)
    db.commit()

    return Response.success({
        "class_name": class_obj.name,
        "teacher_id": class_obj.teacher_id
    }, "加入班级成功")


# ---------- 家长端路由 ----------
parent_router = APIRouter(prefix="/api/parent", tags=["家长端"])


@parent_router.post("/bind-child")
async def bind_child(
        child_code: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """家长绑定孩子"""
    if current_user.role != UserRole.PARENT:
        return Response.error("只有家长可以绑定孩子", 403)

    child = db.query(User).filter(User.username == child_code).first()
    if not child:
        return Response.error("孩子账号不存在", 404)

    if child.role != UserRole.STUDENT:
        return Response.error("只能绑定学生账号", 400)

    existing = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child.id
    ).first()
    if existing:
        return Response.error("已绑定该孩子", 400)

    parent_child = ParentChild(
        parent_id=current_user.id,
        child_id=child.id
    )
    db.add(parent_child)
    db.commit()

    return Response.success({
        "child_name": child.full_name or child.username
    }, "绑定成功")


@parent_router.get("/children")
async def get_children(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """家长获取已绑定的孩子列表"""
    if current_user.role != UserRole.PARENT:
        return Response.error("只有家长可以查看", 403)

    children = db.query(User).join(
        ParentChild, User.id == ParentChild.child_id
    ).filter(
        ParentChild.parent_id == current_user.id
    ).all()

    result = []
    for child in children:
        customer = db.query(Customer).filter(Customer.user_id == child.id).first()
        result.append({
            "id": child.id,
            "name": child.full_name or child.username,
            "mastery": customer.knowledge_mastery if customer else 0,
            "accuracy": customer.average_accuracy if customer else 0,
            "weak_count": customer.weak_knowledge_count if customer else 0
        })

    return Response.success(result)

# ---------- 客户档案路由 ----------
customer_router = APIRouter(prefix="/api/customer", tags=["客户档案"])


@customer_router.get("/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return Response.error("客户不存在", 404)
    return Response.success(CustomerInfo.from_orm(customer))


@customer_router.post("/")
async def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    if customer_data.user_id:
        user = db.query(User).filter(User.id == customer_data.user_id).first()
        if not user:
            return Response.error("关联用户不存在", 404)
    customer = Customer(**customer_data.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return Response.success(CustomerInfo.from_orm(customer), "客户创建成功")


@customer_router.put("/{customer_id}")
async def update_customer(customer_id: int, customer_data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return Response.error("客户不存在", 404)
    for key, value in customer_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return Response.success(CustomerInfo.from_orm(customer), "客户更新成功")


@customer_router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return Response.error("客户不存在", 404)
    db.delete(customer)
    db.commit()
    return Response.success(message="客户删除成功")


@customer_router.get("/user/{user_id}")
async def get_customer_by_user(user_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.user_id == user_id).first()
    if not customer:
        return Response.error("客户不存在", 404)
    return Response.success(CustomerInfo.from_orm(customer))


# ---------- 数据看板路由 ----------
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["数据看板"])


@dashboard_router.get("/stats/{customer_id}")
async def get_dashboard_stats(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return Response.error("客户不存在", 404)

    knowledge_points = db.query(KnowledgePoint).filter(KnowledgePoint.user_id == customer.user_id).all()
    records = db.query(LearningRecord).filter(LearningRecord.customer_id == customer_id).order_by(
        LearningRecord.date.desc()).all()

    knowledge_mastery = calculate_knowledge_mastery(knowledge_points)

    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_records = [r for r in records if r.date >= week_start]
    weekly_hours = sum(r.duration_minutes for r in week_records) / 60

    weak_count = sum(1 for kp in knowledge_points if kp.mastery_level.value in ["weak", "critical"])
    avg_accuracy = customer.average_accuracy

    current_week_hours = sum(r.duration_minutes for r in week_records)
    last_week_start = week_start - timedelta(days=7)
    last_week_records = [r for r in records if last_week_start <= r.date < week_start]
    last_week_hours = sum(r.duration_minutes for r in last_week_records)
    growth_rate = calculate_growth_rate(current_week_hours, last_week_hours)

    weekly_data = {"days": [], "hours": [], "accuracy": []}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_records = [r for r in records if r.date.date() == day.date()]
        day_hours = sum(r.duration_minutes for r in day_records) / 60
        day_accuracy = sum(r.accuracy for r in day_records) / len(day_records) if day_records else 0
        weekly_data["days"].append(day.strftime("%Y-%m-%d"))
        weekly_data["hours"].append(round(day_hours, 1))
        weekly_data["accuracy"].append(round(day_accuracy, 1))

    stats = DashboardStats(
        knowledge_mastery=round(knowledge_mastery, 1),
        weekly_learning_hours=round(weekly_hours, 1),
        weak_knowledge_count=weak_count,
        average_accuracy=round(avg_accuracy, 1),
        weekly_growth_rate=round(growth_rate, 1),
        weekly_data=weekly_data
    )
    return Response.success(stats.dict())


# ===================== 1.知识图谱模块 =====================
knowledge_router = APIRouter(prefix="/api/knowledge", tags=["知识图谱"])


@knowledge_router.get("/user/{user_id}")
async def get_knowledge_points(user_id: int, db: Session = Depends(get_db)):
    points = db.query(KnowledgePoint).filter(KnowledgePoint.user_id == user_id).all()
    return Response.success([KnowledgePointInfo.from_orm(p) for p in points])


@knowledge_router.post("/")
async def create_knowledge_point(kp_data: KnowledgePointCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == kp_data.user_id).first()
    if not user:
        return Response.error(message="用户不存在", code=404)
    kp = KnowledgePoint(**kp_data.dict())
    db.add(kp)
    db.commit()
    db.refresh(kp)
    return Response.success(KnowledgePointInfo.from_orm(kp), message="知识点创建成功")


@knowledge_router.put("/{kp_id}")
async def update_knowledge_point(kp_id: int, kp_data: KnowledgePointUpdate, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        return Response.error("知识点不存在", 404)
    for key, value in kp_data.dict(exclude_unset=True).items():
        setattr(kp, key, value)
    db.commit()
    db.refresh(kp)
    return Response.success(KnowledgePointInfo.from_orm(kp), "知识点更新成功")


@knowledge_router.post("/{kp_id}/record-practice")
async def record_practice(kp_id: int, is_correct: bool, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        return Response.error("知识点不存在", 404)

    kp.total_count += 1
    if is_correct:
        kp.correct_count += 1
        kp.consecutive_low_count = 0
        kp.consecutive_high_count += 1
    else:
        kp.consecutive_low_count += 1
        kp.consecutive_high_count = 0

    kp.accuracy = round((kp.correct_count / kp.total_count) * 100, 2)
    kp.mastery_level = calculate_mastery_level(kp.accuracy)

    if check_weak_alert(kp.consecutive_low_count):
        kp.is_alert = True
        alert = Alert(
            user_id=kp.user_id,
            knowledge_point_id=kp.id,
            alert_type=AlertType.WEAK,
            title=f"知识点 '{kp.name}' 连续3次正确率低于50%",
            description=f"当前正确率: {kp.accuracy}%, 连续错误次数: {kp.consecutive_low_count}"
        )
        db.add(alert)

    if check_mastered_condition(kp.consecutive_high_count):
        kp.mastery_level = MasteryLevel.MASTERED

    kp.last_review_date = datetime.utcnow()
    db.commit()
    db.refresh(kp)

    return Response.success({
        "knowledge_point": KnowledgePointInfo.from_orm(kp),
        "is_alert": kp.is_alert,
        "mastery_level": kp.mastery_level.value
    }, "练习记录已更新")


# 【新增】知识图谱可视化思维导图接口
@knowledge_router.get("/mindmap/{user_id}")
async def get_knowledge_mindmap(user_id: int, db: Session = Depends(get_db)):
    kp_list = db.query(KnowledgePoint).filter(KnowledgePoint.user_id == user_id).all()
    mindmap = generate_mindmap_data(kp_list)
    return Response.success(mindmap, "知识图谱思维导图数据")


# 修复你截断的衰减风险接口
@knowledge_router.get("/{kp_id}/decay-risk")
async def check_decay_risk(kp_id: int, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        return Response.error("知识点不存在", 404)
    has_risk = check_decay_risk(kp.last_review_date)
    # 生成遗忘预警
    if has_risk:
        exist_alert = db.query(Alert).filter(
            Alert.knowledge_point_id == kp.id,
            Alert.alert_type == AlertType.DECAY,
            Alert.is_read == False
        ).first()
        if not exist_alert:
            decay_alert = Alert(
                user_id=kp.user_id,
                knowledge_point_id=kp.id,
                alert_type=AlertType.DECAY,
                title=f"知识点「{kp.name}」存在遗忘风险",
                description=f"距离上次复习已超过5天，建议及时巩固复习"
            )
            db.add(decay_alert)
            db.commit()
    return Response.success({
        "kp_id": kp.id,
        "kp_name": kp.name,
        "last_review": kp.last_review_date.strftime("%Y-%m-%d"),
        "decay_risk": has_risk
    })


# ===================== 2.学习任务模块 =====================
task_router = APIRouter(prefix="/api/task", tags=["学习任务"])


# 创建任务
@task_router.post("/")
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(task_data.user_id)
    if not user:
        return Response.error("用户不存在", 404)
    task = Task(**task_data.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return Response.success(TaskInfo.from_orm(task), "任务创建成功")


# 获取用户全部任务
@task_router.get("/user/{user_id}")
async def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    task_list = db.query(Task).filter(Task.user_id == user_id).order_by(Task.priority.desc()).all()
    return Response.success([TaskInfo.from_orm(t) for t in task_list])


# 单任务详情
@task_router.get("/{task_id}")
async def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        return Response.error("任务不存在", 404)
    return Response.success(TaskInfo.from_orm(task))


# 更新任务
@task_router.put("/{task_id}")
async def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        return Response.error("任务不存在", 404)
    for k, v in task_data.dict(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return Response.success(TaskInfo.from_orm(task), "任务更新完成")


# 删除任务
@task_router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        return Response.error("任务不存在", 404)
    db.delete(task)
    db.commit()
    return Response.success(message="任务已删除")


# 获取任务进度统计
@task_router.get("/progress/{user_id}")
async def get_task_progress(user_id: int, db: Session = Depends(get_db)):
    all_tasks = db.query(Task).filter(Task.user_id == user_id).all()
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.status == "completed")
    pending = sum(1 for t in all_tasks if t.status == "pending")
    doing = sum(1 for t in all_tasks if t.status == "doing")
    progress = TaskProgress(
        total_tasks=total,
        completed_tasks=completed,
        progress_percentage=round(completed / total * 100, 2) if total > 0 else 0,
        pending_tasks=pending,
        doing_tasks=doing
    )
    return Response.success(progress.dict())


# ===================== 3.AI对话模块 =====================
chat_router = APIRouter(prefix="/api/chat", tags=["AI对话"])


# 发送消息
@chat_router.post("/send")
async def send_chat_msg(msg: ChatMessageCreate, current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    new_msg = ChatMessage(
        user_id=current_user.id,
        session_id=msg.session_id,
        message_type=msg.message_type,
        content=msg.content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    # AI自动回复模拟
    reply_data = ChatMessage(
        user_id=current_user.id,
        session_id=msg.session_id,
        message_type=MessageType.SYSTEM,
        content=f"AI已收到你的提问：{msg.content}，正在为你分析学情知识点",
        chart_data=generate_chart_data_for_taylor([0, 1, 2, 3])
    )
    db.add(reply_data)
    db.commit()
    return Response.success({
        "user_msg": ChatMessageInfo.from_orm(new_msg),
        "ai_reply": ChatMessageInfo.from_orm(reply_data)
    })


# 获取会话历史
@chat_router.get("/history/{user_id}/{session_id}")
async def get_chat_history(user_id: int, session_id: str, db: Session = Depends(get_db)):
    history = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id,
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return Response.success([ChatMessageInfo.from_orm(m) for m in history])


# ===================== 4.工具能力模块 =====================
tool_router = APIRouter(prefix="/api/tools", tags=["工具能力"])


# 智能出题工具
@tool_router.get("/generate-questions")
async def gen_questions(knowledge: str, difficulty: str = "medium", count: int = 5):
    data = generate_smart_questions(knowledge, difficulty, count)
    return Response.success(data, "智能练习题生成完成")


# 泰勒展开可视化工具
@tool_router.get("/taylor-plot")
async def taylor_chart(x_start: float = 0, x_end: float = 3, step: float = 0.5, terms: int = 5):
    x_list = []
    cur = x_start
    while cur <= x_end:
        x_list.append(round(cur, 2))
        cur += step
    chart = generate_chart_data_for_taylor(x_list, terms)
    return Response.success(chart, "泰勒展开拟合图表数据")


# ===================== 5.数据预警模块 =====================
alert_router = APIRouter(prefix="/api/alert", tags=["数据预警"])


# 获取用户全部预警
@alert_router.get("/user/{user_id}")
async def get_user_alerts(user_id: int, db: Session = Depends(get_db), read: Optional[bool] = None):
    query = db.query(Alert).filter(Alert.user_id == user_id).order_by(Alert.created_at.desc())
    if read is not None:
        query = query.filter(Alert.is_read == read)
    alert_list = query.all()
    return Response.success([AlertInfo.from_orm(a) for a in alert_list])


# 标记预警已读
@alert_router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).get(alert_id)
    if not alert:
        return Response.error("预警记录不存在", 404)
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return Response.success(AlertInfo.from_orm(alert), "预警已标记为已读")


# 一键全部已读
@alert_router.put("/user/{user_id}/all-read")
async def all_alert_read(user_id: int, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.user_id == user_id, Alert.is_read == False).all()
    for a in alerts:
        a.is_read = True
    db.commit()
    return Response.success(message=f"共{len(alerts)}条预警标记已读")


# ===================== 6.报表导出模块 =====================
export_router = APIRouter(prefix="/api/export", tags=["报表导出"])
from fastapi.responses import StreamingResponse
import io
import csv


@export_router.get("/learning-report/{customer_id}")
async def export_learning_report(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).get(customer_id)
    if not customer:
        return Response.error("客户不存在", 404)
    records = db.query(LearningRecord).filter(LearningRecord.customer_id == customer_id).all()
    kp_list = db.query(KnowledgePoint).filter(KnowledgePoint.user_id == customer.user_id).all()

    # 生成CSV内存流
    output = io.StringIO()
    writer = csv.writer(output)
    # 表头
    writer.writerow(
        ["姓名", "年级", "总学习时长(小时)", "平均正确率", "薄弱知识点数量", "日期", "科目", "练习时长(分钟)",
         "做题总数", "正确数", "正确率"])
    # 数据行
    for r in records:
        writer.writerow([
            customer.name, customer.grade, customer.total_learning_hours,
            customer.average_accuracy, customer.weak_knowledge_count,
            r.date.strftime("%Y-%m-%d"), r.subject.value, r.duration_minutes,
            r.total_count, r.correct_count, r.accuracy
        ])
    # 知识点附表
    writer.writerow([])
    writer.writerow(["知识点名称", "科目", "掌握程度", "正确率", "是否预警"])
    for kp in kp_list:
        writer.writerow([kp.name, kp.subject.value, kp.mastery_level.value, kp.accuracy, kp.is_alert])

    output.seek(0)
    stream = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    filename = f"学情报表_{customer.name}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# ========== 统一注册所有路由 ==========
app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(dashboard_router)
app.include_router(knowledge_router)
app.include_router(task_router)
app.include_router(chat_router)
app.include_router(tool_router)
app.include_router(alert_router)
app.include_router(export_router)
app.include_router(ai_router)
app.include_router(tools_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(parent_router)


# ========== 健康检查 ==========
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")


@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "code": 200,
        "message": f"{app.title} v{app.version} 运行正常",
        "data": {"timestamp": datetime.utcnow().isoformat()}
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ========= 前端静态资源(生产部署:前后端同源,由后端托管 dist) =========
assets_dir = os.path.join(FRONTEND_DIST, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# ========= 启动入口 =========
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "4:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )