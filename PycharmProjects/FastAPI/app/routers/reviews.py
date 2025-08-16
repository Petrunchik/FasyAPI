import datetime
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, insert
from slugify import slugify
from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateReviews
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user

router = APIRouter(prefix='/reviews', tags=['reviews'])

@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active==True))
    all_review = reviews.all()
    if not all_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return all_review


@router.get('/{product_id}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    reviews = await db.scalars(
        select(Review).where(Review.is_active==True, Review.product_id == product_id))

    if reviews is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no reviews found"
        )

    return reviews.all()

@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                     create_review: CreateReviews,
                     product_id: int,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if not (0.0 <= create_review.grade <= 5.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade must be between 0.0 and 5.0"
        )
    if get_user.get('is_customer'):
        product = await db.scalar(select(Product).where(Product.id == product_id))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no product found"
            )
        await db.execute(insert(Review).values(
            product_id=product_id,
            comment=create_review.comment,
            comment_date=datetime.date.today(),
            grade=create_review.grade,
            user_id=get_user.get('id')
        ))

        rating = await db.scalars(select(Review.grade).where(Review.is_active==True, Review.product_id==product_id))
        all_rating = rating.all()
        if len(all_rating) <= 1:
            result_rating = all_rating
        else:
            result_rating = round(sum(all_rating) / len(all_rating), 1)

        product.rating = result_rating
        await db.commit()


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to use this method'
        )

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.delete('/{review_id}')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)],
                         review_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    review = await db.scalar(select(Review).where(Review.id == review_id))
    if get_user.get('is_admin'):
        if review is None:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no review found"
            )

        review.is_active = False
        await db.commit()

        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Product delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method"
        )