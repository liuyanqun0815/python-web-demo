from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    user_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=10000)


class ProcessData(BaseModel):
    user_id: int
    action: str
    age: int


class ApiResponse(BaseModel):
    code: int
    message: str
    data: ProcessData | None
