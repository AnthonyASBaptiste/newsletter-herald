from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse

from helpers.key_utils import verify_api_key
from helpers.text_utils import extract_text_from_pdf, extract_text_from_docx

from llm.providers import choose_llm_and_summarize


app = FastAPI(
    title="SALLTO Herald API Gateway",
    description="The API Gateway acts as a single entry point that manages client requests and delegates them to the appropriate backend services.",
    version="0.1.0",
)


@app.get("/")
async def root():
    """
    A simple endpoint to confirm the API is running.
    """
    return {"message": "Welcome to your SALLTO Herald API Gateway"}


@app.post("/upload-document")
async def upload_summary(
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key)
):
    """
    Handles the uploading and summarization of document files through an HTTP POST endpoint.
    The function accepts a PDF or DOCX file, extracts its textual content, and generates
    a summary using a language model.

    :param _:
    :param file: an instance of UploadFile containing the uploaded document. Accepted
        file types are "application/pdf" and
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document".
    :return: a JSONResponse containing the generated summary of the document.
    """
    if file.content_type not in ["application/pdf",
                                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()

    try:
        if file.content_type == "application/pdf":
            with open("temp.pdf", "wb") as f:
                f.write(contents)
            text = extract_text_from_pdf("temp.pdf")
        else:
            text = extract_text_from_docx(file.file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    try:
        summary = choose_llm_and_summarize(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return JSONResponse(content={"summary": summary})
