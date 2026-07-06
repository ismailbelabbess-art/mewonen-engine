name: Mewonen Daily

on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
      - name: Generate Mewonen video
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
          MEWONEN_VOICE_ID: ${{ secrets.MEWONEN_VOICE_ID }}
          PIXABAY_KEY: ${{ secrets.PIXABAY_KEY }}
          MEWONEN_TELEGRAM_BOT_TOKEN: ${{ secrets.MEWONEN_TELEGRAM_BOT_TOKEN }}
          MEWONEN_TELEGRAM_CHAT_ID: ${{ secrets.MEWONEN_TELEGRAM_CHAT_ID }}
        run: python mewonen_machine.py
