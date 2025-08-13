 token
   - `TELEGRAM_CHAT_ID` = `@MyKitchenDeals`
   - `AMAZON_TAG` = `yourtag-20` (optional)
4. **Cron schedule:** `*/10 * * * *`
5. **Command:** `python kitchen_deals_bot.py`

## Local Test (optional)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_TOKEN=...
export TELEGRAM_CHAT_ID=@MyKitchenDeals
export AMAZON_TAG=yourtag-20
python kitchen_deals_bot.py
```

## Files

- `kitchen_deals_bot.py` — main script
- `requirements.txt` — deps
- `.gitignore` — ignores venv, caches

