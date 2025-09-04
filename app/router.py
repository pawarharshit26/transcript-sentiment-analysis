from fastapi import APIRouter
from fastapi import status

router = APIRouter(prefix="/api/v1")


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():
    return {"message": "API is ready"}