import json
import asyncio
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
import openai

from app.models import EnquiryNL
from .tools import EnquiryExtractionTool
from .prompt import EXTRACTION_PROMPT


async def convert_natural_language_to_form(
        *,
        enquiry: EnquiryNL,
        client: openai.OpenAI
) -> dict:
    
    system_prompt = EXTRACTION_PROMPT

    try:
        completion = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enquiry.requirement_description}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "EnquiryExtractionTool",
                        "description": "Extract user preferences for rental housing.",
                        "parameters": EnquiryExtractionTool.model_json_schema() 
                    }
                }
            ],
            tool_choice={
                "type": "function", 
                "function": {"name": "EnquiryExtractionTool"}
            }
        )
        
        tool_call = completion.choices[0].message.tool_calls[0]
        if tool_call.function.name == "EnquiryExtractionTool":
            extracted_data = json.loads(tool_call.function.arguments)
            filtered_data = {k: v for k, v in extracted_data.items() if v is not None}
            if enquiry.device_id:
                # name must same as EnquiryForm.device_id
                filtered_data['device_id'] = enquiry.device_id
            return filtered_data
        else:
            return {}

    # API Exception
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error communicating with AI model."
            
        )
    
    # Parse Exception
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        print(f"LLM parsing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not understand or parse the requirement description. Please try rephrasing your request."
        )
