
import google.generativeai as genai
import time
from google.api_core import exceptions as google_exceptions

def get_response_text(response):
    """Extract text from Gemini API response"""
    try:
        # Try different ways to access the text
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            return response.candidates[0].content.parts[0].text
        elif hasattr(response, 'result'):
            return response.result
        else:
            return str(response)
    except Exception as e:
        return f"Error extracting response: {str(e)}"

def get_gemini_model(api_key: str):
    """Get the best available Gemini model"""
    genai.configure(api_key=api_key)
    # Prefer supported models for this API version (remove unsupported flash variant)
    model_names = [
        'gemini-2.5-pro',
        'gemini-1.5-pro', 
        'gemini-1.0-pro',
        'gemini-pro'
    ]
    
    # Try each model in order
    last_error = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            # Test if model is accessible by getting its name
            _ = model.model_name
            return model
        except Exception as e:
            last_error = e
            continue
    
    # If all models fail, try to list available models
    try:
        available_models = list(genai.list_models())
        generate_models = [
            m for m in available_models 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        if generate_models:
            model_name = generate_models[0].name.split('/')[-1]
            return genai.GenerativeModel(model_name)
    except Exception:
        pass
    
    # Last resort: raise error with helpful message
    raise ValueError(
        f"Could not find a valid Gemini model. "
        f"Last error: {str(last_error)}. "
        f"Please check your API key and ensure you have access to Gemini models. "
        f"Try: gemini-1.5-flash, gemini-1.5-pro, or gemini-pro"
    )

def generate_content_with_retry(model, prompt, max_retries=2, base_delay=1):
    """Generate content with automatic retry for rate limit errors"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except google_exceptions.ResourceExhausted as e:
            last_error = e
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str:
                retry_delay = base_delay * (2 ** attempt)
                
                if "retry in" in error_str.lower():
                    try:
                        import re
                        delay_match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                        if delay_match:
                            retry_delay = float(delay_match.group(1)) + 1
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(
                        f"Rate limit exceeded after {max_retries} attempts. "
                        f"Please wait and try again later."
                    )
            else:
                raise
        except Exception as e:
            if attempt == 0:
                raise
            else:
                raise Exception(f"Error after {attempt + 1} attempts: {str(e)}")
    
    raise last_error

