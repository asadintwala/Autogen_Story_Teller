import google.generativeai as genai
import toml
import time

def load_config(config_path="config/config.toml"):
    """Load configuration from a TOML file."""
    try:
        config = toml.load(config_path)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    except toml.TomlDecodeError as e:
        raise ValueError(f"Error decoding TOML file: {e}")

def generate_text_gemini(prompt, config_path="config/config.toml", max_retries=3):
    """Generate text using the Gemini API with improved error handling."""
    # Load config each time to ensure we have the latest settings
    try:
        config = load_config(config_path)
        api_key = config['api_key']
        model_name = config['model_name']
        
        # Configure the API with the current key
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return f"Configuration error: {str(e)}"
    
    # Print debug information
    # print(f"Using model: {model_name}")
    # print(f"API key (first 4 chars): {api_key[:4]}...")
    
    retries = 0
    while retries < max_retries:
        try:
            # Create a new model instance each time
            model = genai.GenerativeModel(model_name)
            
            # Set safety settings to be more permissive if needed
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
            
            # Generate content with more detailed parameters
            generation_config = {
                "temperature": 0.7, # to generate more deterministiv yet creative & diverse(lengthy) output
                "top_p": 0.95, # more lengthy and diverse response
                "top_k": 40, # for more diverse words
                "max_output_tokens": 2048,
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if hasattr(response, 'text'):
                return response.text
            else:
                print(f"Unexpected response format: {response}")
                # Try to extract text from the response in different ways
                if hasattr(response, 'parts'):
                    parts = response.parts
                    if parts and len(parts) > 0:
                        return parts[0].text
                
                # If all else fails, convert to string
                return str(response)
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error generating text with Gemini (attempt {retries+1}/{max_retries}): {error_msg}")
            
            # Print more detailed error information
            import traceback
            traceback.print_exc()
            
            # Check for specific error types
            if "API key not valid" in error_msg or "authentication" in error_msg.lower():
                return "Error: The API key appears to be invalid. Please check your configuration."
            
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                wait_time = (retries + 1) * 5  # Exponential backoff
                print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                # For other errors, wait a shorter time
                time.sleep(2)
            
            retries += 1
    
    return "I apologize, but I encountered an error while processing your request. Please check your API key and model configuration."