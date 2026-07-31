import uvicorn

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # Enables hot-reloading for development
    )
