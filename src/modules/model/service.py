import json
import time
import asyncio
from typing import AsyncGenerator
import redis.asyncio as redis
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import BizException
from src.core.base_schema import PageResult
from src.core.deps import PageParams
from src.infra.redis_cache import _redis_client
from src.modules.model.model import LLMModel
from src.modules.model.repository import ModelRepository
from src.modules.model.schema import ModelCreate, ModelUpdate, ModelRead, ChatRequest
from src.modules.provider.repository import ProviderRepository


class ModelService:
    SESSION_KEY_PREFIX = "chat:memory:"
    SESSION_TTL_SECONDS = 1800  # 30分钟无交互自动释放短期记忆
    MAX_HISTORY_MESSAGES = 10   # 滑动窗口保留最多 10 条（5轮）对话

    def __init__(self, db: AsyncSession, redis_client: redis.Redis | None = None):
        self.repo = ModelRepository(db)
        self.provider_repo = ProviderRepository(db)
        self.redis = redis_client or _redis_client

    def _to_read(self, model: LLMModel) -> ModelRead:
        """将 ORM 对象转换为 Read Schema（处理关联字段和格式转换）"""
        return ModelRead(
            id=model.id,
            name=model.name,
            model_id=model.model_id,
            provider_id=model.provider_id,
            provider_name=model.provider.name if model.provider else "",
            capabilities=model.capabilities.split(",") if model.capabilities else [],
            context_length=model.context_length,
            status=model.status,
            input_price=float(model.input_price),
            output_price=float(model.output_price),
            currency=model.currency,
            is_default=model.is_default,
            description=model.description,
        )

    async def create_model(self, data: ModelCreate) -> ModelRead:
        # 1. 检查 model_id 是否已存在
        existing = await self.repo.get_by_model_id(data.model_id)
        if existing:
            raise BizException(code=41001, message=f"模型 '{data.model_id}' 已存在")

        # 2. 检查供应商是否存在
        provider = await self.provider_repo.get_by_id(data.provider_id)
        if not provider:
            raise BizException(code=41002, message="供应商不存在")

        # 3. 如果设为默认，先取消其他默认
        if data.is_default:
            current_default = await self.repo.get_default_model()
            if current_default:
                current_default.is_default = False
                await self.repo.update(current_default)

        # 4. 创建模型
        model = LLMModel(
            name=data.name,
            model_id=data.model_id,
            provider_id=data.provider_id,
            capabilities=",".join(data.capabilities) if data.capabilities else None,
            context_length=data.context_length,
            input_price=data.input_price,
            output_price=data.output_price,
            currency=data.currency,
            is_default=data.is_default,
            description=data.description,
        )
        model = await self.repo.create(model)
        return self._to_read(model)

    async def get_model(self, model_id: int) -> ModelRead:
        model = await self.repo.get_by_id(model_id)
        if not model:
            raise BizException(code=41003, message="模型不存在")
        return self._to_read(model)

    async def list_models(
        self, params: PageParams, provider_id: int | None = None
    ) -> PageResult[ModelRead]:
        """分页查询模型列表，支持按供应商筛选"""
        if provider_id:
            # 按供应商筛选时，不走通用分页（数据量通常较少）
            models = await self.repo.get_by_provider(provider_id)
            items = [self._to_read(m) for m in models]
            return PageResult(
                items=items,
                total=len(items),
                page=1,
                page_size=len(items),
            )
        else:
            items, total = await self.repo.search_page(
                offset=params.offset,
                limit=params.page_size,
                keyword=params.keyword,
            )
            return PageResult(
                items=[self._to_read(m) for m in items],
                total=total,
                page=params.page,
                page_size=params.page_size,
            )

    async def update_model(self, model_id: int, data: ModelUpdate) -> ModelRead:
        model = await self.repo.get_by_id(model_id)
        if not model:
            raise BizException(code=41003, message="模型不存在")

        if data.name is not None:
            model.name = data.name
        if data.capabilities is not None:
            model.capabilities = ",".join(data.capabilities) if data.capabilities else None
        if data.context_length is not None:
            model.context_length = data.context_length
        if data.status is not None:
            model.status = data.status
        if data.input_price is not None:
            model.input_price = data.input_price
        if data.output_price is not None:
            model.output_price = data.output_price
        if data.currency is not None:
            model.currency = data.currency
        if data.is_default is not None:
            if data.is_default:
                current_default = await self.repo.get_default_model()
                if current_default and current_default.id != model_id:
                    current_default.is_default = False
                    await self.repo.update(current_default)
            model.is_default = data.is_default
        if data.description is not None:
            model.description = data.description

        model = await self.repo.update(model)
        return self._to_read(model)

    async def delete_model(self, model_id: int) -> None:
        model = await self.repo.get_by_id(model_id)
        if not model:
            raise BizException(code=41003, message="模型不存在")
        await self.repo.delete_by_id(model_id)

    async def _resolve_model_and_provider(self, model_id: int | str | None) -> tuple[LLMModel | None, any]:
        """解析模型及其所属供应商"""
        model = None
        if model_id is not None:
            if isinstance(model_id, int) or (isinstance(model_id, str) and model_id.isdigit()):
                model = await self.repo.get_by_id(int(model_id))
            if not model and isinstance(model_id, str):
                model = await self.repo.get_by_model_id(model_id)

        if not model:
            model = await self.repo.get_default_model()

        if not model:
            all_models = await self.repo.get_all(limit=1)
            if all_models:
                model = all_models[0]

        if not model:
            return None, None

        provider = model.provider
        if not provider and model.provider_id:
            provider = await self.provider_repo.get_by_id(model.provider_id)

        return model, provider

    async def get_conversation_history(self, conversation_id: int | str) -> list[dict]:
        """从 Redis 读取短期会话历史"""
        if not self.redis:
            return []
        try:
            data = await self.redis.get(f"{self.SESSION_KEY_PREFIX}{conversation_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"从 Redis 读取会话历史失败: {e}")
        return []

    async def save_conversation_history(self, conversation_id: int | str, messages: list[dict]) -> None:
        """保存会话历史到 Redis，应用滑动窗口并刷新 TTL"""
        if not self.redis:
            return
        try:
            trimmed = messages[-self.MAX_HISTORY_MESSAGES:]
            await self.redis.set(
                f"{self.SESSION_KEY_PREFIX}{conversation_id}",
                json.dumps(trimmed, ensure_ascii=False),
                ex=self.SESSION_TTL_SECONDS
            )
        except Exception as e:
            logger.warning(f"保存会话历史到 Redis 失败: {e}")

    async def clear_conversation_history(self, conversation_id: int | str) -> None:
        """从 Redis 中清理短期会话历史"""
        if not self.redis:
            return
        try:
            await self.redis.delete(f"{self.SESSION_KEY_PREFIX}{conversation_id}")
            logger.info(f"已清理会话短期记忆: {conversation_id}")
        except Exception as e:
            logger.warning(f"清理 Redis 会话历史失败: {e}")

    def _format_messages(self, request: ChatRequest) -> tuple[list[dict], str]:
        """提取并标准化对话消息，同时返回用户最新的问题文本"""
        formatted = []
        last_user_message = ""

        if request.messages:
            for m in request.messages:
                if isinstance(m, dict):
                    role = m.get("role", "user")
                    content = m.get("content", "")
                    formatted.append({"role": role, "content": content})
                    if role == "user":
                        last_user_message = content
                elif hasattr(m, "role") and hasattr(m, "content"):
                    formatted.append({"role": m.role, "content": m.content})
                    if m.role == "user":
                        last_user_message = m.content
        elif request.message:
            formatted.append({"role": "user", "content": request.message})
            last_user_message = request.message
        else:
            formatted.append({"role": "user", "content": "你好"})
            last_user_message = "你好"

        return formatted, last_user_message

    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        SSE 流式对话生成器（支持 Redis 短期记忆滑动窗口）：
        1. 遵循 OpenAI SSE 协议规范 (data: {"choices": [{"delta": {"content": "..."}}], "conversation_id": ...}\\n\\n)
        2. 流式传输结束输出 data: [DONE]\\n\\n
        3. 对测试密钥/未配置密钥提供即时友好的模拟输出，对真实密钥调用 upstream LLM
        """
        conv_id = request.conversation_id or int(time.time() * 1000)
        formatted_messages, user_message = self._format_messages(request)

        # 1. 查询模型与供应商
        model, provider = await self._resolve_model_and_provider(request.model_id)
        if not model:
            err_payload = {
                "choices": [{"delta": {"content": "系统未配置任何可用模型，请先在模型管理中添加模型。"}}],
                "conversation_id": conv_id,
            }
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 2. 组装短期记忆（优先使用 Redis 会话历史，滑动窗口截断）
        if request.messages and len(request.messages) > 1:
            prompt_messages = formatted_messages
        else:
            history = await self.get_conversation_history(conv_id)
            prompt_messages = history + [{"role": "user", "content": user_message}]
        prompt_messages = prompt_messages[-self.MAX_HISTORY_MESSAGES:]

        provider_name = provider.name if provider else "未指定供应商"
        endpoint = provider.endpoint.rstrip("/") if provider and provider.endpoint else ""
        api_key = provider.api_key.strip() if provider and provider.api_key else ""

        # 3. 开发者测试/未配置真实 API Key 场景的模拟流式输出
        is_test_key = not api_key or api_key.startswith("sk-test")
        if is_test_key:
            logger.info(f"模型测试使用测试密钥/占位模式: model={model.model_id}, provider={provider_name}")
            history_hint = f"- 本次会话已记忆上下文：共 {len(prompt_messages) - 1} 条历史记录\n" if len(prompt_messages) > 1 else ""
            mock_text = (
                f"【FastAPI + SSE 连接成功】\n\n"
                f"- 当前测试模型：`{model.name}` (`{model.model_id}`)\n"
                f"- 所属供应商：`{provider_name}`\n"
                f"- API 端点：`{endpoint or '默认端点'}`\n"
                f"{history_hint}"
                f"- 收到您的提问：\"{user_message}\"\n\n"
                f"[提示] 当前供应商 API Key 为占位测试密钥（`{api_key or '未填写'}`），"
                f"SSE 流式链路畅通。如需调用真实大模型，请前往「模型供应商」页面配置有效的 API Key 与 API Endpoint。"
            )
            # 模拟打字机分块推送
            chunk_size = 4
            for i in range(0, len(mock_text), chunk_size):
                chunk = mock_text[i:i + chunk_size]
                payload = {
                    "choices": [{"delta": {"content": chunk}}],
                    "conversation_id": conv_id,
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.02)

            # 保存本轮对话到 Redis 短期记忆
            await self.save_conversation_history(
                conv_id,
                prompt_messages + [{"role": "assistant", "content": mock_text}]
            )

            yield "data: [DONE]\n\n"
            return

        # 4. 真实模型流式调用（基于 AsyncOpenAI 异步迭代器）
        try:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=endpoint if endpoint else None,
            )
            stream = await client.chat.completions.create(
                model=model.model_id,
                messages=prompt_messages,
                stream=True,
                temperature=request.temperature if request.temperature is not None else 0.7,
                max_tokens=request.max_tokens,
            )
            full_assistant_reply = ""
            async for chunk in stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = choice.delta
                delta_dict = {}
                if delta.content:
                    delta_dict["content"] = delta.content
                    full_assistant_reply += delta.content
                if getattr(delta, "tool_calls", None):
                    delta_dict["tool_calls"] = [
                        tc.model_dump() if hasattr(tc, "model_dump") else dict(tc)
                        for tc in delta.tool_calls
                    ]

                if delta_dict:
                    payload = {
                        "choices": [{"delta": delta_dict}],
                        "conversation_id": conv_id,
                    }
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            # 保存本轮对话至 Redis 短期记忆
            if full_assistant_reply:
                await self.save_conversation_history(
                    conv_id,
                    prompt_messages + [{"role": "assistant", "content": full_assistant_reply}]
                )

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"调用模型失败: {e}")
            err_payload = {
                "choices": [{"delta": {"content": f"\n\n[模型调用异常]: {str(e)}"}}],
                "conversation_id": conv_id,
                "error": str(e),
            }
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    async def chat(self, request: ChatRequest) -> dict:
        """非流式对话回退"""
        conv_id = request.conversation_id or int(time.time() * 1000)
        formatted_messages, user_message = self._format_messages(request)
        model, provider = await self._resolve_model_and_provider(request.model_id)

        if not model:
            raise BizException(code=41003, message="模型不存在或未配置")

        if request.messages and len(request.messages) > 1:
            prompt_messages = formatted_messages
        else:
            history = await self.get_conversation_history(conv_id)
            prompt_messages = history + [{"role": "user", "content": user_message}]
        prompt_messages = prompt_messages[-self.MAX_HISTORY_MESSAGES:]

        endpoint = provider.endpoint.rstrip("/") if provider and provider.endpoint else ""
        api_key = provider.api_key.strip() if provider and provider.api_key else ""

        if not api_key or api_key.startswith("sk-test"):
            reply = f"【系统测试响应】已收到问题：{user_message}。当前为占位测试模式。"
            await self.save_conversation_history(
                conv_id,
                prompt_messages + [{"role": "assistant", "content": reply}]
            )
            return {
                "conversation_id": conv_id,
                "choices": [{"message": {"role": "assistant", "content": reply}}],
            }

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=endpoint if endpoint else None,
        )
        response = await client.chat.completions.create(
            model=model.model_id,
            messages=prompt_messages,
            stream=False,
            temperature=request.temperature if request.temperature is not None else 0.7,
            max_tokens=request.max_tokens,
        )
        reply = response.choices[0].message.content or ""
        await self.save_conversation_history(
            conv_id,
            prompt_messages + [{"role": "assistant", "content": reply}]
        )
        return {
            "conversation_id": conv_id,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": reply,
                    }
                }
            ],
        }
