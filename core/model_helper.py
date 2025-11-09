
import google.generativeai as genai
import time
from google.api_core import exceptions as google_exceptions

# DeepSeek support (OpenAI-compatible)
try:
    import openai
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    openai = None

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

def generate_content_with_retry(model, prompt, max_retries=3, base_delay=1.0):
    """Generate content with automatic retry for rate limit errors"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except google_exceptions.ResourceExhausted as e:
            last_error = e
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str or "rate limit" in error_str.lower():
                # Calculate retry delay with exponential backoff
                retry_delay = base_delay * (2 ** attempt)
                
                # Try to extract retry time from error message
                if "retry in" in error_str.lower() or "retry-after" in error_str.lower():
                    try:
                        import re
                        # Look for patterns like "retry in 60s" or "retry-after: 60"
                        delay_match = re.search(r'retry[-\s]*(?:in|after)[\s:]*(\d+)', error_str.lower())
                        if delay_match:
                            retry_delay = float(delay_match.group(1)) + 2
                        else:
                            # Try another pattern
                            delay_match = re.search(r'(\d+)\s*second', error_str.lower())
                            if delay_match:
                                retry_delay = float(delay_match.group(1)) + 2
                    except:
                        pass
                
                # Cap delay at 10 seconds
                retry_delay = min(retry_delay, 10.0)
                
                if attempt < max_retries - 1:
                    print(f"Rate limit hit, retrying in {retry_delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} attempts")
            else:
                raise
        except Exception as e:
            if attempt == 0:
                raise
            else:
                raise Exception(f"Error after {attempt + 1} attempts: {str(e)}")
    
    raise last_error

# DeepSeek API support
def get_deepseek_model(api_key: str):
    """Get DeepSeek model (OpenAI-compatible API)"""
    if not DEEPSEEK_AVAILABLE:
        raise ImportError(
            "OpenAI library not installed. Install it with: pip install openai"
        )
    
    # Configure OpenAI client for DeepSeek
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    return client

def get_deepseek_response_text(response):
    """Extract text from DeepSeek/OpenAI API response"""
    try:
        if hasattr(response, 'choices') and len(response.choices) > 0:
            return response.choices[0].message.content
        elif hasattr(response, 'text'):
            return response.text
        else:
            return str(response)
    except Exception as e:
        return f"Error extracting response: {str(e)}"

def generate_content_with_deepseek(client, prompt, max_retries=3, base_delay=1.0):
    """Generate content using DeepSeek API with automatic retry"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Handle rate limits
            if "rate limit" in error_str or "429" in error_str or "quota" in error_str:
                retry_delay = base_delay * (2 ** attempt)
                retry_delay = min(retry_delay, 10.0)
                
                if attempt < max_retries - 1:
                    print(f"DeepSeek rate limit hit, retrying in {retry_delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} attempts")
            else:
                if attempt == 0:
                    raise
                else:
                    raise Exception(f"Error after {attempt + 1} attempts: {str(e)}")
    
    raise last_error

