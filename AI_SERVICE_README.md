# AI Service Documentation

## Overview
The AI Service module provides GitHub Copilot-like functionality using LangChain and OpenRouter API. It integrates advanced AI coding assistance into the code editor.

## Architecture

### Key Components

1. **AIService (`utils/ai_service.py`)**
   - Main service class managing all AI interactions
   - Handles LLM initialization and configuration
   - Provides methods for all AI features
   - Manages conversation memory for chat functionality

2. **PromptTemplates (`utils/prompt_templates.py`)**
   - Collection of carefully crafted prompts for different tasks
   - Uses LangChain's ChatPromptTemplate for structured prompts
   - Separates system and user messages for better context

3. **Configuration**
   - `.env` file: API keys and environment settings
   - `editor_config.json`: Editor and AI feature settings
   - Runtime configuration through AIService

## Features Implemented

### 1. **Code Completion** ✓
```python
completion = ai_service.generate_completion_sync(
    code_before="def calculate_sum(a, b):\n    ",
    code_after="",
    current_line="    ",
    file_name="test.py",
    language="python"
)
```
- Inline suggestions based on context
- Considers code before and after cursor
- Language-aware completions

### 2. **Code Explanation** ✓
```python
explanation = ai_service.explain_code(
    code="def fibonacci(n): ...",
    file_name="test.py",
    language="python"
)
```
- Educational explanations of code
- Explains what code does and how it works
- Identifies patterns and concepts

### 3. **Code Generation** ✓
```python
code = ai_service.generate_code_from_description(
    requirement="Create a function to validate email addresses",
    context="# Email validation utility",
    file_name="utils.py",
    language="python"
)
```
- Generate code from TODO comments
- Implement functions from descriptions
- Context-aware generation

### 4. **Code Refactoring** ✓
```python
suggestions = ai_service.suggest_refactoring(
    code="# Your code here",
    file_name="main.py",
    language="python"
)
```
- Performance improvements
- Readability enhancements
- Best practices recommendations

### 5. **Bug Detection & Fixing** ✓
```python
analysis = ai_service.detect_and_fix_bugs(
    code="def divide(a, b): return a/b",
    error_message="ZeroDivisionError",
    file_name="calc.py",
    language="python"
)
```
- Identify potential bugs
- Suggest fixes with explanations
- Handle runtime errors

### 6. **Error Correction** ✓
```python
correction = ai_service.correct_error(
    code="buggy_code_here",
    error_message="TypeError: ...",
    stack_trace="Traceback...",
    file_name="app.py",
    language="python"
)
# Returns: {'analysis': '...', 'corrected_code': '...', 'explanation': '...'}
```
- Detailed error analysis
- Root cause identification
- Corrected code with explanation

### 7. **Documentation Generation** ✓
```python
docs = ai_service.generate_documentation(
    code="def complex_function(): ...",
    file_name="api.py",
    language="python"
)
```
- Generate docstrings
- Create inline comments
- README sections

### 8. **AI Chat** ✓
```python
response = ai_service.chat(
    question="How do I optimize this function?",
    file_name="main.py",
    file_context="def slow_function(): ...",
    language="python",
    use_memory=True
)
```
- Context-aware conversations
- Maintains conversation history
- File-specific assistance

### 9. **File Creation** ✓
```python
content = ai_service.create_file(
    file_name="user_service.py",
    requirements="Create a user authentication service",
    project_context="Flask REST API",
    related_files="# models.py content...",
    language="python"
)
```
- Generate complete files
- Context from related files
- Project-aware code

## Configuration

### Environment Variables (`.env`)
```bash
# OpenRouter API Key (Required)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Model Configuration
AI_MODEL=mistralai/devstral-2512:free
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048

# Feature Toggles
AI_ENABLED=true
AI_AUTO_SUGGEST=true
AI_SUGGESTION_DELAY=1000
```

### Editor Config (`editor_config.json`)
```json
{
  "ai": {
    "enabled": true,
    "model": "mistralai/devstral-2512:free",
    "temperature": 0.7,
    "max_tokens": 2048,
    "features": {
      "code_completion": true,
      "code_explanation": true,
      "code_generation": true,
      "refactoring": true,
      "bug_detection": true,
      "documentation": true,
      "chat": true,
      "file_creation": true,
      "error_correction": true
    }
  }
}
```

## Usage Examples

### Initialize AI Service
```python
from utils.ai_service import get_ai_service

# Get singleton instance
ai_service = get_ai_service()

# Check availability
if ai_service.is_available():
    print("AI is ready!")

# Get model info
info = ai_service.get_model_info()
print(f"Using model: {info['model']}")
```

### Test Connection
```python
result = ai_service.test_connection()
if result['success']:
    print("✓ AI service working")
else:
    print(f"✗ Error: {result['message']}")
```

### Update Settings
```python
ai_service.update_settings({
    'temperature': 0.5,
    'max_tokens': 1024
})
```

### Clear Chat Memory
```python
ai_service.clear_memory()
```

## LangChain Best Practices

### 1. **Prompt Engineering**
- Clear system messages defining AI role
- Structured input with context
- Specific output format instructions

### 2. **Context Management**
- Limit context to relevant code (last 1000-1500 chars)
- Include code before and after cursor
- Provide file and language info

### 3. **Error Handling**
- Graceful fallbacks when API fails
- User-friendly error messages
- Retry logic for transient failures

### 4. **Memory Management**
- Use ConversationBufferMemory for chat
- Clear memory when switching files
- Limit memory size to prevent token overflow

### 5. **Streaming Responses**
- Use callbacks for real-time feedback
- Implement custom StreamingCallbackHandler
- Show progress indicators to users

## OpenRouter Integration

### Why OpenRouter?
- Access to multiple models through one API
- Free tier available (devstral-2512:free)
- OpenAI-compatible API format
- No vendor lock-in

### Configuration
```python
self.llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "Code Editor AI"
    }
)
```

### Available Models
- `mistralai/devstral-2512:free` - Free coding model
- `anthropic/claude-3.5-sonnet` - High quality (paid)
- `openai/gpt-4-turbo` - Most capable (paid)
- Many more on OpenRouter

## Testing

Run the test script to verify setup:
```bash
python test_ai_service.py
```

Tests include:
1. Service initialization
2. Configuration loading
3. API connection
4. Code completion
5. Code explanation
6. Error correction

## Next Steps (Phase 2-4)

### Phase 2: Core Features Integration
- [ ] Integrate completion into text widget
- [ ] Add inline ghost text display
- [ ] Implement debounced suggestions
- [ ] Add accept/reject keybindings

### Phase 3: Advanced Features
- [ ] Multi-file context indexing
- [ ] Vector database for code search
- [ ] Project-wide refactoring
- [ ] Smart import suggestions

### Phase 4: UI Integration
- [ ] AI status indicator
- [ ] Settings panel for AI config
- [ ] Chat panel interface
- [ ] Token usage tracking

## Troubleshooting

### API Key Issues
```bash
# Verify .env file exists and has correct key
cat .env | grep OPENROUTER_API_KEY
```

### Import Errors
```bash
# Install required packages
pip install langchain langchain-openai python-dotenv
```

### Connection Issues
```bash
# Test connection manually
python test_ai_service.py
```

### Rate Limiting
- Free tier has rate limits
- Implement exponential backoff
- Cache common completions
- Use streaming for better UX

## Learning Resources

### LangChain
- [Official Documentation](https://python.langchain.com/docs/get_started)
- [Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/)
- [Memory](https://python.langchain.com/docs/modules/memory/)

### OpenRouter
- [Documentation](https://openrouter.ai/docs)
- [Models](https://openrouter.ai/models)
- [API Reference](https://openrouter.ai/docs/api-reference)

### Coding AI Agents
- Understand token limits and context windows
- Master prompt engineering techniques
- Learn about streaming and async operations
- Study code parsing and AST manipulation

## Contributing

When adding new features:
1. Add prompt template in `prompt_templates.py`
2. Implement method in `ai_service.py`
3. Add configuration in `editor_config.json`
4. Update documentation
5. Add tests

## License

This AI service module is part of the Code Editor project.
