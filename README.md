
# RESTful SMTP Client
SMTP Client for Serverless Functions

This project provides an SMTP client accessible via a RESTful API, allowing serverless functions to send emails. It overcomes the limitations of traditional SMTP libraries like Nodemailer in serverless environments by handling the SMTP communication in a separate service.

## Features

- **Send Emails**: Send emails using SMTP with SSL/TLS encryption.
- **Dry Run**: Validate and decode email messages without sending them.
- **Health Check**: Check the health status of this SMTP client.

## Getting Started

### Prerequisites

- **Python 3.7+**
- **Flask**
- **Gunicorn** (for production deployment)
- **Docker** (for containerised deployment)

### Cloning the Repository

   ```bash
   git clone https://github.com/bearz314/restful-smtp-client.git
   cd restful-smtp-client
   ```

### Running the Application (Local Development)

To run the application locally, you can use Flask's built-in server for development purposes:

1. **Install Dependencies**:
   Use `pip` to install the required Python packages. Consider using a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the following variables. Note that for security, only SSL/TLS is supported. STARTTLS is not supported, but you could modify the code. The same `API_KEY` created here must be provided by the serverless functions.
   ```plaintext
   SMTP_SERVER=smtp.yourprovider.com
   SMTP_PORT=your_smtp_port
   SMTP_USER=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   API_KEY=your_api_key
   ```
   **This `API_KEY` must be very strong** or people can send emails on your behalf!

3. **Run Flask application for development**:
   Do not use for production.
   ```bash
   flask run
   ```

4. **Use WSGI server for production**:
   You can use Gunicorn or other WSGI server.
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Using Docker (For Deployment to Production)

A Dockerfile is already prepared for your convenience.

1. **Build the Docker Image**:
   ```bash
   docker build -t restful-smtp-client .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -d -p 5000:5000 --env-file .env restful-smtp-client
   ```

3. **Alternatively, use docker compose**:
   It is assumed that you can set up TLS. Change as necessary. **Unencrypted traffic can be subject to manipulation, and worse, leaks your `API_KEY`**. It is otherwise recommended that this SMTP client is not public Internet facing.
   ```yaml
   services:
    restful-smtp-client:
        image: restful-smtp-client
        container_name: restful-smtp-client
        restart: always
        ports:
          - "443:5000"
        environment:
          - SMTP_SERVER=smtp.yourprovider.com
          - SMTP_PORT=your_smtp_port
          - SMTP_USER=your_smtp_username
          - SMTP_PASSWORD=your_smtp_password
          - API_KEY=your_api_key
   ```

## API Endpoints

### `/sendmail`

- **Method**: `POST`
- **Description**: Sends the email using the specified SMTP server.
- **Request Body**:
  ```json
  {
    "api_key": "your_api_key",
    "envelope_from": "sender@example.com",
    "envelope_to": "recipient@example.com",
    "encoding": "b64",
    "raw": "<base64_encoded_raw_email_including_headers>"
  }
  ```
  ```json
  {
    "api_key": "your_api_key",
    "envelope_from": "sender@example.com",
    "envelope_to": "recipient@example.com",
    "encoding": "string",
    "raw": "<string_raw_email_including_headers>"
  }
  ```
- **Response**:

  Success `200`
  ```json
  {"success": 1}
  ```

  Failure `4xx` `5xx`
  ```json
  {"success": 0, "error": "<reason>"}
  ```

### `/sendmail_dryrun`

- **Method**: `POST`
- **Description**: Decodes and validates the email message without sending it.
- **Request Body**:
  ```json
  {
    "api_key": "your_api_key",
    "envelope_from": "sender@example.com",
    "envelope_to": "recipient@example.com",
    "encoding": "b64",
    "raw": "<base64_encoded_raw_email_including_headers>"
  }
  ```
  ```json
  {
    "api_key": "your_api_key",
    "envelope_from": "sender@example.com",
    "envelope_to": "recipient@example.com",
    "encoding": "string",
    "raw": "<string_raw_email_including_headers>"
  }
  ```
- **Response**: Returns the raw email includling headers.

### `/health`

- **Method**: `GET`
- **Description**: Checks the health status of the SMTP server.
- **Response**: Returns the health status.

  Healthy `200`
  ```json
  {"status": "healthy"}
  ```

  Failure `4xx` `5xx`
  ```json
  {"status": "unhealthy", "error": "<reason>"}
  ```

## Security

Make sure to secure your API key and SMTP credentials. It's recommended to use environment variables or a secret management system to store sensitive information.

It is also recommended that this SMTP client is not publicly accessible.

## Contributing

Feel free to open issues or submit pull requests. For major changes, please open an issue first to discuss what you would like to change.