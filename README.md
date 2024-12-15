# JobSeekerTG Bot
<img src="https://github.com/user-attachments/assets/44a7be89-cfe3-4e4c-bb94-f6ca8e1b23db" width="400" height="400">

JobSeekerTG is a Telegram bot that scrapes job postings from platforms like LinkedIn, Indeed, Glassdoor, and others (currently under development). It gathers job data based on title and location, reformats it into a structured format, and saves it to a MongoDB database. New job posts are automatically sent to a designated Telegram bot chat.

This project is based on the [JobSpy](https://github.com/Bunsly/JobSpy) project. Credits to the original creator.

## Features

- **Job scraping**: Collects job postings from multiple job platforms.
- **Structured data**: Reformats job data into a structured format for easy processing and storage.
- **Database storage**: Saves job data into a MongoDB database.
- **Telegram integration**: Sends new job postings directly to a Telegram bot chat.

## Data Structure

The scraped job postings are stored in the following format:

```yaml
JobPost
├── title
├── company
├── company_url
├── job_url
├── location
│   ├── country
│   ├── city
│   ├── state
├── description
├── job_type: fulltime, parttime, internship, contract
├── job_function
│   ├── interval: yearly, monthly, weekly, daily, hourly
│   ├── min_amount
│   ├── max_amount
│   ├── currency
│   └── salary_source: direct_data, description (parsed from posting)
├── date_posted
├── emails
└── is_remote
```

## Prerequisites

- Python 3.8+
- MongoDB
- Telegram bot token (create a bot via [BotFather](https://core.telegram.org/bots#botfather))

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yariv245/JobSeeker.git
   cd JobSeeker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with the following:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   MONGO_URI=your_mongodb_connection_string
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```

## Usage

- Add the bot to a Telegram group or chat.
- Start the bot to receive job postings as they are scraped.

## Testing

This project includes testing to ensure data scraping, formatting, and Telegram integration work as expected. Run the tests using:

```bash
pytest
```

Ensure you have the necessary environment variables and mock data set up before running the tests.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a pull request.

## Acknowledgments

- [JobSpy](https://github.com/Bunsly/JobSpy) for inspiring this project.

