START_MESSAGE: str = "Hi there! I'm Professor Bot, your friendly job search assistant.😊\n" \
                     "I'm here to help you find the perfect position.\n\n" \
                     "To stop chatting with me at any time, just send '/cancel'.\n\n"

POSITION_MESSAGE: str = "What kind of position are you looking for? ✨\n" \
                        "(e.g., Software Engineer, Data Scientist, Marketing Manager)"

POSITION_NOT_FOUND: str = "I couldn't find any positions matching your request. 😕\n" \
                          "Please try again"
multi_value_message: str = "📌  You can enter multiple tags separated by commas."

LOCATION_MESSAGE: str = "Where are you hoping to find a position? 🌎\n" \
                        "(e.g., Rishon Lezion, New York City, San Francisco)\n\n" + multi_value_message

EXPERIENCE_MESSAGE: str = "How many years of professional experience do you have in this field? 💼\n"

FILTER_TILE_MESSAGE: str = "To help me narrow down your search, tell me about any relevant tags or keywords.\n" \
                           "For example: 'remote', 'entry-level', 'python', 'machine learning', 'QA'.\n\n" + multi_value_message

THANK_YOU_MESSAGE: str = "Thank you for chatting with Professor Bot!\n\n" \
                         "I can help you find jobs on LinkedIn, Glassdoor, and more."

SEARCH_MESSAGE: str = "To search for jobs on a specific site, simply send the site name:\n" \
                      "/linkedin\n" \
                      "/glassdoor\n" \
                      "/google\n\n" \
                      "Or, use the command /find to search across all supported job boards for a broader search.\n\n" \
                      "Let me know how I can assist you further! 😊"

BYE_MESSAGE: str = "Have a great day!✨\n" \
                   "I hope to assist you with your job search in the future.😊"

VERIFY_MESSAGE: str = "Did you choose: %s ? 🧐"
