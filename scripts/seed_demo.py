import json
from datetime import date, timedelta

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.user import User
from app.models.daily_log import DailyLog
from app.models.goal import Goal


def main():
    init_db()
    db = SessionLocal()

    user = User(name="demo_user")
    db.add(user)
    db.commit()
    db.refresh(user)

    log = DailyLog(
        user_id=user.id,
        log_date=date.today(),
        mood=6,
        energy=5,
        sleep_hours=6.5,
        behaviors_json=json.dumps(
            [
                "上午学习 Agent 基础 40 分钟",
                "下午刷短视频 1.5 小时",
                "晚上整理项目想法",
            ],
            ensure_ascii=False,
        ),
        wins_json=json.dumps(["开始动手做项目，而不是只看教程"], ensure_ascii=False),
        problems_json=json.dumps(["下午注意力断掉", "目标有点大，不知道先写什么"], ensure_ascii=False),
        notes="想做一个长期陪伴型 AI 自我成长教练。",
    )
    db.add(log)

    goal = Goal(
        user_id=user.id,
        title="连续 3 天记录每日行为",
        why="让 Agent 有足够数据分析我",
        metric="每天至少记录 3 条行为 + 1 个卡点",
        target_date=date.today() + timedelta(days=3),
    )
    db.add(goal)

    db.commit()
    print(f"Demo user created. user_id={user.id}")
    db.close()


if __name__ == "__main__":
    main()
