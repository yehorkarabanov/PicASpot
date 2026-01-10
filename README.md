# PicASpot

## Run Locally

1. Clone the repository

```bash
git clone
```

2. Add MAPILLARY_API_KEY to the .env file in the root directory

```
MAPILLARY_API_KEY=your_mapillary_api_key_here
```

3. Start the backend server

```bash
docker-compose up
```

4. Install dependencies for the frontend

```bash
cd ./src/frontend
npm install
```

5. Run the script to automatically detect server IP and construct its URL.
    - !NOTE: Make sure the backend server is running before executing this step.
    - !NOTE: It works on windows, i'm not sure about other OS.

```bash
npm run predev
```

6. Start the frontend development server (Expo)

```bash
npm run dev
```
