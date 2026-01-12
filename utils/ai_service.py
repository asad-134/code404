"""
AI Service Module for Code Editor
Handles all AI-powered features using LangChain and OpenRouter API
"""

import os
from typing import Dict, Optional, List, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain_classic.memory import ConversationBufferMemory
import json

# Load environment variables
load_dotenv()


class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming responses"""
    
    def __init__(self, callback_func=None):
        self.callback_func = callback_func
        self.text = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.text += token
        if self.callback_func:
            self.callback_func(token)
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes"""
        if self.callback_func:
            self.callback_func(None, finished=True)


class AIService:
    """
    Main AI service class for code editor
    Manages LLM interactions and provides AI-powered coding features
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize AI Service
        
        Args:
            config: Configuration dictionary with AI settings
        """
        self.config = config or self._load_default_config()
        self.llm = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.is_initialized = False
        self.current_model = self.config.get('model', 'mistralai/devstral-2512:free')
        
        # Initialize the LLM
        self._initialize_llm()
    
    def _load_default_config(self) -> Dict:
        """Load default configuration from environment variables"""
        return {
            'api_key': os.getenv('OPENROUTER_API_KEY'),
            'model': os.getenv('AI_MODEL', 'mistralai/devstral-2512:free'),
            'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('AI_MAX_TOKENS', '2048')),
            'enabled': os.getenv('AI_ENABLED', 'true').lower() == 'true',
            'auto_suggest': os.getenv('AI_AUTO_SUGGEST', 'true').lower() == 'true',
            'suggestion_delay': int(os.getenv('AI_SUGGESTION_DELAY', '1000'))
        }
    
    def _initialize_llm(self):
        """Initialize the language model with OpenRouter"""
        try:
            api_key = self.config.get('api_key')
            if not api_key:
                raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file")
            
            # Initialize ChatOpenAI with OpenRouter configuration
            self.llm = ChatOpenAI(
                model=self.current_model,
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 2048),
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost",  # Optional
                    "X-Title": "Code Editor AI"  # Optional
                },
                streaming=True
            )
            
            self.is_initialized = True
            print(f"✓ AI Service initialized with model: {self.current_model}")
            
        except Exception as e:
            print(f"✗ Failed to initialize AI service: {str(e)}")
            self.is_initialized = False
            raise
    
    def is_available(self) -> bool:
        """Check if AI service is available and enabled"""
        return self.is_initialized and self.config.get('enabled', True)
    
    def get_model_info(self) -> Dict:
        """Get current model information"""
        return {
            'model': self.current_model,
            'temperature': self.config.get('temperature'),
            'max_tokens': self.config.get('max_tokens'),
            'enabled': self.config.get('enabled'),
            'auto_suggest': self.config.get('auto_suggest')
        }
    
    def update_settings(self, settings: Dict):
        """
        Update AI service settings
        
        Args:
            settings: Dictionary with new settings
        """
        self.config.update(settings)
        
        # Reinitialize if model changed
        if 'model' in settings and settings['model'] != self.current_model:
            self.current_model = settings['model']
            self._initialize_llm()
    
    async def generate_completion(
        self,
        code_before: str,
        code_after: str,
        current_line: str,
        file_name: str = "untitled",
        language: str = "python",
        callback=None
    ) -> str:
        """
        Generate inline code completion
        
        Args:
            code_before: Code before cursor
            code_after: Code after cursor
            current_line: Current line content
            file_name: Name of the file
            language: Programming language
            callback: Optional callback for streaming
            
        Returns:
            Completion suggestion
        """
        if not self.is_available():
            return ""
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_code_completion_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code_before=code_before[-1000:],  # Last 1000 chars for context
                code_after=code_after[:500],  # Next 500 chars
                current_line=current_line
            )
            
            if callback:
                handler = StreamingCallbackHandler(callback)
                response = await self.llm.agenerate([messages], callbacks=[handler])
                return handler.text
            else:
                response = await self.llm.agenerate([messages])
                return response.generations[0][0].text.strip()
                
        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            return ""
    
    def generate_completion_sync(
        self,
        code_before: str,
        code_after: str,
        current_line: str,
        file_name: str = "untitled",
        language: str = "python"
    ) -> str:
        """
        Synchronous version of generate_completion
        
        Args:
            code_before: Code before cursor
            code_after: Code after cursor
            current_line: Current line content
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Completion suggestion
        """
        if not self.is_available():
            return ""
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_code_completion_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code_before=code_before[-1000:],
                code_after=code_after[:500],
                current_line=current_line
            )
            
            response = self.llm.invoke(messages)
            return response.content.strip()
                
        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            return ""
    
    def explain_code(
        self,
        code: str,
        file_name: str = "untitled",
        language: str = "python"
    ) -> str:
        """
        Explain selected code
        
        Args:
            code: Code to explain
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Explanation of the code
        """
        if not self.is_available():
            return "AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_code_explanation_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code=code
            )
            
            response = self.llm.invoke(messages)
            return response.content
                
        except Exception as e:
            return f"Error explaining code: {str(e)}"
    
    def generate_code_from_description(
        self,
        requirement: str,
        context: str = "",
        file_name: str = "untitled",
        language: str = "python"
    ) -> str:
        """
        Generate code from description/TODO comment
        
        Args:
            requirement: Description of what code should do
            context: Surrounding code context
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Generated code
        """
        if not self.is_available():
            return "# AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_code_generation_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                context=context[-1500:] if context else "No context provided",
                requirement=requirement
            )
            
            response = self.llm.invoke(messages)
            return response.content.strip()
                
        except Exception as e:
            return f"# Error generating code: {str(e)}"
    
    def suggest_refactoring(
        self,
        code: str,
        file_name: str = "untitled",
        language: str = "python"
    ) -> str:
        """
        Suggest refactoring improvements
        
        Args:
            code: Code to analyze
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Refactoring suggestions
        """
        if not self.is_available():
            return "AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_code_refactoring_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code=code
            )
            
            response = self.llm.invoke(messages)
            return response.content
                
        except Exception as e:
            return f"Error suggesting refactoring: {str(e)}"
    
    def detect_and_fix_bugs(
        self,
        code: str,
        error_message: str = "",
        file_name: str = "untitled",
        language: str = "python"
    ) -> str:
        """
        Detect bugs and suggest fixes
        
        Args:
            code: Code to analyze
            error_message: Error message if any
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Bug analysis and fixes
        """
        if not self.is_available():
            return "AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_bug_detection_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code=code,
                error_message=error_message or "No specific error message provided"
            )
            
            response = self.llm.invoke(messages)
            return response.content
                
        except Exception as e:
            return f"Error detecting bugs: {str(e)}"
    
    def correct_error(
        self,
        code: str,
        error_message: str,
        stack_trace: str = "",
        file_name: str = "untitled",
        language: str = "python"
    ) -> Dict[str, str]:
        """
        Correct code errors with detailed analysis
        
        Args:
            code: Code with error
            error_message: Error message
            stack_trace: Stack trace if available
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Dictionary with analysis, corrected_code, and explanation
        """
        if not self.is_available():
            return {
                'analysis': "AI service is not available",
                'corrected_code': code,
                'explanation': ""
            }
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_error_correction_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code=code,
                error_message=error_message,
                stack_trace=stack_trace or "No stack trace available"
            )
            
            response = self.llm.invoke(messages)
            content = response.content
            
            # Try to parse the response into sections
            sections = {
                'analysis': '',
                'corrected_code': '',
                'explanation': ''
            }
            
            # Simple parsing - look for code blocks and sections
            if '```' in content:
                parts = content.split('```')
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Code block
                        # Remove language identifier if present
                        lines = part.strip().split('\n')
                        if lines[0].strip() in ['python', 'javascript', 'java', 'c', 'cpp']:
                            sections['corrected_code'] = '\n'.join(lines[1:])
                        else:
                            sections['corrected_code'] = part.strip()
            
            sections['analysis'] = content
            sections['explanation'] = content
            
            return sections
                
        except Exception as e:
            return {
                'analysis': f"Error analyzing code: {str(e)}",
                'corrected_code': code,
                'explanation': ""
            }
    
    def generate_documentation(
        self,
        code: str,
        file_name: str = "untitled",
        language: str = "python"
    ) -> str:
        """
        Generate documentation for code
        
        Args:
            code: Code to document
            file_name: Name of the file
            language: Programming language
            
        Returns:
            Generated documentation
        """
        if not self.is_available():
            return "# AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_documentation_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                code=code
            )
            
            response = self.llm.invoke(messages)
            return response.content
                
        except Exception as e:
            return f"# Error generating documentation: {str(e)}"
    
    def chat(
        self,
        question: str,
        file_name: str = "untitled",
        file_context: str = "",
        language: str = "python",
        use_memory: bool = True
    ) -> str:
        """
        Chat with AI about code
        
        Args:
            question: User's question
            file_name: Current file name
            file_context: Current file content for context
            language: Programming language
            use_memory: Whether to use conversation memory
            
        Returns:
            AI response
        """
        if not self.is_available():
            return "AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_chat_prompt()
            messages = prompt.format_messages(
                file_name=file_name,
                language=language,
                file_context=file_context[-2000:] if file_context else "No file context",
                question=question
            )
            
            # Add memory if enabled
            if use_memory:
                history = self.memory.load_memory_variables({})
                if history.get('chat_history'):
                    # Prepend history to messages
                    messages = list(history['chat_history']) + messages
            
            response = self.llm.invoke(messages)
            
            # Save to memory
            if use_memory:
                self.memory.save_context(
                    {"input": question},
                    {"output": response.content}
                )
            
            return response.content
                
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def create_file(
        self,
        file_name: str,
        requirements: str,
        project_context: str = "",
        related_files: str = "",
        language: str = "python"
    ) -> str:
        """
        Generate complete file content based on requirements
        
        Args:
            file_name: Name of file to create
            requirements: What the file should do
            project_context: Context about the project
            related_files: Content of related files
            language: Programming language
            
        Returns:
            Complete file content
        """
        if not self.is_available():
            return "# AI service is not available"
        
        from .prompt_templates import PromptTemplates
        
        try:
            prompt = PromptTemplates.get_file_creation_prompt()
            messages = prompt.format_messages(
                project_context=project_context or "No project context provided",
                file_name=file_name,
                language=language,
                requirements=requirements,
                related_files=related_files or "No related files provided"
            )
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```'):
                lines = content.split('\n')
                # Remove first line (```language)
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # Remove last line (```)
                if lines[-1].strip() == '```':
                    lines = lines[:-1]
                content = '\n'.join(lines)
            
            return content
                
        except Exception as e:
            return f"# Error creating file: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test AI service connection
        
        Returns:
            Dictionary with test results
        """
        try:
            if not self.is_initialized:
                return {
                    'success': False,
                    'message': 'AI service not initialized',
                    'model': self.current_model
                }
            
            # Try a simple completion
            response = self.llm.invoke([
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Say 'Hello' if you can hear me.")
            ])
            
            return {
                'success': True,
                'message': 'AI service is working correctly',
                'model': self.current_model,
                'response': response.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}',
                'model': self.current_model
            }


# Singleton instance
_ai_service_instance = None


def get_ai_service(config: Optional[Dict] = None) -> AIService:
    """
    Get or create AI service singleton instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        AIService instance
    """
    global _ai_service_instance
    
    if _ai_service_instance is None:
        _ai_service_instance = AIService(config)
    
    return _ai_service_instance
