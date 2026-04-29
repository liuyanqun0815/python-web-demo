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


class CpuBurnRequest(BaseModel):
    iterations: int = Field(default=5000, gt=0, le=200000)


class CpuBurnData(BaseModel):
    iterations: int
    checksum: int
    elapsed_ms: int


class CpuBurnResponse(BaseModel):
    code: int
    message: str
    data: CpuBurnData | None
