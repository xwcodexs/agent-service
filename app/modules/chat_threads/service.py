from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from .exceptions import ChatThreadNotFoundError
from .models import ChatThread
from .respository import ChatThreadRepository


class ChatThreadService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ChatThreadRepository(session)

    async def add(self, user_id: int , title: str):
        # 用上下文管理，开启事务，运行完成，自动commit，出现异常，自动rollback
        async with self.session.begin():
            # 创建对象，对象 映射 到数据库 一条数据
            chat_thread = ChatThread(user_id = user_id, title = title)
            # 新增对象，就是插入一条数据
            await self.repository.add(chat_thread)

            return chat_thread
    async def list_by_user(self, user_id: int)-> list[ChatThread]:
        return await self.repository.list_by_user(user_id)
    async def rename(self, thread_id: UUID,user_id: int,title:str) -> ChatThread:
        async with self.session.begin():
            # 1.根据thread_id和user_id查询，判断是否匹配
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                # 为None，说明不存在，或者不属于当前用户，抛出异常
                # raise: 就是指扔出去一个异常，代码会立刻终止，结束运行，把异常扔给调用者
                raise ChatThreadNotFoundError

            # 2.查询后直接修改字段，触发数据库更新
            thread.title = title

            # 3.刷新数据，重新从数据库中查出最新值
            await self.session.flush()
            await self.session.refresh(thread)

        return thread
    async def delete_thread(self, thread_id: UUID, user_id: int):
        async with self.session.begin():
            # 1.根据thread_id和user_id查询，判断是否匹配
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                # 为None，说明不存在，或者不属于当前用户，抛出异常
                # raise: 就是指扔出去一个异常，代码会立刻终止，结束运行，把异常扔给调用者
                raise ChatThreadNotFoundError

            # 2.删除对象，就是删除数据库中的一条数据
            await self.repository.delete_thread(thread)

