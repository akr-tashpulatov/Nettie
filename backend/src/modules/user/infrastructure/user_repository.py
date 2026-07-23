from sqlalchemy import func, or_, select, update

from src.core.database.interfaces.repositories import SQLAlchemyAbstractRepository
from src.models import UserModel

from ..application.dtos import UsersQueryDto
from ..domain.entities import User
from ..domain.value_objects import Email, PhoneNumber


class UserRepository(SQLAlchemyAbstractRepository):
    @staticmethod
    def _to_domain(m: UserModel) -> User:
        return User(
            id=m.id,
            email=Email.from_trusted(m.email),
            phone_number=PhoneNumber.from_trusted(m.phone_number),
            password_hash=m.password_hash,
            role=m.role,
            full_name=m.full_name,
            is_active=m.is_active,
            email_verified=m.email_verified,
            created_at=m.created_at,
        )

    async def add(self, user: User) -> User:
        model = UserModel(
            email=user.email.value,
            phone_number=user.phone_number.value,
            password_hash=user.password_hash,
            role=user.role,
            full_name=user.full_name,
            is_active=user.is_active,
            email_verified=user.email_verified,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self.session.get(UserModel, user_id)
        return self._to_domain(model) if model else None

    async def get_many(self, query: UsersQueryDto) -> tuple[list[User], int]:
        offset = (query.page - 1) * query.limit

        filters = []
        if query.query:
            search_term = f"%{query.query}%"
            filters.append(
                or_(
                    UserModel.full_name.ilike(search_term),
                    UserModel.email.ilike(search_term),
                    UserModel.phone_number.ilike(search_term),
                )
            )
        if query.is_active is not None:
            filters.append(UserModel.is_active == query.is_active)

        stmt = (
            select(UserModel)
            .where(*filters)
            .order_by(UserModel.created_at.desc())
            .limit(query.limit)
            .offset(offset)
        )
        total_stmt = select(func.count()).select_from(UserModel).where(*filters)

        total = await self.session.scalar(total_stmt) or 0
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()], total

    async def get_by_email(self, email: str) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        return self._to_domain(model) if model else None

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(UserModel.phone_number == phone_number)
        )
        return self._to_domain(model) if model else None

    async def exists_by_email(self, email: str, exclude_id: int | None = None) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email)
        if exclude_id is not None:
            stmt = stmt.where(UserModel.id != exclude_id)
        return await self.session.scalar(stmt.limit(1)) is not None

    async def exists_by_phone_number(
        self, phone_number: str, exclude_id: int | None = None
    ) -> bool:
        stmt = select(UserModel.id).where(UserModel.phone_number == phone_number)
        if exclude_id is not None:
            stmt = stmt.where(UserModel.id != exclude_id)
        return await self.session.scalar(stmt.limit(1)) is not None

    async def update(self, user: User) -> User:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                full_name=user.full_name,
                role=user.role,
                email=user.email.value,
                phone_number=user.phone_number.value,
                password_hash=user.password_hash,
                is_active=user.is_active,
                email_verified=user.email_verified,
            )
            .returning(UserModel)
        )
        result = await self.session.execute(stmt)
        return self._to_domain(result.scalar_one())
