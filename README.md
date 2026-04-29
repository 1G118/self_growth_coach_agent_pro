# AI Self Growth Coach Agent Pro

这是一个基于 FastAPI 的自我成长教练 Agent 后端项目，支持每日记录、每日复盘、每周复盘、长期记忆和目标追踪。

当前版本已经把原先只支持 OpenAI 的调用方式改成了可扩展的 LLM 抽象层。业务代码只依赖统一的 `call_llm_json(...)` 接口，不再直接绑定某一家模型厂商。

## 当前支持的 LLM Provider

- `openai`
  - 使用 OpenAI Python SDK 的 Responses API
  - 也可用于兼容该接口的网关，只要它支持 Responses API
- `openai_compatible`
  - 使用通用 `chat/completions` 协议
  - 适合大多数 OpenAI-compatible 平台或中转网关
- `anthropic`
  - 使用 Anthropic Messages API
- `gemini`
  - 使用 Google Gemini `generateContent` API

后续如果要接更多厂商，只需要在 `app/llm/providers.py` 新增一个 provider，并在 `app/llm/factory.py` 注册。

## 项目结构

```txt
self_growth_coach_agent_pro/
  app/
    core/
      config.py
    db/
    llm/
      base.py
      factory.py
      providers.py
    models/
    prompts/
    routes/
    schemas/
    services/
      llm_service.py
      reflection_service.py
      weekly_service.py
    main.py
  scripts/
  requirements.txt
  .env.example
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

先复制环境变量模板：

```bash
cp .env.example .env
```

然后按你要接入的厂商填写。

### 1. OpenAI

```env
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_key
LLM_MODEL=gpt-5.2
DATABASE_URL=sqlite:///./coach_agent.db
```

### 2. OpenAI-Compatible 网关

```env
LLM_PROVIDER=openai_compatible
LLM_API_KEY=your_gateway_key
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://your-gateway.example.com/v1
DATABASE_URL=sqlite:///./coach_agent.db
```

### 3. Anthropic

```env
LLM_PROVIDER=anthropic
LLM_API_KEY=your_anthropic_key
LLM_MODEL=claude-3-5-sonnet-latest
LLM_API_VERSION=2023-06-01
DATABASE_URL=sqlite:///./coach_agent.db
```

### 4. Gemini

```env
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_key
LLM_MODEL=gemini-1.5-pro
DATABASE_URL=sqlite:///./coach_agent.db
```

## 启动

```bash
uvicorn app.main:app --reload
```

打开：

```txt
http://127.0.0.1:8000/docs
```

## Agent 调用链

1. 用户写入每日行为日志
2. `reflection_service` / `weekly_service` 组装业务上下文
3. `llm_service` 调用统一 LLM 抽象层
4. provider 负责把统一请求转成具体厂商 API
5. 返回 JSON 结构后继续更新记忆、目标和复盘结果

## 说明

- 业务层不应该再直接 import OpenAI SDK。
- 统一配置项优先使用 `LLM_*`。
- 为兼容旧配置，`OPENAI_API_KEY` 和 `OPENAI_MODEL` 仍可继续使用。
