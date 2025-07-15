import requests
import sys

def search_files(query: str, host: str = "http://localhost:8000"):
    try:
        response = requests.get(f"{host}/search", params={"q": query})
        response.raise_for_status()
        results = response.json()
        if not results:
            print("Empty")
        else:
            for result in results:
                print(f"{result['name']}...{result['url']}")
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cli.py <search_term>")
        sys.exit(1)
    search_files(sys.argv[1])