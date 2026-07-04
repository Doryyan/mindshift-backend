from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TrainingEvaluateRequest(BaseModel):
    training_type: str = Field(description="sensory/belief/anchor/language/quiz")
    input_data: dict


class TrainingRecordResponse(BaseModel):
    id: str
    training_type: str
    input_data: dict
    ai_result: dict | None = None
    overall_score: float | None = None
    time_spent_seconds: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BeliefMineRequest(BaseModel):
    user_input: str = Field(
        description="用户描述的情况或困扰", min_length=10, json_schema_extra={"example": "我觉得自己永远做不好公开演讲"}
    )


class MeditationGenerateRequest(BaseModel):
    state: str = Field(description="用户当前情绪状态，如：焦虑、疲惫、迷茫", json_schema_extra={"example": "焦虑"})
    focus: str = Field(description="NLP聚焦领域，如：信念转化、次感元调整、心锚安装", json_schema_extra={"example": "信念转化"})


class DreamAnalyzeRequest(BaseModel):
    dream_text: str = Field(
        description="梦境描述文本", min_length=20, json_schema_extra={"example": "我梦见自己在一条很长的走廊里跑，尽头有一扇门但怎么也跑不到"}
    )
