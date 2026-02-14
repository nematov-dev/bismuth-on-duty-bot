# Telegram Employee Birthday & Duty Scheduler Bot

This project is a Telegram bot that automates employee birthday reminders and daily duty scheduling. It is built using **Python**, **Aiogram**, and **APScheduler**.

---

## Features

1. 🎉 **Birthday Notifications**

   * Sends birthday greetings to employees in a Telegram group.
   * Sends a reminder message one day before the birthday.

2. 🛎 **Duty Scheduling**

   * Automatically rotates duty assignments among eligible employees.
   * Keeps track of the last assigned employee and continues rotation.

3. 🛠 **Admin Panel**

   * Add new employees with name, birthday, and duty eligibility.
   * View a list of all employees.
   * Clear the employee database.

4. ⏰ **Timezone Support**

   * All scheduled tasks follow the Uzbekistan timezone (`Asia/Tashkent`).

---

## Project Structure

```
bot/
├── bot.py                 # Main bot code
├── data.json              # Employee database (auto-generated)
├── .env                   # Environment variables (TOKEN, ADMIN_ID, GROUP_ID)
└── README.md
```

---

## Requirements

* Python >= 3.9
* Aiogram >= 3.x
* APScheduler
* python-decouple
* pytz

Install dependencies:

```bash
pip install aiogram apscheduler python-decouple pytz
```

---

## Environment Variables

Create a `.env` file in the project root:

```
TOKEN=<your_bot_token>
ADMIN_ID=<your_telegram_user_id>
GROUP_ID=<target_group_id>
```

* `TOKEN`: Telegram bot token from @BotFather.
* `ADMIN_ID`: Telegram user ID for admin actions.
* `GROUP_ID`: Telegram group ID to send messages.

---

## Usage

1. Run the bot:

```bash
python bot.py
```

2. Admin commands in Telegram:

| Command / Button          | Description             |
| ------------------------- | ----------------------- |
| `/start`                  | Show admin panel        |
| `➕ Xodim qo'shish`        | Add a new employee      |
| `📋 Ro'yxat`              | View employee list      |
| `🗑 O'chirish (Tozalash)` | Clear employee database |

3. Bot automatically:

   * Sends birthday greetings on the employee's birthday.
   * Sends reminders one day prior.
   * Announces daily duty assignments for eligible employees.

---

## Data Storage

* **data.json** file stores employees in the following structure:

```json
{
  "users": [
    {
      "name": "John Doe",
      "birthday": "14-02",
      "can_be_duty": true
    }
  ],
  "last_duty_index": 0
}
```

* `name`: Employee full name
* `birthday`: `dd-mm` format
* `can_be_duty`: Whether the employee can be assigned daily duties
* `last_duty_index`: Tracks last assigned employee for rotation

---

## Scheduling

* Uses **APScheduler** to run the `daily_job` function.
* Configured to run **Monday to Saturday** at **10:00 AM UZT**.
* Tasks include:

  * Birthday greetings
  * Birthday reminders
  * Duty assignment announcements

---

## Notes

* Make sure the bot has permissions to send messages in the target group.
* The bot will automatically create `data.json` if it doesn’t exist.
* Supports Markdown formatting in messages.

---

## License

This project is open-source and free to use.
