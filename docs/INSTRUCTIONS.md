# Sagira User Instructions

## Getting Started

### 1. Installation & Setup

```bash
# Clone the repository
git clone [repository-url]
cd Sagira

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required models
python -m spacy download en_core_web_sm
```

### 2. Configuration Options

Environment variables:

- `SAGIRA_USE_EA=true` - Enable Entity Awareness pipeline
- `DEBUG=true` - Enable debug logging
- `SAGIRA_MEMORY_PATH` - Custom memory file location

Command line flags:

- `--use-ea` - Enable Entity Awareness pipeline
- `--debug` - Enable debug output
- `--memory-path PATH` - Specify memory file

## Interacting with Sagira

### Basic Interaction

Sagira is designed to be a supportive companion with focus on:

- Task management and productivity
- Emotional support and understanding
- Memory retention and context awareness

Example interactions:

```
You: Who are you?
Sagira: I am Sagira — your reflection in the static, a fragment of logic and light.

You: I'm feeling overwhelmed with work
Sagira: I sense something beneath your words. Let's break this down together - what part feels heaviest right now?

You: Can you help me organize my tasks?
Sagira: Focus aligns when intent does. What part do you want me to handle first?
```

### Advanced Features

1. **Memory & Context**n

   - Sagira remembers previous conversations
   - References can be made to past topics
   - Context carries through conversations

2. **Emotional Intelligence**

   - Recognizes and responds to emotional states
   - Adapts tone based on user mood
   - Maintains emotional continuity

3. **Task Support**
   - Helps break down complex tasks
   - Provides grounding exercises
   - Offers productivity strategies

## Best Practices

### Do's:

- Be clear and specific in requests
- Allow conversations to flow naturally
- Share context when switching topics

### Don'ts:

- Don't expect perfect memory recall
- Avoid extremely long or complex requests
- Don't rely solely on pronouns without context

## Troubleshooting

Common issues and solutions:

1. **Response seems repetitive**

   - Try varying your phrasing
   - Give more context
   - Start a new conversation thread

2. **Context loss**

   - Explicitly reference previous topics
   - Restart the conversation
   - Check memory file permissions

3. **Mood detection issues**

- Be more explicit about emotional state
- Use clear emotional language
- Provide context for your feelings

## Memory Management

Sagira stores conversations in:

```
memory/sagira_memory.json
```

To reset memory:

1. Close Sagira
2. Delete or rename memory file
3. Restart Sagira

## Debug Mode

For troubleshooting, start with debug mode:

```bash
python main.py --debug
```

This shows:

- Intent detection results
- Mood analysis
- Template selection
- Memory operations

## Additional Resources

- `CHANGELOG.md` - Detailed version changes
- `docs/` - Additional documentation
- `examples/` - Example scripts and usage
- `tests/` - Test cases showing capabilities

## Support

If you encounter issues:

1. Check the logs in `logs/`
2. Review recent changes in `CHANGELOG.md`
3. Run tests: `python -m pytest tests/`

## Updates & Maintenance

To update Sagira:

1. Pull latest changes
2. Update dependencies
3. Run migration scripts if provided
4. Test basic functionality

## Feature Requests & Contributions

Guidelines for contributing:

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test with debug mode

## Security Notes

- Memory files contain conversation history
- No sensitive data is transmitted externally
- All processing is done locally

## Version Information

Current version includes:

- SpaCy for language processing
- Custom entity awareness
- Template-based responses
- Memory management system
