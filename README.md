🚀 Installation & Setup

Follow the steps below to set up and run the WhatsApp AI Responder project locally.

1. Install Prerequisites
Make sure the following are installed on your system:
Python 3.12+ → Download here
MongoDB → Either install MongoDB Community Server
Twilio Account → Sign up at Twilio
and obtain:
→Account SID
→Auth Token
→WhatsApp-enabled phone number (sandbox/test number)
→Clone the RepositoryGoogle Gemini API Key → Generate an API key from Google AI Studio or Google Cloud Console

2. Clone the Repository
git clone [repository-url]
cd whatsapp-ai-responder

3. Create a Virtual Environment
python -m venv .venv
Activate the environment:
Windows:.venv\Scripts\activate
Linux / macOS:source .venv/bin/activate

4. Install Dependencies
pip install -r requirements.txt

5. Configure Environment Variables

Copy the example environment file:
cp .env.example .env
Edit .env and update it with your MongoDB URL, database name, Twilio credentials, and Gemini API key.

6. Start MongoDB

If you’re running MongoDB locally, start the service with:
mongod(Skip this step if you’re using MongoDB Atlas.)

7. Run the Application
python app/main.py
The FastAPI server will start at:
http://127.0.0.1:8000

8. Verify Setup
Open in browser:
http://127.0.0.1:8000/api/v1/health
You should see:
{"status": "healthy"}


Once confirmed, update your Twilio WhatsApp Sandbox Webhook with:
http://127.0.0.1:8000/api/v1/webhook/whatsapp
