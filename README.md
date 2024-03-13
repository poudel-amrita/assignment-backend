# Google OAUTH Backend

An Oauth application that uses Google authenticaiton to fetch github profile information of the User.

## Tech Stack

**Server:** FastAPI, Python , SQLAlchemy

## Run Locally

Clone the project

```bash
  git clone https://github.com/poudel-amrita/assignment-backend.git
```

Go to the project directory

```bash
  cd assignment-backend
```

Create a virtual environment

```bash
  pythhon3 -m venv venv
```

Activate virtual environment

```bash
  cd venv
  Scripts/activate
```

Install Python dependencies

```bash
  pip install -r requirments.txt
```

Set up google oauth credentials

Copy .env.example file and make .env folder and paste it

Start the backend server

```bash
  uvicorn main:app -- reload

```

Go to http://localhost:3000/ to get started!
