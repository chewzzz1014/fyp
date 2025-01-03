from fastapi import APIRouter, HTTPException, Depends
from .schema import NERRequest, NERResponse
from .utils import make_prediction, remove_non_alphanumeric
from backend.auth.utils import AuthJWT

router = APIRouter()

@router.post("/predict", response_model=NERResponse)
def ner_predict(
    request: NERRequest, 
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        text = remove_non_alphanumeric(request.text)
        entities = make_prediction(text)
        return {'entities': entities}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))