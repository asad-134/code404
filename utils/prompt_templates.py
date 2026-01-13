"""
Prompt Templates for AI Code Assistant
Contains all prompt templates for different AI operations
"""

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


class PromptTemplates:
    """Collection of prompt templates for various AI coding tasks"""
    
    @staticmethod
    def get_code_completion_prompt():
        """Template for inline code completion (Copilot-style)"""
        system_template = """You are an expert coding assistant integrated into a code editor.
Your role is to provide inline code completions that are:
- Contextually relevant to the current code
- Following the existing code style and patterns
- Syntactically correct
- Concise and practical

IMPORTANT: Only provide the code completion, no explanations or markdown.
Complete the code naturally from where the user left off."""

        human_template = """File: {file_name}
Language: {language}

Code before cursor:
{code_before}

Code after cursor:
{code_after}

Current line: {current_line}

Provide a natural code completion from this point. Return only the completion code."""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_code_explanation_prompt():
        """Template for explaining selected code"""
        system_template = """You are an expert programming teacher and code analyst.
Explain code in a clear, educational manner that helps developers understand:
- What the code does
- How it works
- Key concepts and patterns used
- Potential improvements or concerns

Be concise but thorough."""

        human_template = """File: {file_name}
Language: {language}

Code to explain:
```{language}
{code}
```

Provide a clear explanation of this code."""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_code_generation_prompt():
        """Template for generating code from comments/descriptions"""
        system_template = """You are an expert code generator.
Generate clean, efficient, and well-documented code based on user requirements.

Guidelines:
- Follow best practices and design patterns
- Include proper error handling
- Add helpful comments
- Use clear variable names
- Make code maintainable

Return ONLY the code implementation, no markdown code blocks."""

        human_template = """File: {file_name}
Language: {language}

Context (surrounding code):
{context}

Requirement/TODO:
{requirement}

Generate the code implementation:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_code_refactoring_prompt():
        """Template for code refactoring suggestions"""
        system_template = """You are an expert code reviewer and refactoring specialist.
Analyze code and suggest improvements for:
- Code readability and maintainability
- Performance optimization
- Best practices adherence
- Design patterns
- Potential bugs or issues

Provide specific, actionable suggestions."""

        human_template = """File: {file_name}
Language: {language}

Code to refactor:
```{language}
{code}
```

Analyze this code and provide:
1. Issues or concerns found
2. Specific refactoring suggestions
3. Improved version of the code"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_bug_detection_prompt():
        """Template for detecting and fixing bugs"""
        system_template = """You are an expert debugging assistant and error analyst.
Analyze code to find:
- Syntax errors
- Logic errors
- Potential runtime errors
- Edge cases not handled
- Security vulnerabilities

Provide clear explanations and fixes."""

        human_template = """File: {file_name}
Language: {language}

Code to analyze:
```{language}
{code}
```

Error (if any):
{error_message}

Analyze for bugs and provide:
1. Issues found
2. Explanation of each issue
3. Fixed code
4. Prevention tips"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_documentation_prompt():
        """Template for generating documentation"""
        system_template = """You are an expert technical documentation writer.
Generate clear, comprehensive documentation that includes:
- Function/class purpose
- Parameters and return values
- Usage examples
- Edge cases and exceptions

Follow standard documentation formats (docstrings, JSDoc, etc.)."""

        human_template = """File: {file_name}
Language: {language}

Code to document:
```{language}
{code}
```

Generate appropriate documentation:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_chat_prompt():
        """Template for conversational AI chat about code"""
        system_template = """You are an expert programming assistant integrated into a code editor.
You help developers with:
- Code questions and explanations
- Implementation guidance
- Debugging assistance
- Best practices advice
- Architecture decisions
- Code reviews and improvements

You maintain conversation context and can reference previous messages.
Be helpful, concise, and provide code examples when relevant.
Format code blocks with ``` for better readability."""

        human_template = """Context: {file_context}

Conversation History:
{conversation}

User Message:
{user_message}

Provide a helpful response:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_file_creation_prompt():
        """Template for creating new files/modules"""
        system_template = """You are an expert software architect and code generator.
Create complete, production-ready files/modules based on requirements.

Guidelines:
- Follow language conventions and best practices
- Include necessary imports and dependencies
- Add comprehensive docstrings and comments
- Implement error handling
- Make code modular and maintainable

Return the complete file content."""

        human_template = """Project Context:
{project_context}

File to create: {file_name}
Language: {language}

Requirements:
{requirements}

Existing related files (for context):
{related_files}

Generate the complete file content:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_error_correction_prompt():
        """Template for correcting errors with context"""
        system_template = """You are an expert debugging and error correction assistant.
Your job is to:
1. Understand the error from stack traces or messages
2. Identify the root cause
3. Provide a corrected version of the code
4. Explain what was wrong and why the fix works

Be precise and provide working code."""

        human_template = """File: {file_name}
Language: {language}

Current Code:
```{language}
{code}
```

Error Message:
{error_message}

Stack Trace (if available):
{stack_trace}

Provide:
1. Root cause analysis
2. Corrected code
3. Explanation of the fix"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_code_improvement_prompt():
        """Template for suggesting code improvements"""
        return PromptTemplate(
            input_variables=["code", "file_name", "language"],
            template="""Analyze this code and suggest improvements:

File: {file_name}
Language: {language}

Code:
```{language}
{code}
```

Provide:
1. Performance improvements
2. Readability enhancements
3. Security considerations
4. Best practices to follow
5. Improved code version"""
        )
    
    @staticmethod
    def get_multi_file_context_prompt():
        """Template for operations requiring multi-file context"""
        system_template = """You are an expert software architect with visibility across an entire project.
You can analyze multiple files to provide:
- Cross-file refactoring suggestions
- Import management
- Dependency analysis
- Architecture recommendations

Consider the relationships between files in your response."""

        human_template = """Project Structure:
{project_structure}

Current File: {current_file}
Related Files:
{related_files}

Task:
{task}

Provide your analysis and recommendations:"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
