import requests
import argparse
import threading
import time

def generate_bucket_names(company, wordlist):
    buckets = set()
    for word in wordlist:
        buckets.add(f"{word}-{company}")
        buckets.add(f"{company}-{word}")
    buckets.add(company)  # Direct company name
    return list(buckets)

def check_bucket(bucket, results, lock, retries=2, timeout=5, proxy=None):
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
                if r.status_code < 400:
                    with lock:
                        print(f"[✅ FOUND] {url} ({r.status_code})")
                        results.append(f"{url} ({r.status_code})")
                else:
                    print(f"[❌ NOT FOUND] {url} ({r.status_code})")
                return  # Found a valid response; no more attempts
            except requests.RequestException as e:
                print(f"[⚠️ ERROR] {url} | {type(e).__name__}: {e}")
                attempt += 1
                if attempt <= retries:
                    time.sleep(1)
                    print(f"🔁 Retrying {url} (Attempt {attempt}/{retries})...")
                else:
                    print(f"⛔ Giving up on {url} after {retries} retries.")

def main():
    parser = argparse.ArgumentParser(description="🔎 S3 Bucket Finder Tool (with proxy, HTTPS, retries)")
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
        print(f"[!] Error reading wordlist: {e}")
        return

    buckets = generate_bucket_names(args.company, words)
    results = []
    lock = threading.Lock()
    threads = []

    print(f"\n🚀 Starting S3 bucket scan for: {args.company}")
    print(f"🔧 Threads: {args.threads} | Timeout: {args.timeout}s | Retries: {args.retries}")
    if args.proxy:
        print(f"🌐 Using proxy: {args.proxy}")
    print(f"📦 Total buckets to check: {len(buckets)}\n")

    for bucket in buckets:
        while threading.active_count() > args.threads:
            time.sleep(0.1)
        t = threading.Thread(target=check_bucket, args=(
            bucket, results, lock, args.retries, args.timeout, args.proxy))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    if args.output:
        with open(args.output, "w") as f:
            for line in results:
                f.write(line + "\n")
        print(f"\n💾 Results saved to {args.output}")

    print(f"\n✅ Scan completed. {len(results)} accessible buckets found.")

if __name__ == "__main__":
    main()
