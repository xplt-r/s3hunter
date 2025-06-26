import requests
import argparse
import threading
import time
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)  # Auto-reset colors after print

def generate_bucket_names(company, wordlist):
    buckets = set()
    for word in wordlist:
        buckets.add(f"{word}-{company}")
        buckets.add(f"{company}-{word}")
    buckets.add(company)
    return list(buckets)

def check_bucket(bucket, results, lock, progress, retries=2, timeout=5, proxy=None):
    urls = [
        f"http://{bucket}.s3.amazonaws.com",
        f"https://{bucket}.s3.amazonaws.com"
    ]
    
    for url in urls:
        attempt = 0
        while attempt <= retries:
            try:
                proxies = {"http": proxy, "https": proxy} if proxy else None
                r = requests.head(url, timeout=timeout, proxies=proxies)
                headers = r.headers
                if r.status_code < 400:
                    aws_signed = "x-amz-request-id" in headers
                    msg = f"[✅ FOUND] {url} ({r.status_code}) {'[AWS SIGNED]' if aws_signed else ''}"
                    with lock:
                        print(Fore.GREEN + msg)
                        results.append(msg)
                else:
                    with lock:
                        print(Fore.YELLOW + f"[❌ NOT FOUND] {url} ({r.status_code})")
                break
            except requests.RequestException as e:
                with lock:
                    print(Fore.RED + f"[⚠️ ERROR] {url} | {type(e).__name__}: {e}")
                attempt += 1
                if attempt <= retries:
                    time.sleep(1)
                    with lock:
                        print(Fore.CYAN + f"🔁 Retrying {url} (Attempt {attempt}/{retries})...")
                else:
                    with lock:
                        print(Fore.MAGENTA + f"⛔ Giving up on {url} after {retries} retries.")
        with lock:
            progress.update(1)

def main():
    parser = argparse.ArgumentParser(description="🔎 Advanced S3 Bucket Finder Tool (Color, Progress, Signed detection)")
    parser.add_argument("-C", "--company", required=True, help="Company name (e.g. tomorrowland)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-o", "--output", help="Save found buckets to file")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout for each request (default: 5 sec)")
    parser.add_argument("--retries", type=int, default=2, help="Retries on failure (default: 2)")
    parser.add_argument("--proxy", help="Proxy (e.g. http://127.0.0.1:8080)")

    args = parser.parse_args()

    try:
        with open(args.wordlist) as f:
            words = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(Fore.RED + f"[!] Error reading wordlist: {e}")
        return

    buckets = generate_bucket_names(args.company, words)
    results = []
    lock = threading.Lock()
    threads = []

    print(Fore.CYAN + f"\n🚀 Starting S3 bucket scan for: {args.company}")
    print(Fore.CYAN + f"🔧 Threads: {args.threads} | Timeout: {args.timeout}s | Retries: {args.retries}")
    if args.proxy:
        print(Fore.CYAN + f"🌐 Using proxy: {args.proxy}")
    print(Fore.CYAN + f"📦 Total buckets to check: {len(buckets)}\n")

    progress = tqdm(total=len(buckets)*2, desc="Scanning", unit="req")

    for bucket in buckets:
        while threading.active_count() > args.threads:
            time.sleep(0.1)
        t = threading.Thread(target=check_bucket, args=(
            bucket, results, lock, progress, args.retries, args.timeout, args.proxy))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    progress.close()

    if args.output:
        with open(args.output, "w") as f:
            for line in results:
                f.write(line + "\n")
        print(Fore.GREEN + f"\n💾 Results saved to {args.output}")

    print(Fore.GREEN + f"\n✅ Scan completed. {len(results)} accessible buckets found.")

if __name__ == "__main__":
    main()
