from authentication.google_auth import authenticate

def main():
    credentials = authenticate()
    print(f"SUCCESS:\n{credentials}")

if __name__ == "__main__":
    main()
