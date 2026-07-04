from __future__ import annotations

from app.schemas.auth import Token, TokenPayload, UserRegister, UserLogin, UserResponse, RefreshToken
from app.schemas.course import LessonResponse, CourseListItem, CourseDetail
from app.schemas.training import TrainingEvaluateRequest, TrainingRecordResponse
from app.schemas.roleplay import (
    ScenarioListItem,
    ScenarioDetail,
    DialogueStartRequest,
    DialogueChatRequest,
    DialogueSessionResponse,
    DialogueHistoryResponse,
)
from app.schemas.community import (
    PostCreate,
    PostListItem,
    CommentCreate,
    CommentResponse,
    PostDetail,
    CheckinRequest,
    CheckinStatus,
)
