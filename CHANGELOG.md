## Current Release (0.3.0)

#### BREAKING CHANGES:
- Migration to MVC Architecture

#### FEATURES:
- Conversations become Password-free
- Added supporting for conversations in multi chats
- Added rate limit for messages in OpenAI conversation
- Added workflow for code style checking
- Added menu and few admin commands for gpt-3 info getting
- Added ORM models for ChatGPT conversations and users
- Implemented the "Repository" pattern for working with ORM models
- Added admin-role filter
- Added privacy policy optional config parametr, which asks each user to accept it
- Added middleware to prevent unregistered users from using the bot

#### IMPROVEMENTS:
- Migration to asynchronus request with aiohttp
- Refactoring and code style fixing
- Migration from gpt-3 to gpt-3.5-turbo model, which means faster responses and bigger prompts
- Temperature of gpt-3 answers has been raised to 0.7 by default

#### BUG FIXES:
- Fix bot triggering with ! prefix
