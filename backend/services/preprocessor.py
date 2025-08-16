import google.generativeai as genai
import os
import dotenv
from PIL import Image
from pdf2image import convert_from_path
import json
dotenv.load_dotenv()
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)
# This model is multimodal and can handle images and text.
VISION_MODEL = "models/gemini-1.5-pro-latest"
# Use a faster, more cost-effective model for text-only tasks.
TEXT_MODEL = "models/gemini-1.5-flash-latest"


def get_model_for_file(path: str) -> str:
    """
    Selects the appropriate generative model based on the file type.

    Args:
        path: The file path.

    Returns:
        The name of the recommended Google AI model.
    """
    p = path.lower()
    # For image files, a vision model is required.
    if p.endswith((".png", ".jpg", ".jpeg", ".tiff", ".webp", ".bmp")):
        return VISION_MODEL
    # For PDFs, a vision model is often best for receipts/invoices,
    # as they can be scanned. The calling code will need to convert
    # PDF pages to images before sending to the model.
    if p.endswith(".pdf"):
        return VISION_MODEL
    # For text-based files, a standard text model is sufficient.
    # The calling code is responsible for extracting text from these files.
    if p.endswith((".txt", ".md", ".docx", ".json", ".csv")):
        return TEXT_MODEL
    # Fallback to the standard text model for unknown file types.
    return TEXT_MODEL


def process_receipt(file_path: str, user_id: str) -> dict:
    """
    Processes a receipt file to extract expense details using a generative model.

    Args:
        file_path: The path to the receipt file (image, PDF, or text).
        user_id: The ID of the user submitting the expense.

    Returns:
        A dictionary containing the extracted expense details.
    """
    model_name = get_model_for_file(file_path)
    content = None
    is_pdf_fallback = False

    if model_name == VISION_MODEL:
        try:
            if file_path.lower().endswith(".pdf"):
                # Convert first page of PDF to an image
                images = convert_from_path(
                    file_path, first_page=1, last_page=1)
                if not images:
                    raise ValueError("Could not extract image from PDF.")
                content = images[0]
            else:
                content = Image.open(file_path)
        except Exception as e:
            print(
                f"Vision model processing failed for {file_path}: {e}. Attempting to process as text.")
            if file_path.lower().endswith(".pdf"):
                is_pdf_fallback = True
                model_name = TEXT_MODEL  # Switch to text model
            else:
                # For non-PDF image files, failure is terminal.
                return {"error": f"Failed to process image file: {e}"}

    if model_name == TEXT_MODEL:
        # This block handles regular text files and PDF fallbacks.
        try:
            # For PDF fallback, we need to extract text first.
            if is_pdf_fallback:
                try:
                    import fitz  # fitz
                    doc = fitz.open(file_path)
                    text_content = ""
                    for page in doc:
                        text_content += page.get_text()
                    doc.close()
                    content = text_content
                    if not content.strip():
                        return {"error": "PDF contains no extractable text."}
                except ImportError:
                    return {"error": "PyMuPDF is required for PDF text extraction. Please install it (`pip install PyMuPDF`)."}
                except Exception as e:
                    return {"error": f"Failed to extract text from PDF: {e}"}
            else:
                # For regular text-based files.
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return {"error": f"Failed to read text file: {e}"}

    if content is None:
        return {"error": "Could not prepare content for model processing."}

    # Instantiate the model (could be vision or text at this point)
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    Analyze the following receipt and extract the expense details.
    Provide the output in a clean JSON format. Do not include the markdown "```json" wrapper.
    The user ID is "{user_id}".
    Use the current date and time if the creation date is not found in the receipt.

    The JSON object should have a single key "expenses" with the following structure:
    {{
        "expenses": {{
            "title": "string",
            "category": "string (e.g., Food, Travel, Office Supplies)",
            "amount": "float",
            "description": "string",
        }}
    }}
    """

    try:
        response = model.generate_content([prompt, content])
        # Clean up the response to ensure it's valid JSON
        cleaned_response_text = response.text.strip().replace(
            "```json", "").replace("```", "").strip()
        return json.loads(cleaned_response_text)
    except Exception as e:
        print(f"Error generating content or parsing JSON: {e}")
        return {"error": "Failed to get valid details from the model."}
