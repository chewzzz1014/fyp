from fastapi import APIRouter, HTTPException, Depends
from .schema import NERRequest, NERResponse
from .utils import make_prediction
from backend.auth.utils import AuthJWT

router = APIRouter()

@router.post("/predict", response_model=NERResponse)
def predict(
    request: NERRequest, 
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        entities = make_prediction(request.text)
        return {'entities': entities}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")