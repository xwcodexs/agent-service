from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ChatThread


class ChatThreadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 没有 async，没有 return，干干净净
    async def add(self, chat_thread: ChatThread):
        self.session.add(chat_thread)

    async def list_by_user(self, chat_thread_id: int)-> list[ChatThread]:
        result = await self.session.scalars(
            select(ChatThread)
            .where(ChatThread.user_id == chat_thread_id)
            .order_by(
                ChatThread.updated_at.desc(),
                ChatThread.created_at.desc()
                      )
        )
        return list(result.all())

    async def find_owned(
            self,
            thread_id: UUID,
            user_id: int,
    ) -> ChatThread | None:
        return await self.session.scalar(
            select(ChatThread).where(
                ChatThread.id == thread_id,
                ChatThread.user_id == user_id,
            )
        )
    async def delete_thread(self, thread: ChatThread)-> None:
        await self.session.delete(thread)


