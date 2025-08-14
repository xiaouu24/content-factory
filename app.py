from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from controller import generate_package, publish_everything

app = FastAPI(title="Content Factory v2")

class GenerateRequest(BaseModel):
    product_input: str
    canonical_url: str | None = None
    schedule_iso: str | None = None

@app.post("/content-package")
async def content_package(req: GenerateRequest):
    try:
        pkg = await generate_package(req.product_input, req.canonical_url)
        result = {"package": pkg.model_dump()}
        if req.schedule_iso:
            result["publish"] = await publish_everything(pkg, req.schedule_iso)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
