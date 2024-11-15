from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/{user_id}')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        return user
    raise HTTPException(status_code=404, detail="User was not found")


@router.post('/create')
async def create_user(user_data: CreateUser, db: Annotated[Session, Depends(get_db)]):
    new_user = insert(User).values(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        slug=slugify(user_data.username)
    )
    db.execute(new_user)
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_user(user_id: int, user_data: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    user_query = select(User).where(User.id == user_id)
    user = db.scalar(user_query)
    if user:
        update_query = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data.dict(exclude_unset=True))
        )
        db.execute(update_query)
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    raise HTTPException(status_code=404, detail="User was not found")


@router.delete('/delete')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_query = select(User).where(User.id == user_id)
    user = db.scalar(user_query)
    if user:
        delete_query = delete(User).where(User.id == user_id)
        db.execute(delete_query)
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User deletion is successful!'}
    raise HTTPException(status_code=404, detail="User was not found")
