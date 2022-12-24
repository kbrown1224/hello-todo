from fastapi import HTTPException, status

missing_summary_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Card summary is required"
)

invalid_card_id_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Card not found"
)
