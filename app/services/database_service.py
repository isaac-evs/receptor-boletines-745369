from sqlalchemy import create_engine, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import boto3
from botocore.exceptions import ClientError

from app.config import (
    DATABASE_URL,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    PRESIGNED_URL_EXPIRATION
)
from app.models.newsletter import Base, Newsletter

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_db_session():
    session = SessionLocal()
    try:
        return session
    finally:
        session.close()

def get_newsletter_by_id_and_email(newsletter_id, email):
    try:
        session = get_db_session()
        newsletter = session.query(Newsletter).filter(
            Newsletter.id == newsletter_id,
            Newsletter.email == email
        ).first()

        if newsletter:
            # Mark the newsletter as read
            if not newsletter.read:
                newsletter.read = True
                session.commit()
                logger.info(f"Newsletter {newsletter_id} marked as read")

        return newsletter

    except Exception as e:
        logger.error(f"Error retrieving newsletter: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()

def get_s3_presigned_url(object_key):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )

        return presigned_url

    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        return None
