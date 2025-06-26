## S3 Hunter 🪣
An advanced, high-speed S3 bucket discovery tool for bug bounty hunters and cloud security researchers.
✅ Supports AWS signed detection, progress bar, color-coded output, retries, proxy, and customizable hiding of noisy status codes like 404/403.
⚡ Easily scan thousands of bucket permutations like company-admin, admin-company, etc.

## 🚀 Features
Combine prefixes + company name + suffixes dynamically

Colorful output using colorama (green = found, yellow = not found, red = error)

Detects AWS signed buckets

Supports HTTP + HTTPS check

Progress bar with tqdm

Multithreading with user-defined threads

Retries for flaky networks

Timeout & proxy support

Hide status codes (e.g. hide 404/403 from console)

## ⚙️ Installation
```
git clone https://github.com/xplt-r/s3hunter
cd s3hunter
pip3 install -r requirements.txt
```
## 📝 Usage Example
```
python3 s3finder.py -C google -w wordlist.txt -o found_buckets.txt --threads 20 --retries 3 --timeout 7 --hide-status 403,404
```
## 📌 Options
```-C, --company```Company name (required)
```-w, --wordlist```Wordlist file path (required)
```-o, --output```Save results to file
```-t, --threads```Number of threads (default: 10)
```--timeout```Request timeout in seconds (default: 5)
```--retries```Number of retries per URL (default: 2)
```--proxy```Use proxy (e.g. http://127.0.0.1:8080)
```--hide-status```Comma-separated HTTP codes to hide (e.g. 403,404)

## 🌟 Example Output
```
[✅ FOUND] https://admin-tomorrowland.s3.amazonaws.com (200) [AWS SIGNED]
[❌ NOT FOUND] http://tomorrowland-admin.s3.amazonaws.com (404)
[⚠️ ERROR] https://somebucket.s3.amazonaws.com | ConnectTimeout: HTTPSConnectionPool...
```
## 💡 Notes
The tool generates combinations like:
admin-company, company-admin, company

Use small wordlists for faster scanning; large wordlists may generate a huge number of requests!

Respect AWS rate limits; too many requests may result in blocking or throttling.

## 👑 Credits
⚡ Inspired from LazyS3 by Nahamsec, built from scratch for speed & flexibility.
Made by a bug bounty hunter, for bug bounty hunters.

## 🛠 Example Wordlist
```
admin
cdn
media
backup
assets
dev
staging
public
private
```
## 🔒 Disclaimer
This tool is for educational and authorized testing purposes only.
Do not use against systems without explicit permission.

## 📌 Future Enhancements Ideas
✅ Silent mode
✅ JSON report option
✅ Auto-resume on interruption

## 👉 Feel free to fork, modify, and contribute!
