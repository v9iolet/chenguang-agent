

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.infra.database import get_db
from src.infra.redis_cache import get_redis_client
from src.core.base_schema import ResponseSchema, PageResult
from src.core.deps import PageParams
from src.modules.model.schema import ModelCreate, ModelUpdate, ModelRead, ChatRequest
from src.modules.model.service import ModelService

router = APIRouter(prefix="/models", tags=["模型管理"])
chat_router = APIRouter(tags=["模型测试与对话"])


def get_model_service(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> ModelService:
    return ModelService(db, redis_client)


@router.post("", response_model=ResponseSchema[ModelRead], summary="添加模型")
async def create_model(
    data: ModelCreate,
    svc: ModelService = Depends(get_model_service),
):
    result = await svc.create_model(data)
    return ResponseSchema(data=result)


@router.get("", response_model=ResponseSchema[PageResult[ModelRead]], summary="模型列表")
async def list_models(
    params: PageParams = Depends(),
    provider_id: int | None = Query(None, description="按供应商筛选"),
    svc: ModelService = Depends(get_model_service),
):
    page_result = await svc.list_models(params, provider_id)
    return ResponseSchema(data=page_result)


@router.get("/{model_id}", response_model=ResponseSchema[ModelRead], summary="模型详情")
async def get_model(
    model_id: int,
    svc: ModelService = Depends(get_model_service),
):
    result = await svc.get_model(model_id)
    return ResponseSchema(data=result)


@router.put("/{model_id}", response_model=ResponseSchema[ModelRead], summary="更新模型")
async def update_model(
    model_id: int,
    data: ModelUpdate,
    svc: ModelService = Depends(get_model_service),
):
    result = await svc.update_model(model_id, data)
    return ResponseSchema(data=result)


@router.delete("/{model_id}", response_model=ResponseSchema, summary="删除模型")
async def delete_model(
    model_id: int,
    svc: ModelService = Depends(get_model_service),
):
    await svc.delete_model(model_id)
    return ResponseSchema(message="删除成功")

@router.post("/chat/stream", summary="模型对话测试(流式SSE)")
@chat_router.post("/chat/stream", summary="模型对话测试(流式SSE)")
async def chat_stream(
    request: ChatRequest,
    svc: ModelService = Depends(get_model_service),
):
    """
    模型对话测试接口：
    - 前端模型测试页调用此接口（POST /api/v1/chat/stream 或 /api/v1/models/chat/stream）
    - 返回标准 Server-Sent Events (SSE) 流式响应
    - 当 request.stream 为 False 时回退到非流式 JSON 响应
    """
    if not request.stream:
        result = await svc.chat(request)
        return ResponseSchema(data=result)

    return StreamingResponse(
        svc.chat_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/chat/conversation/{conversation_id}", response_model=ResponseSchema, summary="清空会话短期记忆")
@chat_router.delete("/chat/conversation/{conversation_id}", response_model=ResponseSchema, summary="清空会话短期记忆")
async def clear_conversation(
    conversation_id: str,
    svc: ModelService = Depends(get_model_service),
):
    """主动清理 Redis 中暂存的指定会话短期上下文记忆"""
    await svc.clear_conversation_history(conversation_id)
    return ResponseSchema(message="会话记忆已成功清空")
