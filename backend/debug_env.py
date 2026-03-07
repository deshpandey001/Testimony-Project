from dotenv import load_dotenv
import os

# Use verbose=True to get diagnostic output from the dotenv library
# It will tell us if it found the file.
success = load_dotenv(verbose=True)

print("-" * 30)
print(f"Was the .env file found and loaded? -> {success}")

# Now, let's try to get the variable
url = os.getenv("SUPABASE_URL")

print(f"The value read for SUPABASE_URL is: -> {url}")
print("-" * 30)

if url:
    print("SUCCESS: The environment variable was read correctly!")
else:
    print("FAILURE: The environment variable was NOT read.")