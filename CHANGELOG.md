## Current Release (0.3.0)

#### BREAKING CHANGES:
- Migration to MVC Architecture

#### FEATURES:
- Conversations become Password-free
- Added supporting for conversations in multi chats
- Added rate limit for messages in OpenAI conversation
- Added workflow for code style checking
- Added menu and admin-actions handlers
- Added ORM models for ChatGPT conversations and users
- Implemented the "Repository" pattern for working with ORM models
- Added admin-role filter

#### IMPROVEMENTS:
- Migration to asynchronus request with aiohttp
- Refactoring and code style fixing
- Migration from gpt-3 to gpt-3.5-turbo model, which means faster responses and bigger prompts

#### BUG FIXES:
- Fix bot triggering with ! prefix
