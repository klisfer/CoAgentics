def analyze_prompt(prompt: str) -> str:
    """
    Analyzes the user's prompt to provide more context for the AI model.

    For now, it performs a simple keyword check. If the prompt contains
    the word "finance," it enhances the prompt to guide the AI.

    Args:
        prompt: The user's input string.

    Returns:
        An enhanced prompt if keywords are found, otherwise the original prompt.
    """
    # Convert prompt to lowercase for case-insensitive matching
    lower_prompt = prompt.lower()

    if "finance" in lower_prompt:
        enhanced_prompt = (
            "As a financial advisor, please provide a detailed and informative "
            f"response to the following user query: '{prompt}'"
        )
        return enhanced_prompt
    
    # If no specific keywords are found, return the original prompt
    return prompt 