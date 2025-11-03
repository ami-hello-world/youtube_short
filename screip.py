import requests
import random
import time
import os
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag 
from typing import List, Set, Optional, Dict, Any, Tuple

# --- 設定: CSSセレクタと基本設定 ---
SELECTORS = {
    "category_article": "a[itemprop='url']",
    "category_next_page": 'a[title="次のページへ"]',
    "article_title": "h1.article-title", 
    "article_post_container": "div.article-body",
    "article_post_header": "div.t_h",
}

# --- 基本設定 ---
# 修正: BASE_URL を「痛い話」カテゴリ (cat_1038009.html) に変更
BASE_URL = "http://www.2monkeys.jp/archives/cat_1038009.html"
STATE_FILE = "scraped_urls.txt"
HEADERS = {
    "User-Agent": "MyEfficientScraper/1.0 (+http://example.com/bot.html)"
}
REQUEST_DELAY_SECONDS = 1

# --- 状態管理関数 ---
def load_scraped_urls(file_path: str) -> Set[str]:
    if not os.path.exists(file_path):
        return set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except IOError as e:
        print(f"Error: 状態ファイル '{file_path}' の読み込みに失敗しました: {e}")
        return set()

def save_scraped_url(url: str, file_path: str) -> None:
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(url + '\n')
    except IOError as e:
        print(f"Error: 状態ファイル '{file_path}' への書き込みに失敗しました: {e}")

# --- クローラー関数 ---
def find_random_new_article(start_url: str, scraped_urls: Set[str]) -> Optional[str]:
    current_url = start_url
    while current_url:
        print(f"探索中: {current_url}")
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            response = requests.get(current_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error: ページ '{current_url}' の取得に失敗しました: {e}")
            return None

        soup = BeautifulSoup(response.content, 'lxml')
        
        article_links = soup.select(SELECTORS["category_article"])
        page_urls = {a['href'] for a in article_links if 'href' in a.attrs}
        
        if not page_urls and current_url == start_url:
            print(f"警告: ページ '{current_url}' で記事リンク (a[itemprop='url']) が見つかりません。")

        new_urls = list(page_urls - scraped_urls)
        
        if new_urls:
            selected_url = random.choice(new_urls)
            print(f"発見: 未取得の記事を {len(new_urls)} 件発見しました。")
            return selected_url
            
        next_page_link = soup.select_one(SELECTORS["category_next_page"])
        if next_page_link and 'href' in next_page_link.attrs:
            current_url = next_page_link['href']
        else:
            current_url = None
            
    return None

# --- データ抽出関数 ---
def scrape_conversation(article_url: str) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    print(f"\n--- 記事抽出開始 ---\nURL: {article_url}")
    try:
        time.sleep(REQUEST_DELAY_SECONDS)
        response = requests.get(article_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: 記事ページ '{article_url}' の取得に失敗しました: {e}")
        return None

    soup = BeautifulSoup(response.content, 'lxml')
    
    title_tag = soup.select_one(SELECTORS["article_title"])
    article_title = "（タイトル不明）"
    if title_tag:
        article_title = title_tag.get_text(strip=True)
    else:
        print(f"警告: 記事ページでタイトル ({SELECTORS['article_title']}) が見つかりませんでした。")
        
    container = soup.select_one(SELECTORS["article_post_container"])
    if not container:
        print(f"Error: 記事ページで会話コンテナ ({SELECTORS['article_post_container']}) が見つかりませんでした。")
        return None
        
    conversation = []
    header_tags = container.select(SELECTORS["article_post_header"])
    
    for header_tag in header_tags:
        header_text = header_tag.get_text(strip=True)
        body_tag = header_tag.find_next_sibling("div", class_="t_b")
        
        body_text = ""
        if body_tag:
            body_text = body_tag.get_text(separator="\n", strip=True)
        
        if header_text or body_text:
            conversation.append({"header": header_text, "body": body_text})

    if not conversation:
        print(f"Error: コンテナ内で投稿 ({SELECTORS['article_post_header']}) が見つかりませんでした。")

    return (article_title, conversation)

# --- メイン実行ブロック ---
def main() -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    """
    スクリプトのメイン処理。
    抽出した (タイトル, 会話データ) のタプルを返す。
    """
    print("--- スクレイピング処理を開始します ---")
    
    scraped_urls = load_scraped_urls(STATE_FILE)
    print(f"状態をロード: {len(scraped_urls)} 件の取得済みURLを認識しました。")
    
    new_article_url = find_random_new_article(BASE_URL, scraped_urls)
    
    if not new_article_url:
        print("\n--- 処理終了: 新規の未取得記事は見つかりませんでした。 ---")
        return None
        
    scrape_result = scrape_conversation(new_article_url)
    
    if scrape_result:
        article_title, conversation_data = scrape_result
        
        save_scraped_url(new_article_url, STATE_FILE)
        print(f"\n状態を更新: URL '{new_article_url}' を取得済みとして記録しました。")
        
        print("\n--- スクレイピング処理を正常に終了しました ---")
        
        return (article_title, conversation_data)
    
    print("\n--- スクレイピング処理を正常に終了しました ---")
    return None

if __name__ == "__main__":
    """
    スクリプトが直接実行された場合、main()を呼び出し、
    返された結果をコンソールに出力する。
    """
    scraped_data = main()
    
    if scraped_data:
        title, conversation = scraped_data
        
        print("\n--- 抽出結果 ---")
        print(f"■■■ タイトル: {title} ■■■\n")
        
        if not conversation:
             print("（会話データは見つかりませんでした）")
        
        for post in conversation:
            if post['header'] or post['body']:
                print(f"[{post['header']}]\n{post['body']}\n")
        print("--- 抽出完了 ---")